"""Durable, fenced state for controlled tool actions."""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
from typing import Any

from tool_adapter_contract import validate_action_state

ALLOWED_TRANSITIONS = {
    "PLANNED": {"AUTHORIZED", "BLOCKED"},
    "AUTHORIZED": {"RUNNING", "BLOCKED"},
    "RUNNING": {"SUCCEEDED", "FAILED", "UNCERTAIN", "BLOCKED"},
    "UNCERTAIN": {"SUCCEEDED", "FAILED", "AUTHORIZED", "BLOCKED"},
    "BLOCKED": {"PLANNED", "AUTHORIZED"},
    "SUCCEEDED": set(),
    "FAILED": {"AUTHORIZED"},
}


def load_action(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_action_state(value)
    if errors:
        raise ValueError("invalid tool action state: " + "; ".join(errors))
    return value


def transition_action(state: dict[str, Any], target: str, evidence: dict[str, Any]) -> dict[str, Any]:
    current = state.get("state")
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"illegal tool action transition: {current} -> {target}")
    if current == "UNCERTAIN" and not isinstance(evidence.get("reconciliation"), dict):
        raise ValueError("UNCERTAIN action requires reconciliation evidence before transition")
    if current == "FAILED" and target == "AUTHORIZED" and state.get("attempt", 0) >= state.get("max_attempts", 0):
        raise ValueError("action retry budget exhausted")
    value = json.loads(json.dumps(state))
    value["state"] = target
    if target == "RUNNING":
        value["attempt"] = value.get("attempt", 0) + 1
    value.setdefault("evidence", []).append({"target_state": target, **evidence})
    errors = validate_action_state(value)
    if errors:
        raise ValueError("invalid transitioned action: " + "; ".join(errors))
    return value


def _fsync_directory(directory: Path) -> None:
    try:
        descriptor = os.open(str(directory), os.O_RDONLY)
    except OSError as exc:
        if exc.errno in {errno.EINVAL, errno.ENOTSUP, errno.EISDIR}:
            return
        raise
    try:
        os.fsync(descriptor)
    except OSError as exc:
        if exc.errno not in {errno.EINVAL, errno.ENOTSUP}:
            raise
    finally:
        os.close(descriptor)


def _validate_lease(current: dict[str, Any] | None, proposed: dict[str, Any], owner_id: str | None, fencing_token: int | None, now: int | None) -> None:
    prior = (current or {}).get("lease")
    next_lease = proposed.get("lease")
    if prior is None:
        if next_lease is not None and (next_lease.get("owner_id") != owner_id or next_lease.get("fencing_token") != fencing_token):
            raise ValueError("stale tool action fencing token")
        return
    same_owner = prior.get("owner_id") == owner_id and prior.get("fencing_token") == fencing_token
    turnover = (
        now is not None
        and prior.get("expires_at", 0) <= now
        and next_lease is not None
        and next_lease.get("owner_id") == owner_id
        and next_lease.get("fencing_token") == fencing_token
        and isinstance(fencing_token, int)
        and fencing_token > prior.get("fencing_token", 0)
    )
    if not same_owner and not turnover:
        raise ValueError("stale tool action fencing token")


def save_action_atomic(
    path: Path,
    state: dict[str, Any],
    expected_revision: int,
    *,
    owner_id: str | None = None,
    fencing_token: int | None = None,
    now: int | None = None,
) -> dict[str, Any]:
    current = load_action(path) if path.is_file() else None
    actual_revision = current.get("revision", 0) if current else 0
    if actual_revision != expected_revision:
        raise ValueError("stale tool action revision")
    _validate_lease(current, state, owner_id, fencing_token, now)
    value = json.loads(json.dumps(state))
    value["revision"] = actual_revision + 1
    errors = validate_action_state(value)
    if errors:
        raise ValueError("invalid tool action state: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    _fsync_directory(path.parent)
    return value


def find_by_idempotency(ledger_dir: Path, key: str) -> dict[str, Any] | None:
    for path in sorted(ledger_dir.glob("*.json")):
        action = load_action(path)
        if action.get("idempotency_key") == key:
            return action
    return None
