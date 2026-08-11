from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tool_adapter_contract import (  # noqa: E402
    REGISTRY_PATH,
    canonical_target_digest,
    get_capability,
    load_registry,
    validate_action_state,
    validate_invocation,
    validate_registry,
    validate_result,
)

errors: list[str] = []
registry = load_registry(REGISTRY_PATH)
no_targets = {"kind": "none", "items": []}
no_targets = {**no_targets, "digest": canonical_target_digest(no_targets)}

valid_invocation = {
    "contract_version": "2.0",
    "adapter_id": "git-local",
    "capability_id": "git.inspect",
    "action_id": "act-00000001",
    "idempotency_key": "idem-00000001",
    "plan_id": "plan-00000001",
    "plan_revision": 1,
    "arguments": {"repository": "fixture"},
    "operation_targets": no_targets,
    "authority_grant_id": None,
    "deadline": "2026-08-11T12:00:00Z",
}
if validate_invocation(valid_invocation, registry):
    errors.append("valid read-only invocation was rejected")

mutations = {
    "raw command": {**valid_invocation, "command": "git status"},
    "literal environment": {**valid_invocation, "environment": {"TOKEN": "secret"}},
    "secret values": {**valid_invocation, "secret_values": {"REMOTE": "private"}},
    "unknown capability": {**valid_invocation, "capability_id": "git.shell"},
    "invalid action id": {**valid_invocation, "action_id": "x"},
    "unexpected argument": {**valid_invocation, "arguments": {"repository": "fixture", "command": "status"}},
}
for label, value in mutations.items():
    if not validate_invocation(value, registry):
        errors.append(f"{label} mutation was accepted")

forbidden_registry_mutations: dict[str, dict] = {}
duplicate = copy.deepcopy(registry)
duplicate["adapters"].append(copy.deepcopy(duplicate["adapters"][0]))
forbidden_registry_mutations["duplicate adapter"] = duplicate
bad_risk = copy.deepcopy(registry)
bad_risk["adapters"][0]["capabilities"][0]["risk"] = "unbounded"
forbidden_registry_mutations["invalid risk"] = bad_risk
missing_authority = copy.deepcopy(registry)
missing_authority["adapters"][0]["capabilities"][1]["required_authority"] = []
forbidden_registry_mutations["mutation without authority"] = missing_authority
remote_without_reconcile = copy.deepcopy(registry)
remote_without_reconcile["adapters"][0]["capabilities"][1]["risk"] = "remote-mutating"
remote_without_reconcile["adapters"][0]["capabilities"][1]["supports_reconciliation"] = False
forbidden_registry_mutations["remote mutation without reconciliation"] = remote_without_reconcile
unbounded = copy.deepcopy(registry)
unbounded["adapters"][0]["capabilities"][0]["max_output_bytes"] = 0
forbidden_registry_mutations["unbounded output"] = unbounded

for label, value in forbidden_registry_mutations.items():
    if not validate_registry(value):
        errors.append(f"{label} registry mutation was accepted")

valid_result = {
    "contract_version": "1.0",
    "adapter_id": "git-local",
    "capability_id": "git.inspect",
    "action_id": "act-00000001",
    "state": "SUCCEEDED",
    "summary": "repository inspected",
    "output": {"head": "0" * 40},
    "artifact_refs": [],
    "observed_side_effects": [],
    "diagnostics": [],
    "output_hash": "",
    "latency_ms": 1,
    "model_calls": 0,
}
valid_result["output_hash"] = __import__("hashlib").sha256(json.dumps(valid_result["output"], sort_keys=True).encode("utf-8")).hexdigest()
if validate_result(valid_result):
    errors.append("valid result was rejected")
bad_result = copy.deepcopy(valid_result)
bad_result["state"] = "RUNNING"
if not validate_result(bad_result):
    errors.append("non-terminal public result was accepted")
bad_hash = copy.deepcopy(valid_result)
bad_hash["output_hash"] = "0" * 64
if not validate_result(bad_hash):
    errors.append("result output_hash mismatch was accepted")

valid_action = {
    "schema_version": 2,
    "revision": 1,
    "action_id": "act-00000001",
    "idempotency_key": "idem-00000001",
    "plan_id": "plan-00000001",
    "plan_revision": 1,
    "adapter_id": "git-local",
    "adapter_version": "1.0.0",
    "capability_id": "git.inspect",
    "state": "PLANNED",
    "attempt": 0,
    "max_attempts": 1,
    "input_hash": "0" * 64,
    "operation_targets": no_targets,
    "target_evidence": [],
    "authority_grant_id": None,
    "evidence": [],
    "lease": None,
}
if validate_action_state(valid_action):
    errors.append("valid action state was rejected")

# Positive propagation and negative schema drift: the public interpreter must
# observe an injected authoritative schema, while the default schema remains
# unchanged.
with tempfile.TemporaryDirectory(prefix="cloudbox-tool-contract-") as temp_name:
    temp = Path(temp_name)
    schema = json.loads((ROOT / "evals/agent/contracts/tool-adapter-registry.schema.json").read_text(encoding="utf-8"))
    max_output = schema["$defs"]["capability"]["properties"]["max_output_bytes"]
    max_output["minimum"] = 8192
    drift_path = temp / "registry.schema.json"
    drift_path.write_text(json.dumps(schema), encoding="utf-8")
    if not validate_registry(registry, drift_path):
        errors.append("authoritative registry schema drift did not propagate")
    if validate_registry(registry):
        errors.append("default registry schema changed during drift injection")

if get_capability(registry, "git-local", "git.inspect")["risk"] != "read-only":
    errors.append("registry consumer did not resolve the authoritative capability")

for error in errors:
    print(f"ERROR: {error}")
if errors:
    raise SystemExit(1)
print("Validated authoritative tool adapter registry, envelopes, propagation, and negative drift mutations.")
