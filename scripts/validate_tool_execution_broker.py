from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tool_execution_broker import ExecutionContext, execute_prepared, prepare_invocation, prepare_reconciliation, reconcile_prepared  # noqa: E402
from tool_action_store import load_action  # noqa: E402

FIXTURE = ROOT / "scripts/fixtures/tool_adapter_fixture.py"


def registry(timeout: int = 1, maximum: int = 1024) -> dict:
    return {
        "schema_version": 1,
        "protocol_version": "1.0",
        "adapters": [{
            "adapter_id": "fixture-cli",
            "adapter_version": "1.0.0",
            "transport": "local-cli",
            "provenance": {"kind": "repository-script", "path": "scripts/fixtures/tool_adapter_fixture.py", "sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest()},
            "capabilities": [{
                "capability_id": "fixture.execute",
                "risk": "local-mutating",
                "required_authority": ["fixture.execute"],
                "allowed_root_refs": ["FIXTURE_ROOT"],
                "secret_refs": ["FIXTURE_SECRET"],
                "timeout_seconds": timeout,
                "max_attempts": 1,
                "idempotent": True,
                "supports_reconciliation": True,
                "max_output_bytes": maximum,
                "argument_schema": {"type": "object", "additionalProperties": False, "required": ["repository", "mode"], "properties": {"repository": {"type": "string", "minLength": 1}, "mode": {"enum": ["success", "timeout", "malformed", "oversized", "leak", "no-change"]}}},
            }],
        }],
    }


def invocation(mode: str = "success") -> dict:
    return {
        "contract_version": "1.0",
        "adapter_id": "fixture-cli",
        "capability_id": "fixture.execute",
        "action_id": "act-00000001",
        "idempotency_key": "idem-00000001",
        "plan_id": "plan-00000001",
        "plan_revision": 1,
        "arguments": {"repository": "repo", "mode": mode},
        "authority_grant_id": "grant-000001",
        "deadline": "2099-08-11T12:00:00Z",
    }


errors: list[str] = []
with tempfile.TemporaryDirectory(prefix="cloudbox-tool-broker-") as temp_name:
    root = Path(temp_name)
    (root / "repo").mkdir()
    context = ExecutionContext(
        root_refs={"FIXTURE_ROOT": root},
        secret_values={"FIXTURE_SECRET": "private-value"},
        approved_authority={"fixture.execute"},
        repository_root=ROOT,
        owner_id="fixture-owner",
        fencing_token=1,
        now_epoch=1760000000,
    )
    prepared = prepare_invocation(invocation(), registry(), context)
    if isinstance(prepared.argv, str) or prepared.argv[:2] != [sys.executable, str(FIXTURE)]:
        errors.append("broker did not prepare an argument-array fixture command")
    result = execute_prepared(prepared, root / "actions" / "act-00000001.json", context)
    if result["state"] != "SUCCEEDED":
        errors.append("valid fixture execution did not succeed")

    for label, mutate in (
        ("raw command", lambda value: value.update({"command": "git status"})),
        ("unknown adapter", lambda value: value.update({"adapter_id": "unknown-cli"})),
        ("path escape", lambda value: value["arguments"].update({"repository": "../outside"})),
    ):
        value = invocation()
        mutate(value)
        try:
            prepare_invocation(value, registry(), context)
        except ValueError:
            pass
        else:
            errors.append(f"{label} was accepted")

    no_authority = ExecutionContext(root_refs=context.root_refs, secret_values=context.secret_values, approved_authority=set(), repository_root=ROOT, owner_id="fixture-owner", fencing_token=1, now_epoch=1760000000)
    try:
        prepare_invocation(invocation(), registry(), no_authority)
    except ValueError:
        pass
    else:
        errors.append("mutation without authority was accepted")

    missing_secret = ExecutionContext(root_refs=context.root_refs, secret_values={}, approved_authority=context.approved_authority, repository_root=ROOT, owner_id="fixture-owner", fencing_token=1, now_epoch=1760000000)
    try:
        prepare_invocation(invocation(), registry(), missing_secret)
    except ValueError:
        pass
    else:
        errors.append("missing secret reference was accepted")

    bad_digest = registry()
    bad_digest["adapters"][0]["provenance"]["sha256"] = "0" * 64
    try:
        prepare_invocation(invocation(), bad_digest, context)
    except ValueError:
        pass
    else:
        errors.append("executable provenance drift was accepted")

    expired = invocation()
    expired["deadline"] = "2000-01-01T00:00:00Z"
    try:
        prepare_invocation(expired, registry(), context)
    except ValueError as exc:
        if "deadline" not in str(exc):
            errors.append("expired invocation failed for the wrong reason")
    else:
        errors.append("expired invocation was accepted")

    for index, mode in enumerate(("leak", "malformed", "oversized", "timeout"), start=2):
        value = invocation(mode)
        value["action_id"] = f"act-0000000{index}"
        value["idempotency_key"] = f"idem-0000000{index}"
        prepared = prepare_invocation(value, registry(), context)
        result = execute_prepared(prepared, root / "actions" / f"act-0000000{index}.json", context)
        serialized = json.dumps(result)
        if "private-value" in serialized:
            errors.append("secret leaked into broker result")
        expected = "SUCCEEDED" if mode == "leak" else "UNCERTAIN"
        if result["state"] != expected:
            errors.append(f"{mode} produced {result['state']} instead of {expected}")
        if mode == "timeout" and load_action(root / "actions" / f"act-0000000{index}.json").get("attempt") != 1:
            errors.append("timeout caused an implicit retry")
        if mode == "timeout":
            resumed = execute_prepared(prepared, root / "actions" / f"act-0000000{index}.json", context)
            if resumed["state"] != "BLOCKED" or load_action(root / "actions" / f"act-0000000{index}.json")["attempt"] != 1:
                errors.append("existing uncertain checkpoint was not resumed without re-execution")
            changed_secret_context = ExecutionContext(root_refs=context.root_refs, secret_values={"FIXTURE_SECRET": "changed-private-value"}, approved_authority=context.approved_authority, repository_root=ROOT, owner_id="fixture-owner", fencing_token=1, now_epoch=4100000000)
            changed_prepared = prepare_reconciliation(value, registry(), changed_secret_context)
            try:
                reconcile_prepared(changed_prepared, root / "actions" / f"act-0000000{index}.json", changed_secret_context)
            except ValueError as exc:
                if "conflicts" not in str(exc):
                    errors.append("changed secret reference failed for the wrong reason")
            else:
                errors.append("reconciliation accepted changed secret/config identity")
            later_context = ExecutionContext(root_refs=context.root_refs, secret_values=context.secret_values, approved_authority=context.approved_authority, repository_root=ROOT, owner_id="replacement-owner", fencing_token=2, now_epoch=4100000100)
            changed_registry = registry()
            changed_registry["adapters"][0]["adapter_version"] = "9.9.9"
            changed_version = prepare_reconciliation(value, changed_registry, later_context)
            try:
                reconcile_prepared(changed_version, root / "actions" / f"act-0000000{index}.json", later_context)
            except ValueError as exc:
                if "conflicts" not in str(exc):
                    errors.append("adapter-version drift failed for the wrong reason")
            else:
                errors.append("reconciliation accepted adapter-version drift")
            reconciliation_prepared = prepare_reconciliation(value, registry(), later_context)
            reconciled = reconcile_prepared(reconciliation_prepared, root / "actions" / f"act-0000000{index}.json", later_context)
            reconciled_state = load_action(root / "actions" / f"act-0000000{index}.json")
            if reconciled["state"] != "SUCCEEDED" or reconciled["output"].get("status") != "RECONCILED":
                errors.append("adapter reconciliation did not classify external completion")
            if reconciled_state["state"] != "SUCCEEDED" or reconciled_state["attempt"] != 1:
                errors.append("reconciliation re-executed or failed to close durable action")

    duplicate = invocation("success")
    duplicate["action_id"] = "act-00000007"
    duplicate["idempotency_key"] = "idem-00000001"
    duplicate_result = execute_prepared(prepare_invocation(duplicate, registry(), context), root / "actions/act-00000007.json", context)
    if duplicate_result["state"] != "BLOCKED" or (root / "actions/act-00000007.json").exists():
        errors.append("duplicate idempotency key executed under a second action identity")

    no_change = invocation("no-change")
    no_change["action_id"] = "act-00000006"
    no_change["idempotency_key"] = "idem-00000006"
    result = execute_prepared(prepare_invocation(no_change, registry(), context), root / "actions/act-00000006.json", context)
    if result["output"].get("status") != "NO_CHANGE" or result["model_calls"] != 0:
        errors.append("deterministic no-change path consumed a model call")

for error in errors:
    print(f"ERROR: {error}")
if errors:
    raise SystemExit(1)
print("Validated controlled CLI authority, provenance, paths, secrets, timeout, output bounds, and zero-model no-change.")
