"""Controlled local-CLI broker for registered CloudBox tool capabilities."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tool_action_store import load_action, reserve_idempotency, save_action_atomic, transition_action
from tool_adapter_contract import get_adapter, get_capability, validate_invocation, validate_registry, validate_result


@dataclass(frozen=True)
class ExecutionContext:
    root_refs: dict[str, Path]
    secret_values: dict[str, str]
    approved_authority: set[str]
    repository_root: Path
    owner_id: str | None = None
    fencing_token: int | None = None
    now_epoch: int | None = None


@dataclass(frozen=True)
class PreparedInvocation:
    invocation: dict[str, Any]
    adapter: dict[str, Any]
    capability: dict[str, Any]
    argv: list[str]
    cwd: Path
    environment: dict[str, str]
    request: dict[str, Any]
    action: dict[str, Any]


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _redact(value: Any, secrets: list[str]) -> Any:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[REDACTED]")
        return redacted
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: _redact(item, secrets) for key, item in value.items()}
    return value


def prepare_invocation(invocation: dict[str, Any], registry: dict[str, Any], context: ExecutionContext, *, _allow_expired: bool = False) -> PreparedInvocation:
    registry_errors = validate_registry(registry)
    if registry_errors:
        raise ValueError("invalid adapter registry: " + "; ".join(registry_errors))
    errors = validate_invocation(invocation, registry)
    if errors:
        raise ValueError("invalid tool invocation: " + "; ".join(errors))
    adapter = get_adapter(registry, invocation["adapter_id"])
    capability = get_capability(registry, invocation["adapter_id"], invocation["capability_id"])
    required_authority = set(capability["required_authority"])
    if not required_authority <= context.approved_authority:
        raise ValueError("tool invocation exceeds approved authority")
    now_epoch = context.now_epoch if context.now_epoch is not None else int(time.time())
    try:
        deadline = datetime.fromisoformat(invocation["deadline"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("invocation deadline is not a valid timestamp") from exc
    if deadline.tzinfo is None or (deadline.astimezone(timezone.utc).timestamp() <= now_epoch and not _allow_expired):
        raise ValueError("invocation deadline has expired")
    mutating = capability["risk"] != "read-only"
    if mutating and (not context.owner_id or not isinstance(context.fencing_token, int) or context.fencing_token < 1):
        raise ValueError("mutating invocation requires broker owner and fencing token")

    roots: list[Path] = []
    for reference in capability["allowed_root_refs"]:
        root = context.root_refs.get(reference)
        if root is None:
            raise ValueError(f"required root reference is unavailable: {reference}")
        roots.append(root.resolve())
    resolved_arguments = json.loads(json.dumps(invocation["arguments"]))
    for key in ("repository", "inbox"):
        relative = resolved_arguments.get(key)
        if relative is None:
            continue
        candidate = (roots[0] / relative).resolve()
        if not _within(candidate, roots[0]):
            raise ValueError(f"{key} path escapes declared root")
        resolved_arguments[key] = str(candidate)

    secrets: dict[str, str] = {}
    for reference in capability["secret_refs"]:
        value = context.secret_values.get(reference)
        if not value:
            raise ValueError(f"required secret reference is unavailable: {reference}")
        secrets[reference] = value

    provenance = adapter["provenance"]
    adapter_path = (context.repository_root / provenance["path"]).resolve()
    repository_root = context.repository_root.resolve()
    if not _within(adapter_path, repository_root) or not adapter_path.is_file():
        raise ValueError("registered adapter path is unavailable or escapes repository")
    observed_digest = hashlib.sha256(adapter_path.read_bytes()).hexdigest()
    if observed_digest != provenance["sha256"]:
        raise ValueError("registered adapter executable provenance drift")

    request = {
        "operation": "execute",
        "contract_version": invocation["contract_version"],
        "adapter_id": invocation["adapter_id"],
        "capability_id": invocation["capability_id"],
        "action_id": invocation["action_id"],
        "idempotency_key": invocation["idempotency_key"],
        "arguments": resolved_arguments,
        "secrets": secrets,
    }
    secret_fingerprints = {name: hashlib.sha256(value.encode("utf-8")).hexdigest() for name, value in secrets.items()}
    input_hash = hashlib.sha256(json.dumps({**request, "secrets": secret_fingerprints}, sort_keys=True).encode("utf-8")).hexdigest()
    action = {
        "schema_version": 1,
        "revision": 0,
        "action_id": invocation["action_id"],
        "idempotency_key": invocation["idempotency_key"],
        "plan_id": invocation["plan_id"],
        "plan_revision": invocation["plan_revision"],
        "adapter_id": invocation["adapter_id"],
        "adapter_version": adapter["adapter_version"],
        "capability_id": invocation["capability_id"],
        "state": "PLANNED",
        "attempt": 0,
        "max_attempts": capability["max_attempts"],
        "input_hash": input_hash,
        "authority_grant_id": invocation["authority_grant_id"],
        "evidence": [],
        "lease": ({"owner_id": context.owner_id, "fencing_token": context.fencing_token, "expires_at": now_epoch + capability["timeout_seconds"] + 30} if mutating else None),
    }
    environment = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
    return PreparedInvocation(invocation, adapter, capability, [sys.executable, str(adapter_path)], repository_root, environment, request, action)


def prepare_reconciliation(invocation: dict[str, Any], registry: dict[str, Any], context: ExecutionContext) -> PreparedInvocation:
    """Reconstruct the original action identity after its execution deadline."""
    prepared = prepare_invocation(invocation, registry, context, _allow_expired=True)
    return replace(prepared, request={**prepared.request, "operation": "reconcile"})


def _uncertain_result(prepared: PreparedInvocation, reason: str, latency_ms: int) -> dict[str, Any]:
    output: dict[str, Any] = {}
    digest = hashlib.sha256(json.dumps(output, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "contract_version": "1.0",
        "adapter_id": prepared.invocation["adapter_id"],
        "capability_id": prepared.invocation["capability_id"],
        "action_id": prepared.invocation["action_id"],
        "state": "UNCERTAIN",
        "summary": "adapter completion is uncertain",
        "output": output,
        "artifact_refs": [],
        "observed_side_effects": [],
        "diagnostics": [reason],
        "output_hash": digest,
        "latency_ms": latency_ms,
        "model_calls": 0,
    }


def _blocked_result(prepared: PreparedInvocation, reason: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    return {
        "contract_version": "1.0",
        "adapter_id": prepared.invocation["adapter_id"],
        "capability_id": prepared.invocation["capability_id"],
        "action_id": prepared.invocation["action_id"],
        "state": "BLOCKED",
        "summary": "durable action requires lifecycle-owner recovery",
        "output": output,
        "artifact_refs": [],
        "observed_side_effects": [],
        "diagnostics": [reason],
        "output_hash": hashlib.sha256(json.dumps(output, sort_keys=True).encode("utf-8")).hexdigest(),
        "latency_ms": 0,
        "model_calls": 0,
    }


def _invoke_adapter(prepared: PreparedInvocation, operation: str) -> dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(
        prepared.argv,
        cwd=prepared.cwd,
        env=prepared.environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    request = {**prepared.request, "operation": operation}
    try:
        stdout, stderr = process.communicate(json.dumps(request, sort_keys=True), timeout=prepared.capability["timeout_seconds"])
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return _uncertain_result(prepared, f"adapter {operation} timeout; reconciliation remains required", int((time.monotonic() - started) * 1000))
    latency = int((time.monotonic() - started) * 1000)
    maximum = prepared.capability["max_output_bytes"]
    if len(stdout.encode("utf-8")) > maximum or len(stderr.encode("utf-8")) > maximum:
        return _uncertain_result(prepared, f"adapter {operation} output exceeded declared bound", latency)
    if process.returncode != 0:
        return _uncertain_result(prepared, f"adapter {operation} process failed", latency)
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return _uncertain_result(prepared, f"adapter {operation} returned malformed JSON", latency)
    parsed = _redact(parsed, list(prepared.request["secrets"].values()))
    validation_errors = validate_result(parsed)
    identity_matches = (
        parsed.get("adapter_id") == prepared.invocation["adapter_id"]
        and parsed.get("capability_id") == prepared.invocation["capability_id"]
        and parsed.get("action_id") == prepared.invocation["action_id"]
    )
    if validation_errors or not identity_matches:
        return _uncertain_result(prepared, f"adapter {operation} result contract or identity mismatch", latency)
    return parsed


def _claim_expired_lease(action: dict[str, Any], prepared: PreparedInvocation, action_path: Path, context: ExecutionContext) -> dict[str, Any]:
    lease = action.get("lease")
    if lease is None or (lease.get("owner_id") == context.owner_id and lease.get("fencing_token") == context.fencing_token):
        return action
    if context.now_epoch < lease.get("expires_at", 0) or not isinstance(context.fencing_token, int) or context.fencing_token <= lease.get("fencing_token", 0):
        raise ValueError("stale tool action fencing token")
    claimed = json.loads(json.dumps(action))
    claimed["lease"] = {
        "owner_id": context.owner_id,
        "fencing_token": context.fencing_token,
        "expires_at": context.now_epoch + prepared.capability["timeout_seconds"] + 30,
    }
    return save_action_atomic(
        action_path, claimed, action["revision"], owner_id=context.owner_id,
        fencing_token=context.fencing_token, now=context.now_epoch,
    )


def execute_prepared(prepared: PreparedInvocation, action_path: Path, context: ExecutionContext) -> dict[str, Any]:
    if not reserve_idempotency(
        action_path.parent, prepared.action["idempotency_key"],
        prepared.action["action_id"], prepared.action["input_hash"], action_path.name,
    ):
        return _blocked_result(prepared, "idempotency key is already bound to another action identity")
    if action_path.exists():
        current = load_action(action_path)
        if current.get("action_id") != prepared.action["action_id"] or current.get("input_hash") != prepared.action["input_hash"]:
            raise ValueError("existing action identity conflicts with prepared invocation")
        if current.get("state") in {"RUNNING", "UNCERTAIN"}:
            return _blocked_result(prepared, "existing action may have completed; reconcile before retry")
        if current.get("state") in {"SUCCEEDED", "FAILED", "BLOCKED"}:
            return _blocked_result(prepared, f"existing action is {current['state']}; lifecycle-owner transition required")
        action = current
    else:
        action = save_action_atomic(
            action_path,
            prepared.action,
            0,
            owner_id=context.owner_id,
            fencing_token=context.fencing_token,
            now=context.now_epoch,
        )
    persistence = {"owner_id": context.owner_id, "fencing_token": context.fencing_token, "now": context.now_epoch}
    action = _claim_expired_lease(action, prepared, action_path, context)
    if action["state"] == "PLANNED":
        action = transition_action(action, "AUTHORIZED", {"authority_grant_id": action["authority_grant_id"]})
        action = save_action_atomic(action_path, action, action["revision"], **persistence)
    action = transition_action(action, "RUNNING", {"adapter_version": prepared.adapter["adapter_version"]})
    action = save_action_atomic(action_path, action, action["revision"], **persistence)

    result = _invoke_adapter(prepared, "execute")

    terminal_evidence = {"result_hash": result["output_hash"], "diagnostics": result["diagnostics"]}
    action = transition_action(action, result["state"], terminal_evidence)
    save_action_atomic(action_path, action, action["revision"], **persistence)
    return result


def reconcile_prepared(prepared: PreparedInvocation, action_path: Path, context: ExecutionContext) -> dict[str, Any]:
    action = load_action(action_path)
    if action.get("state") != "UNCERTAIN":
        raise ValueError("only UNCERTAIN actions require reconciliation")
    if not prepared.capability.get("supports_reconciliation"):
        raise ValueError("capability does not support reconciliation")
    if action.get("action_id") != prepared.action.get("action_id") or action.get("input_hash") != prepared.action.get("input_hash"):
        raise ValueError("reconciliation invocation conflicts with durable action")
    action = _claim_expired_lease(action, prepared, action_path, context)
    result = _invoke_adapter(prepared, "reconcile")
    persistence = {"owner_id": context.owner_id, "fencing_token": context.fencing_token, "now": context.now_epoch}
    reconciliation = {"result_hash": result["output_hash"], "state": result["state"], "diagnostics": result["diagnostics"]}
    if result["state"] == "UNCERTAIN":
        action = json.loads(json.dumps(action))
        action.setdefault("evidence", []).append({"target_state": "UNCERTAIN", "reconciliation": reconciliation})
    else:
        action = transition_action(action, result["state"], {"reconciliation": reconciliation})
    save_action_atomic(action_path, action, action["revision"], **persistence)
    return result
