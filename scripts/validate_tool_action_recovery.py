from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tool_action_store import (  # noqa: E402
    find_by_idempotency,
    load_action,
    save_action_atomic,
    transition_action,
)
from tool_adapter_contract import canonical_target_digest  # noqa: E402


def base_action() -> dict:
    targets = {"kind": "git-fetch-refs", "items": []}
    targets = {**targets, "digest": canonical_target_digest(targets)}
    return {
        "schema_version": 2,
        "revision": 0,
        "action_id": "act-00000001",
        "idempotency_key": "idem-00000001",
        "plan_id": "plan-00000001",
        "plan_revision": 1,
        "adapter_id": "git-local",
        "adapter_version": "1.0.0",
        "capability_id": "git.fetch",
        "state": "PLANNED",
        "attempt": 0,
        "max_attempts": 2,
        "input_hash": "0" * 64,
        "operation_targets": targets,
        "target_evidence": [],
        "authority_grant_id": "grant-000001",
        "evidence": [],
        "lease": None,
    }


errors: list[str] = []
planned = base_action()
authorized = transition_action(planned, "AUTHORIZED", {"authority": "grant-000001"})
running = transition_action(authorized, "RUNNING", {"started": True})
uncertain = transition_action(running, "UNCERTAIN", {"reason": "timeout"})
try:
    transition_action(uncertain, "AUTHORIZED", {"reason": "retry"})
except ValueError as exc:
    if "reconciliation" not in str(exc):
        errors.append("uncertain retry failed for the wrong reason")
else:
    errors.append("ambiguous completion retried without reconciliation")

reconciled = transition_action(uncertain, "SUCCEEDED", {"reconciliation": {"status": "observed-complete"}})
if reconciled["state"] != "SUCCEEDED" or reconciled["evidence"][-1]["target_state"] != "SUCCEEDED":
    errors.append("reconciled terminal evidence was not appended")
try:
    transition_action(reconciled, "AUTHORIZED", {"reason": "repeat"})
except ValueError:
    pass
else:
    errors.append("terminal success was reopened")

with tempfile.TemporaryDirectory(prefix="cloudbox-tool-actions-") as temp_name:
    ledger = Path(temp_name)
    action_path = ledger / "act-00000001.json"
    saved = save_action_atomic(action_path, planned, 0)
    if saved["revision"] != 1 or load_action(action_path)["revision"] != 1:
        errors.append("atomic state revision did not advance")
    if find_by_idempotency(ledger, "idem-00000001")["action_id"] != "act-00000001":
        errors.append("idempotency lookup missed existing action")
    try:
        save_action_atomic(action_path, authorized, 0)
    except ValueError as exc:
        if "stale" not in str(exc):
            errors.append("stale revision failed for the wrong reason")
    else:
        errors.append("stale revision overwrote action")

    leased = dict(saved)
    leased["lease"] = {"owner_id": "owner-a", "fencing_token": 1, "expires_at": 10}
    leased = save_action_atomic(action_path, leased, 1, owner_id="owner-a", fencing_token=1, now=1)
    stale = dict(leased)
    try:
        save_action_atomic(action_path, stale, 2, owner_id="owner-b", fencing_token=1, now=5)
    except ValueError as exc:
        if "fencing" not in str(exc):
            errors.append("stale lease failed for the wrong reason")
    else:
        errors.append("stale owner bypassed fencing")
    takeover = dict(leased)
    takeover["lease"] = {"owner_id": "owner-b", "fencing_token": 2, "expires_at": 20}
    takeover = save_action_atomic(action_path, takeover, 2, owner_id="owner-b", fencing_token=2, now=11)
    if takeover["lease"]["owner_id"] != "owner-b":
        errors.append("expired lease could not transfer with higher fencing")

for error in errors:
    print(f"ERROR: {error}")
if errors:
    raise SystemExit(1)
print("Validated durable tool action transitions, idempotency, atomicity, leases, fencing, and reconciliation.")
