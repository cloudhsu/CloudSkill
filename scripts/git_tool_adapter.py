"""Narrow Git and CloudBox bundle operations for the controlled CLI broker."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from import_eval_candidates import import_selected_archives, resolve_private_terms
from tool_adapter_contract import canonical_target_digest


def _git(arguments: list[str], cwd: Path, timeout: int = 90) -> str:
    result = subprocess.run(["git", *arguments], cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError("registered Git operation failed")
    return result.stdout.strip()


def _ref_fingerprint(repository: Path, remote: str) -> str:
    refs = _git(["for-each-ref", "--format=%(refname):%(objectname)", f"refs/remotes/{remote}/"], repository)
    return hashlib.sha256(refs.encode("utf-8")).hexdigest()


def _inspect(repository: Path) -> tuple[dict[str, Any], list[str]]:
    head = _git(["rev-parse", "HEAD"], repository)
    branch = _git(["branch", "--show-current"], repository)
    dirty = bool(_git(["status", "--porcelain", "--untracked-files=normal"], repository))
    remotes = sorted(item for item in _git(["remote"], repository).splitlines() if item)
    remote_names_hash = hashlib.sha256("\n".join(remotes).encode("utf-8")).hexdigest()
    return {"head": head, "branch": branch, "dirty": dirty, "remote_names_hash": remote_names_hash}, []


def _prepare(capability: str, arguments: dict[str, Any], secrets: dict[str, str]) -> tuple[str, str, dict[str, Any], list[str]]:
    if capability == "git.inspect":
        targets = {"kind": "none", "items": []}
    elif capability == "git.fetch":
        repository = Path(arguments["repository"])
        remote = arguments["remote"]
        if remote not in set(_git(["remote"], repository).splitlines()):
            raise ValueError("requested remote is not registered in repository")
        if _git(["remote", "get-url", remote], repository) != secrets["SOURCE_REMOTE_URL"]:
            raise ValueError("registered remote URL is not host-authorized")
        items = []
        for row in _git(["ls-remote", "--heads", remote], repository).splitlines():
            object_id, ref = row.split(None, 1)
            items.append({"ref": ref, "object_id": object_id})
        targets = {"kind": "git-fetch-refs", "items": sorted(items, key=lambda item: item["ref"])}
    elif capability == "git.import_bundle":
        imports = Path(arguments["inbox"]) / "imports"
        items = []
        for path in sorted(imports.glob("*.zip")) if imports.is_dir() else []:
            if path.is_symlink() or not path.is_file():
                raise ValueError("bundle target must be a direct non-symlink archive")
            items.append({
                "relative_path": f"imports/{path.name}",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": path.stat().st_size,
            })
        targets = {"kind": "eval-bundle-archives", "items": items}
    else:
        raise ValueError("unknown registered Git capability")
    targets = {**targets, "digest": canonical_target_digest(targets)}
    return "SUCCEEDED", "immutable operation targets prepared", {"operation_targets": targets}, []


def _execute(capability: str, arguments: dict[str, Any], targets: dict[str, Any], secrets: dict[str, str]) -> tuple[str, str, dict[str, Any], list[str]]:
    if capability == "git.inspect":
        output, effects = _inspect(Path(arguments["repository"]))
        return "SUCCEEDED", "repository inspected", output, effects
    if capability == "git.fetch":
        repository = Path(arguments["repository"])
        remote = arguments["remote"]
        registered = set(_git(["remote"], repository).splitlines())
        if remote not in registered:
            raise ValueError("requested remote is not registered in repository")
        if _git(["remote", "get-url", remote], repository) != secrets["SOURCE_REMOTE_URL"]:
            raise ValueError("registered remote URL is not host-authorized")
        refspecs = []
        evidence = []
        for item in targets["items"]:
            branch = item["ref"][len("refs/heads/"):]
            destination = f"refs/remotes/{remote}/{branch}"
            refspecs.append(f"+{item['object_id']}:{destination}")
        if refspecs:
            _git(["fetch", "--no-tags", remote, *refspecs], repository)
        for item in targets["items"]:
            branch = item["ref"][len("refs/heads/"):]
            destination = f"refs/remotes/{remote}/{branch}"
            observed = _git(["rev-parse", destination], repository)
            if observed != item["object_id"]:
                raise RuntimeError("prepared fetch target was not installed")
            evidence.append({"ref": item["ref"], "object_id": observed, "outcome": "INSTALLED"})
        return "SUCCEEDED", "prepared Git refs fetched", {"status": "TARGETS_INSTALLED", "target_evidence": evidence}, ["prepared remote-tracking refs installed"]
    if capability == "git.import_bundle":
        inbox = Path(arguments["inbox"])
        config_path = Path(secrets["CLOUDSKILL_CONFIG_PATH"])
        terms = resolve_private_terms(inbox, config_path)
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            totals = import_selected_archives(inbox, targets["items"], terms, bool(arguments.get("dry_run", False)))
        return "SUCCEEDED", "versioned bundle import inspected", totals, ["local Eval Inbox import queues evaluated"]
    raise ValueError("unknown registered Git capability")


def _reconcile(capability: str, arguments: dict[str, Any], targets: dict[str, Any], secrets: dict[str, str]) -> tuple[str, str, dict[str, Any], list[str]]:
    if capability == "git.fetch":
        repository = Path(arguments["repository"])
        remote = arguments["remote"]
        evidence = []
        incomplete = False
        for item in targets["items"]:
            branch = item["ref"][len("refs/heads/"):]
            destination = f"refs/remotes/{remote}/{branch}"
            try:
                observed = _git(["rev-parse", destination], repository)
            except RuntimeError:
                incomplete = True
                observed = None
            matched = observed == item["object_id"]
            incomplete = incomplete or not matched
            evidence.append({"ref": item["ref"], "object_id": item["object_id"], "observed_object_id": observed, "outcome": "MATCHED" if matched else "NOT_OBSERVED"})
        if not targets["items"]:
            rows = _git(["for-each-ref", "--format=%(refname)", f"refs/remotes/{remote}/"], repository)
            incomplete = any(row and not row.endswith("/HEAD") for row in rows.splitlines())
        state = "UNCERTAIN" if incomplete else "SUCCEEDED"
        return state, "Git fetch reconciliation completed", {"status": "OBSERVED_INCOMPLETE" if incomplete else "OBSERVED_COMPLETE", "target_evidence": evidence}, []
    if capability == "git.import_bundle":
        inbox = Path(arguments["inbox"])
        evidence = []
        state = "SUCCEEDED"
        for item in targets["items"]:
            pending = inbox / item["relative_path"]
            processed = inbox / "imports" / "processed" / pending.name
            unsupported = inbox / "imports" / "unsupported" / pending.name
            if pending.is_file():
                observed = hashlib.sha256(pending.read_bytes()).hexdigest()
                outcome = "PENDING" if observed == item["sha256"] else "IDENTITY_CONFLICT"
                state = "FAILED" if outcome == "PENDING" and state == "SUCCEEDED" else "BLOCKED"
            elif processed.is_file() and hashlib.sha256(processed.read_bytes()).hexdigest() == item["sha256"]:
                outcome = "PROCESSED"
            elif unsupported.is_file() and hashlib.sha256(unsupported.read_bytes()).hexdigest() == item["sha256"]:
                outcome = "UNSUPPORTED"
            else:
                outcome = "NOT_OBSERVED"
                if state not in {"BLOCKED", "FAILED"}:
                    state = "UNCERTAIN"
            evidence.append({"relative_path": item["relative_path"], "sha256": item["sha256"], "outcome": outcome})
        return state, "bundle import reconciliation completed", {"status": "OBSERVED_COMPLETE" if state == "SUCCEEDED" else "OBSERVED_INCOMPLETE", "target_evidence": evidence}, []
    raise ValueError("capability does not support reconciliation")


def make_result(request: dict[str, Any], state: str, summary: str, output: dict[str, Any], effects: list[str], diagnostics: list[str], latency_ms: int) -> dict[str, Any]:
    digest = hashlib.sha256(json.dumps(output, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "contract_version": "2.0",
        "adapter_id": request["adapter_id"],
        "capability_id": request["capability_id"],
        "action_id": request["action_id"],
        "state": state,
        "summary": summary,
        "output": output,
        "artifact_refs": [],
        "observed_side_effects": effects,
        "diagnostics": diagnostics,
        "output_hash": digest,
        "latency_ms": latency_ms,
        "model_calls": 0,
    }


def main() -> int:
    started = time.monotonic()
    request = json.loads(sys.stdin.read())
    try:
        operation = request.get("operation")
        if operation not in {"prepare", "execute", "reconcile"}:
            raise ValueError("unsupported adapter operation")
        if operation == "prepare":
            state, summary, output, effects = _prepare(request["capability_id"], request["arguments"], request.get("secrets", {}))
        elif operation == "reconcile":
            state, summary, output, effects = _reconcile(request["capability_id"], request["arguments"], request["operation_targets"], request.get("secrets", {}))
        else:
            state, summary, output, effects = _execute(request["capability_id"], request["arguments"], request["operation_targets"], request.get("secrets", {}))
        result = make_result(request, state, summary, output, effects, [], int((time.monotonic() - started) * 1000))
    except (KeyError, OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        state = "UNCERTAIN" if request.get("operation") == "reconcile" else "FAILED"
        summary = "reconciliation observation did not complete" if state == "UNCERTAIN" else "registered Git operation did not complete"
        result = make_result(request, state, summary, {}, [], [str(exc)], int((time.monotonic() - started) * 1000))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
