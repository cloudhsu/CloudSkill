#!/usr/bin/env python3
"""Safely reconcile a structured local plan with Vikunja.

The helper deliberately keeps the local plan authoritative and the Vikunja
project/task IDs private to a local mapping or journal file.  It is designed
for the project-management-sync Skill, not as a general-purpose Vikunja SDK.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


Json = dict
DEFAULT_TIMEOUT = 20.0
DEFAULT_PAGE_SIZE = 100
SUPPORTED_VIKUNJA_MAJOR = 2
SUPPORTED_PROVIDER_ADAPTERS = ("vikunja",)
DESCRIPTION_SECTIONS = ("標題", "問題/背景", "建議處理方式", "Acceptance Criteria", "Source")


class SyncError(Exception):
    """A user-actionable, already-redacted sync error."""

    def __init__(self, code: str, *, unknown: bool = False) -> None:
        super().__init__(code)
        self.code = code
        self.unknown = unknown


class SecretStore:
    def get(self) -> str:
        ...


class MacOSKeychainStore:
    def __init__(self, service: str, account: str) -> None:
        self.service = service
        self.account = account

    def get(self) -> str:
        if sys.platform != "darwin":
            raise SyncError("keychain_backend_unavailable")
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", self.service, "-a", self.account, "-w"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            raise SyncError("credential_missing") from None
        token = result.stdout.strip()
        if not token:
            raise SyncError("credential_missing")
        return token


class CIEnvironmentStore:
    """Read a token injected by an external CI secret manager.

    This is intentionally opt-in.  The variable name is configuration; its
    value must never be committed, echoed, or included in a plan.
    """

    def __init__(self, variable: str) -> None:
        self.variable = variable

    def get(self) -> str:
        token = os.environ.get(self.variable, "").strip()
        if not token:
            raise SyncError("credential_missing")
        return token


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    payload: Any


class VikunjaHTTP:
    def __init__(self, base_url: str, token: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        parsed = urllib.parse.urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SyncError("invalid_base_url")
        root = base_url.rstrip("/")
        if not root.endswith("/api/v1"):
            root += "/api/v1"
        self.root = root
        self.token = token
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        payload: Json | None = None,
    ) -> HttpResponse:
        url = f"{self.root}/{path.lstrip('/')}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                **({"Content-Type": "application/json"} if body is not None else {}),
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                headers = {key.lower(): value for key, value in response.headers.items()}
                return HttpResponse(response.status, headers, self._decode(raw))
        except urllib.error.HTTPError as exc:
            # Do not serialize the response body: Vikunja error payloads can
            # contain request details and are not part of the sync contract.
            raise SyncError(f"http_{exc.code}") from None
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            raise SyncError("transport_unknown", unknown=True) from None

    @staticmethod
    def _decode(raw: bytes) -> Any:
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None


@dataclass(frozen=True)
class Capabilities:
    version: str
    api_family: str
    project_create_method: str | None
    task_create_method: str | None
    task_update_method: str | None
    discovery_complete: bool
    read_only_reason: str | None = None

    @property
    def writable(self) -> bool:
        return bool(self.project_create_method and self.task_create_method)

    @property
    def task_update_writable(self) -> bool:
        return bool(self.task_update_method)


class ProviderAdapter:
    """Provider-neutral surface used by the reconciliation core.

    OpenProject and Redmine adapters can implement this same surface later;
    provider/version branches must stay inside their adapters.
    """

    capabilities: Capabilities

    def discover(self) -> Capabilities:
        ...

    def list_projects(self) -> list[Json]:
        ...

    def list_tasks(self, project_id: int) -> list[Json]:
        ...

    def read_project(self, project_id: int) -> Json:
        ...

    def read_task(self, task_id: int) -> Json:
        ...

    def create_project(self, payload: Json) -> Json:
        ...

    def create_task(self, project_id: int, payload: Json) -> Json:
        ...

    def update_task(self, task_id: int, payload: Json) -> Json:
        ...


class VikunjaAdapter:
    """Vikunja v2 adapter using the advertised current API route."""

    def __init__(self, http: VikunjaHTTP) -> None:
        self.http = http
        self.capabilities: Capabilities | None = None

    def discover(self) -> Capabilities:
        # `/info` is both the non-mutating service preflight and the version
        # discovery endpoint.  No project/task enumeration or write is
        # attempted until this succeeds.
        try:
            info = self.http.request("GET", "info").payload
        except SyncError as exc:
            if exc.unknown:
                raise SyncError("service_unavailable", unknown=True) from None
            if exc.code in {"http_404", "http_405"}:
                raise SyncError("service_not_found") from None
            raise
        version = str(info.get("version", "")) if isinstance(info, dict) else ""
        match = re.match(r"^v?(\d+)(?:\.(\d+))?", version, re.IGNORECASE)
        major = int(match.group(1)) if match else None
        if major != SUPPORTED_VIKUNJA_MAJOR:
            self.capabilities = Capabilities(
                version or "unknown",
                "vikunja-unknown",
                None,
                None,
                None,
                False,
                "unsupported_version",
            )
            return self.capabilities

        project_allow = self._allow("projects")
        task_allow = self._allow("projects/0/tasks")
        task_update_allow = self._allow("tasks/0")
        project_method = self._select_create_method(project_allow)
        task_method = self._select_create_method(task_allow)
        task_update_method = self._select_update_method(task_update_allow)
        self.capabilities = Capabilities(
            version,
            "vikunja-v2-api-v1-route",
            project_method,
            task_method,
            task_update_method,
            True,
            None,
        )
        return self.capabilities

    def _allow(self, path: str) -> set[str] | None:
        try:
            response = self.http.request("OPTIONS", path)
        except SyncError:
            return None
        values = response.headers.get("allow", "")
        return {item.strip().upper() for item in values.split(",") if item.strip()}

    @staticmethod
    def _select_create_method(allowed: set[str] | None) -> str | None:
        if not allowed:
            return None
        # Current Vikunja uses PUT for collection creation.  POST remains a
        # capability-driven compatibility fallback, never a hard-coded guess.
        for method in ("PUT", "POST"):
            if method in allowed:
                return method
        return None

    @staticmethod
    def _select_update_method(allowed: set[str] | None) -> str | None:
        if not allowed:
            return None
        for method in ("POST", "PATCH", "PUT"):
            if method in allowed:
                return method
        return None

    @staticmethod
    def _items(payload: Any, key: str) -> list[Json]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for candidate in (key, "items", "data"):
                value = payload.get(candidate)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        raise SyncError("invalid_list_response")

    def _list_all(self, path: str, key: str) -> list[Json]:
        result: list[Json] = []
        seen: set[str] = set()
        for page in range(1, 101):
            response = self.http.request(
                "GET", path, query={"page": page, "per_page": DEFAULT_PAGE_SIZE}
            )
            page_items = self._items(response.payload, key)
            added = 0
            for item in page_items:
                identity = str(item.get("id", "")) or json.dumps(item, sort_keys=True)
                if identity not in seen:
                    seen.add(identity)
                    result.append(item)
                    added += 1
            if len(page_items) < DEFAULT_PAGE_SIZE or not added:
                break
        else:
            raise SyncError("pagination_limit")
        return sorted(result, key=lambda item: (str(item.get("title", "")), int(item.get("id", 0) or 0)))

    def list_projects(self) -> list[Json]:
        return self._list_all("projects", "projects")

    def list_tasks(self, project_id: int) -> list[Json]:
        return self._list_all(f"projects/{project_id}/tasks", "tasks")

    def read_project(self, project_id: int) -> Json:
        payload = self.http.request("GET", f"projects/{project_id}").payload
        if not isinstance(payload, dict):
            raise SyncError("invalid_project_readback")
        return payload

    def read_task(self, task_id: int) -> Json:
        payload = self.http.request("GET", f"tasks/{task_id}").payload
        if not isinstance(payload, dict):
            raise SyncError("invalid_task_readback")
        return payload

    def create_project(self, payload: Json) -> Json:
        if not self.capabilities or not self.capabilities.project_create_method:
            raise SyncError("project_create_not_allowed")
        response = self.http.request(self.capabilities.project_create_method, "projects", payload=payload)
        if not isinstance(response.payload, dict) or not response.payload.get("id"):
            raise SyncError("invalid_project_create_response")
        return response.payload

    def create_task(self, project_id: int, payload: Json) -> Json:
        if not self.capabilities or not self.capabilities.task_create_method:
            raise SyncError("task_create_not_allowed")
        response = self.http.request(
            self.capabilities.task_create_method,
            f"projects/{project_id}/tasks",
            payload=payload,
        )
        if not isinstance(response.payload, dict) or not response.payload.get("id"):
            raise SyncError("invalid_task_create_response")
        return response.payload

    def update_task(self, task_id: int, payload: Json) -> Json:
        if not self.capabilities or not self.capabilities.task_update_method:
            raise SyncError("task_update_not_allowed")
        response = self.http.request(
            self.capabilities.task_update_method,
            f"tasks/{task_id}",
            payload=payload,
        )
        if not isinstance(response.payload, dict) or response.payload.get("id") != task_id:
            raise SyncError("invalid_task_update_response")
        return response.payload


class FakeAdapter:
    """Small in-process adapter used by deterministic tests."""

    def __init__(self, projects: list[Json] | None = None, tasks: dict[int, list[Json]] | None = None) -> None:
        self.projects = projects or []
        self.tasks = tasks or {}
        self.capabilities = Capabilities("2.5.0", "fake", "PUT", "PUT", "POST", True)
        self._next_id = 9000

    def discover(self) -> Capabilities:
        return self.capabilities

    def list_projects(self) -> list[Json]:
        return list(self.projects)

    def list_tasks(self, project_id: int) -> list[Json]:
        return list(self.tasks.get(project_id, []))

    def read_project(self, project_id: int) -> Json:
        return next(project for project in self.projects if project["id"] == project_id)

    def read_task(self, task_id: int) -> Json:
        return next(
            task for project_tasks in self.tasks.values() for task in project_tasks if task["id"] == task_id
        )

    def create_project(self, payload: Json) -> Json:
        self._next_id += 1
        project = {"id": self._next_id, **payload}
        self.projects.append(project)
        self.tasks[project["id"]] = []
        return project

    def create_task(self, project_id: int, payload: Json) -> Json:
        self._next_id += 1
        task = {"id": self._next_id, "project_id": project_id, **payload}
        self.tasks.setdefault(project_id, []).append(task)
        return task

    def update_task(self, task_id: int, payload: Json) -> Json:
        task = self.read_task(task_id)
        task.update(payload)
        task["updated"] = "2026-08-29T00:00:00Z"
        if payload.get("done"):
            task["done_at"] = "2026-08-29T00:00:00Z"
        elif payload.get("done") is False:
            task["done_at"] = None
        return task


def make_adapter(provider: str, http: VikunjaHTTP) -> ProviderAdapter:
    """Select a provider adapter before any provider-specific operation."""
    if provider == "vikunja":
        return VikunjaAdapter(http)
    # Fail closed until an OpenProject or Redmine adapter has its own
    # discovery, capability, pagination, mutation, and readback tests.
    raise SyncError("provider_adapter_not_implemented")


def _require_string(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing_{field}")


def validate_plan(plan: Any) -> Json:
    if not isinstance(plan, dict):
        raise SyncError("invalid_plan")
    errors: list[str] = []
    for field in ("source_system", "target_provider", "target_profile", "agent"):
        _require_string(plan.get(field), field, errors)
    if plan.get("target_provider") not in SUPPORTED_PROVIDER_ADAPTERS:
        errors.append("unsupported_target_provider")
    source_owned_fields = plan.get("source_owned_fields", [])
    if not isinstance(source_owned_fields, list) or any(field != "status" for field in source_owned_fields):
        errors.append("invalid_source_owned_fields")
    project = plan.get("project")
    if not isinstance(project, dict):
        errors.append("missing_project")
    else:
        _require_string(project.get("title"), "project_title", errors)
        _require_string(project.get("description"), "project_description", errors)
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        errors.append("missing_tasks")
        tasks = []
    source_keys: set[str] = set()
    titles: set[str] = set()
    for index, task in enumerate(tasks):
        prefix = f"task_{index}"
        if not isinstance(task, dict):
            errors.append(f"{prefix}_invalid")
            continue
        for field in ("source_key", "title", "problem_background", "approach", "source"):
            _require_string(task.get(field), f"{prefix}_{field}", errors)
        if task.get("status", "planned") not in {"planned", "completed"}:
            errors.append(f"{prefix}_status")
        criteria = task.get("acceptance_criteria")
        if not isinstance(criteria, list) or not criteria or not all(
            isinstance(item, str) and item.strip() for item in criteria
        ):
            errors.append(f"{prefix}_acceptance_criteria")
        source_key = task.get("source_key")
        title = task.get("title")
        if isinstance(source_key, str) and source_key in source_keys:
            errors.append(f"duplicate_source_key_{source_key}")
        if isinstance(title, str) and title in titles:
            errors.append(f"duplicate_title_{title}")
        if isinstance(source_key, str):
            source_keys.add(source_key)
        if isinstance(title, str):
            titles.add(title)
    if errors:
        raise SyncError("invalid_plan:" + ",".join(errors))
    return plan


def render_description(task: Json, agent: str, today: str) -> str:
    criteria = "\n".join(f"- {item}" for item in task["acceptance_criteria"])
    progress = task.get("progress") or [{"date": today, "status": task.get("status", "planned")}]
    lines = [
        "標題",
        f"- {task['source_key']}: {task['title']}",
        "",
        "問題/背景",
        task["problem_background"].strip(),
        "",
        "建議處理方式",
        task["approach"].strip(),
        "",
        "Acceptance Criteria",
        criteria,
        "",
        "Source",
        f"- {task['source'].strip()}",
    ]
    for entry in progress:
        if not isinstance(entry, dict) or not entry.get("date") or not entry.get("status"):
            raise SyncError("invalid_progress_block")
        lines.extend(
            [
                "",
                f"### Progress {entry['date']}",
                f"- Agent: {agent}",
                f"- Status: {entry['status']}",
            ]
        )
        if entry.get("evidence"):
            lines.append(f"- Evidence: {entry['evidence']}")
        if entry.get("next_action"):
            lines.append(f"- Next action: {entry['next_action']}")
    description = "\n".join(lines).strip() + "\n"
    for section in DESCRIPTION_SECTIONS:
        if section not in description:
            raise SyncError("description_format_incomplete")
    if f"- Agent: {agent}" not in description:
        raise SyncError("agent_missing_from_description")
    return description


def _title_matches(items: list[Json], title: str) -> list[Json]:
    return [item for item in items if str(item.get("title", "")) == title]


def _counts(operations: list[Json]) -> dict[str, int]:
    counts = {name: 0 for name in ("no-op", "create", "update", "ambiguous", "blocked")}
    for operation in operations:
        action = operation.get("action", "blocked")
        counts[action] = counts.get(action, 0) + 1
    return counts


def _base_report(mode: str, capabilities: Capabilities, project_title: str) -> Json:
    return {
        "status": "PASS",
        "mode": mode,
        "provider": "vikunja",
        "api_family": capabilities.api_family,
        "server_version": capabilities.version,
        "service_probe": "PASS: provider info endpoint reached before enumeration",
        "secret_store": "configured SecretStore (value redacted)",
        "project": project_title,
        "planned": {name: 0 for name in ("no-op", "create", "update", "ambiguous", "blocked")},
        "executed": {name: 0 for name in ("no-op", "create", "update", "ambiguous", "blocked")},
        "operations": [],
        "post_write_readback": "not_applicable",
        "reconciliation": "not_required",
        "privacy_audit": "PASS: no credential or raw provider response emitted",
    }


def _operation(kind: str, action: str, title: str, *, source_key: str = "", reason: str = "") -> Json:
    result = {"kind": kind, "action": action, "title": title}
    if source_key:
        result["source_key"] = source_key
    if reason:
        result["reason"] = reason
    return result


def _project_state(projects: list[Json], title: str) -> tuple[str, Json | None, str]:
    matches = _title_matches(projects, title)
    if len(matches) == 1:
        return "no-op", matches[0], "exact_title_match"
    if len(matches) > 1:
        return "ambiguous", None, "multiple_exact_title_matches"
    return "create", None, "no_exact_title_match"


def plan_remote(adapter: Any, plan: Json, mode: str, today: str) -> tuple[Json, int | None, list[Json]]:
    capabilities = adapter.discover()
    report = _base_report(mode, capabilities, plan["project"]["title"])
    if capabilities.read_only_reason:
        report["status"] = "BLOCKED" if mode == "apply" else "PASS"
        report["reconciliation"] = capabilities.read_only_reason
    projects = adapter.list_projects()
    project_action, project, project_reason = _project_state(projects, plan["project"]["title"])
    operations: list[Json] = [
        _operation("project", project_action, plan["project"]["title"], reason=project_reason)
    ]
    project_id = int(project["id"]) if project and project.get("id") is not None else None
    if project_action == "ambiguous":
        for task in plan["tasks"]:
            operations.append(
                _operation(
                    "task",
                    "blocked",
                    task["title"],
                    source_key=task["source_key"],
                    reason="project_identity_ambiguous",
                )
            )
    elif project_id is not None:
        tasks = adapter.list_tasks(project_id)
        for task in plan["tasks"]:
            matches = _title_matches(tasks, task["title"])
            if len(matches) == 1:
                if "status" in plan.get("source_owned_fields", []):
                    completion_requested = task.get("status", "planned") == "completed"
                    if completion_requested and matches[0].get("done") is not True:
                        if capabilities.task_update_writable:
                            action, reason = "update", "source_owned_status_differs"
                        else:
                            action, reason = "blocked", "task_update_capability_missing"
                    elif not completion_requested:
                        action, reason = "no-op", "no_completion_requested"
                    else:
                        action, reason = "no-op", "source_owned_status_matches"
                else:
                    action, reason = "no-op", "exact_title_match"
            elif len(matches) > 1:
                action, reason = "ambiguous", "multiple_exact_title_matches"
            elif mode == "audit":
                action, reason = "create", "missing_remote_task_audit_only"
            elif capabilities.writable:
                action, reason = "create", "no_exact_title_match"
            else:
                action, reason = "blocked", "required_capability_missing"
            operations.append(_operation("task", action, task["title"], source_key=task["source_key"], reason=reason))
    else:
        for task in plan["tasks"]:
            action = "create" if mode in {"audit", "dry-run"} or capabilities.writable else "blocked"
            operations.append(
                _operation(
                    "task",
                    action,
                    task["title"],
                    source_key=task["source_key"],
                    reason="project_will_be_created" if action == "create" else "required_capability_missing",
                )
            )
    report["operations"] = operations
    report["planned"] = _counts(operations)
    if any(operation["action"] in {"ambiguous", "blocked"} for operation in operations):
        report["status"] = "BLOCKED" if mode == "apply" else report["status"]
    return report, project_id, operations


def _journal_load(path: Path) -> Json:
    if not path.exists():
        return {"schema_version": 1, "operations": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise SyncError("invalid_journal") from None
    if not isinstance(value, dict) or not isinstance(value.get("operations", []), list):
        raise SyncError("invalid_journal")
    return value


def _journal_save(path: Path, journal: Json) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(journal, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _journal_record(journal: Json, operation_id: str, **fields: Any) -> Json:
    for entry in journal["operations"]:
        if entry.get("operation_id") == operation_id:
            entry.update(fields)
            return entry
    entry = {"operation_id": operation_id, **fields}
    journal["operations"].append(entry)
    return entry


def apply_plan(
    adapter: Any,
    plan: Json,
    report: Json,
    project_id: int | None,
    operations: list[Json],
    journal_path: Path,
    mapping_path: Path | None,
    today: str,
) -> Json:
    journal = _journal_load(journal_path)
    project = plan["project"]
    project_operation = operations[0]
    if project_operation["action"] == "ambiguous":
        report["status"] = "BLOCKED"
        return report
    if project_id is None:
        if project_operation["action"] != "create":
            report["status"] = "BLOCKED"
            return report
        operation_id = "project:" + project["title"]
        _journal_record(journal, operation_id, kind="project", title=project["title"], status="requested")
        _journal_save(journal_path, journal)
        try:
            created = adapter.create_project({"title": project["title"], "description": project["description"]})
            project_id = int(created["id"])
            readback = adapter.read_project(project_id)
            if readback.get("title") != project["title"]:
                raise SyncError("project_readback_mismatch", unknown=True)
        except SyncError as exc:
            unknown = exc.unknown or exc.code.startswith("invalid_") or exc.code.endswith("_readback_mismatch")
            _journal_record(journal, operation_id, status="unknown" if unknown else "blocked", error=exc.code)
            _journal_save(journal_path, journal)
            report["status"] = "BLOCKED" if not unknown else "UNKNOWN"
            report["reconciliation"] = "run_reconcile_before_retry" if unknown else exc.code
            report["executed"]["blocked"] += 1
            return report
        _journal_record(journal, operation_id, status="verified", remote_id=project_id)
        _journal_save(journal_path, journal)
        report["executed"]["create"] += 1

    tasks = adapter.list_tasks(project_id)
    # Recompute from the post-project-create inventory; this closes the race
    # between dry planning and applying and prevents a second create.
    for task in plan["tasks"]:
        matches = _title_matches(tasks, task["title"])
        operation_id = f"task:{task['source_key']}"
        if len(matches) == 1:
            existing_entry = next(
                (entry for entry in journal["operations"] if entry.get("operation_id") == operation_id),
                None,
            )
            if existing_entry and existing_entry.get("status") == "unknown":
                report["executed"]["blocked"] += 1
                report["status"] = "UNKNOWN"
                report["reconciliation"] = "run_reconcile_before_retry"
                continue
            operation = next(
                item for item in operations
                if item.get("kind") == "task" and item.get("source_key") == task["source_key"]
            )
            if operation["action"] == "no-op":
                report["executed"]["no-op"] += 1
                continue
            if operation["action"] != "update":
                report["executed"]["blocked"] += 1
                report["status"] = "BLOCKED"
                continue
            remote = matches[0]
            task_id = int(remote["id"])
            desired_done = True
            before_updated = remote.get("updated")
            _journal_record(
                journal,
                operation_id,
                kind="task",
                source_key=task["source_key"],
                title=task["title"],
                target_project_id=project_id,
                remote_id=task_id,
                status="requested",
                operation="update_status",
                desired_done=desired_done,
                before_updated=before_updated,
            )
            _journal_save(journal_path, journal)
            try:
                adapter.update_task(task_id, {"done": desired_done})
                readback = adapter.read_task(task_id)
                completion_valid = bool(readback.get("done_at"))
                readback_updated = readback.get("updated")
                updated_changed = bool(readback_updated) and (
                    not before_updated or readback_updated != before_updated
                )
                if (
                    readback.get("id") != task_id
                    or readback.get("done") is not desired_done
                    or not completion_valid
                    or not updated_changed
                ):
                    raise SyncError("task_update_readback_mismatch", unknown=True)
            except SyncError as exc:
                unknown = exc.unknown or exc.code.startswith("invalid_") or exc.code.endswith("_readback_mismatch")
                _journal_record(journal, operation_id, status="unknown" if unknown else "blocked", error=exc.code)
                _journal_save(journal_path, journal)
                report["executed"]["blocked"] += 1
                report["status"] = "UNKNOWN" if unknown else "BLOCKED"
                report["reconciliation"] = "run_reconcile_before_retry" if unknown else exc.code
                continue
            _journal_record(
                journal,
                operation_id,
                status="verified",
                remote_id=task_id,
                completion_timestamp_source="provider",
            )
            _journal_save(journal_path, journal)
            report["executed"]["update"] += 1
            continue
        if len(matches) > 1:
            report["executed"]["ambiguous"] += 1
            report["status"] = "BLOCKED"
            continue
        if not adapter.capabilities.writable:
            report["executed"]["blocked"] += 1
            report["status"] = "BLOCKED"
            continue
        payload = {
            "title": task["title"],
            "description": render_description(task, plan["agent"], today),
        }
        _journal_record(
            journal,
            operation_id,
            kind="task",
            source_key=task["source_key"],
            title=task["title"],
            target_project_id=project_id,
            status="requested",
        )
        _journal_save(journal_path, journal)
        try:
            created = adapter.create_task(project_id, payload)
            task_id = int(created["id"])
            readback = adapter.read_task(task_id)
            if readback.get("title") != task["title"] or f"- Agent: {plan['agent']}" not in str(
                readback.get("description", "")
            ):
                raise SyncError("task_readback_mismatch", unknown=True)
        except SyncError as exc:
            unknown = exc.unknown or exc.code.startswith("invalid_") or exc.code.endswith("_readback_mismatch")
            _journal_record(journal, operation_id, status="unknown" if unknown else "blocked", error=exc.code)
            _journal_save(journal_path, journal)
            report["executed"]["blocked"] += 1
            report["status"] = "UNKNOWN" if unknown else "BLOCKED"
            report["reconciliation"] = "run_reconcile_before_retry" if unknown else exc.code
            continue
        _journal_record(journal, operation_id, status="verified", remote_id=task_id)
        _journal_save(journal_path, journal)
        report["executed"]["create"] += 1
        if mapping_path is not None:
            mapping = _journal_load(mapping_path)
            mapping.setdefault("records", {})[task["source_key"]] = {
                "target_project_id": project_id,
                "target_record_id": task_id,
            }
            _journal_save(mapping_path, mapping)
        tasks.append({"id": task_id, **payload})
    report["post_write_readback"] = (
        "PASS" if report["executed"]["create"] or report["executed"]["update"] else "not_applicable"
    )
    if report["status"] != "UNKNOWN" and (
        report["executed"]["ambiguous"] or report["executed"]["blocked"]
    ):
        report["status"] = "BLOCKED"
    return report


def reconcile_unknowns(adapter: Any, journal_path: Path) -> Json:
    journal = _journal_load(journal_path)
    unknowns = [entry for entry in journal["operations"] if entry.get("status") == "unknown"]
    report: Json = {
        "status": "PASS",
        "mode": "reconcile",
        "provider": "vikunja",
        "unknown_operations": len(unknowns),
        "reconciled": 0,
        "safe_to_retry": 0,
        "blocked": 0,
        "privacy_audit": "PASS: no credential or raw provider response emitted",
    }
    projects: list[Json] | None = None
    for entry in unknowns:
        if entry.get("kind") == "project":
            if projects is None:
                projects = adapter.list_projects()
            matches = _title_matches(projects, str(entry.get("title", "")))
        elif entry.get("operation") == "update_status":
            remote_id = entry.get("remote_id")
            if isinstance(remote_id, bool) or not isinstance(remote_id, int) or remote_id <= 0:
                report["blocked"] += 1
                continue
            try:
                remote = adapter.read_task(int(remote_id))
            except SyncError:
                report["blocked"] += 1
                continue
            desired_done = entry.get("desired_done")
            completion_valid = bool(remote.get("done_at"))
            updated = remote.get("updated")
            before_updated = entry.get("before_updated")
            committed = (
                desired_done is True
                and remote.get("id") == int(remote_id)
                and remote.get("done") is desired_done
                and completion_valid
                and bool(updated)
                and (not before_updated or updated != before_updated)
            )
            if committed:
                entry["status"] = "reconciled"
                report["reconciled"] += 1
            else:
                entry["status"] = "safe_to_retry_after_review"
                report["safe_to_retry"] += 1
            continue
        else:
            project_id = entry.get("target_project_id")
            if not project_id:
                report["blocked"] += 1
                continue
            matches = _title_matches(adapter.list_tasks(int(project_id)), str(entry.get("title", "")))
        if len(matches) == 1:
            entry["status"] = "reconciled"
            entry["remote_id"] = matches[0].get("id")
            report["reconciled"] += 1
        elif len(matches) == 0:
            entry["status"] = "safe_to_retry_after_review"
            report["safe_to_retry"] += 1
        else:
            entry["status"] = "blocked_ambiguous"
            report["blocked"] += 1
    if report["blocked"]:
        report["status"] = "BLOCKED"
    _journal_save(journal_path, journal)
    return report


def load_plan(path: Path) -> Json:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise SyncError("invalid_plan_file") from None
    return validate_plan(value)


def make_store(args: argparse.Namespace) -> SecretStore:
    if args.credential_source == "keychain":
        return MacOSKeychainStore(args.keychain_service, args.keychain_account)
    return CIEnvironmentStore(args.credential_env)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="structured local plan JSON")
    parser.add_argument("--mode", choices=("audit", "dry-run", "apply", "reconcile"), default="dry-run")
    parser.add_argument("--base-url", default=os.environ.get("VIKUNJA_BASE_URL"), help="Vikunja web/API base URL")
    parser.add_argument("--credential-source", choices=("keychain", "ci-env"), default="keychain")
    parser.add_argument("--keychain-service", default="cloudbox-vikunja")
    parser.add_argument("--keychain-account", default=os.environ.get("VIKUNJA_KEYCHAIN_ACCOUNT", ""))
    parser.add_argument("--credential-env", default="VIKUNJA_TOKEN")
    parser.add_argument("--journal-file", type=Path, default=Path(".local/vikunja-sync-journal.json"))
    parser.add_argument("--mapping-file", type=Path)
    parser.add_argument("--today", default=date.today().isoformat(), help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plan = load_plan(args.plan)
        if args.mode == "reconcile":
            if not args.base_url:
                raise SyncError("base_url_required")
            token = make_store(args).get()
            adapter = make_adapter(plan["target_provider"], VikunjaHTTP(args.base_url, token))
            report = reconcile_unknowns(adapter, args.journal_file)
        else:
            if not args.base_url:
                raise SyncError("base_url_required")
            if not args.keychain_account and args.credential_source == "keychain":
                raise SyncError("keychain_account_required")
            token = make_store(args).get()
            adapter = make_adapter(plan["target_provider"], VikunjaHTTP(args.base_url, token))
            report, project_id, operations = plan_remote(adapter, plan, args.mode, args.today)
            if args.mode == "apply" and report["status"] != "BLOCKED":
                report = apply_plan(
                    adapter,
                    plan,
                    report,
                    project_id,
                    operations,
                    args.journal_file,
                    args.mapping_file,
                    args.today,
                )
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report.get("status") == "PASS" else 2
    except SyncError as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "error": exc.code,
                    "reconciliation": "run_reconcile_before_retry" if exc.unknown else "manual_review_required",
                    "privacy_audit": "PASS: no credential or raw provider response emitted",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
