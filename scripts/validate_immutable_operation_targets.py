from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tool_adapter_contract import (  # noqa: E402
    canonical_target_digest,
    load_registry,
    validate_invocation,
    validate_operation_targets,
)


def fetch_targets(items: list[dict]) -> dict:
    value = {"kind": "git-fetch-refs", "items": items}
    return {**value, "digest": canonical_target_digest(value)}


registry = load_registry(ROOT / "config/tool-adapters.json")
targets = fetch_targets([{"ref": "refs/heads/main", "object_id": "1" * 40}])
invocation = {
    "contract_version": "2.0",
    "adapter_id": "git-local",
    "capability_id": "git.fetch",
    "action_id": "act-immutable01",
    "idempotency_key": "idem-immutable01",
    "plan_id": "plan-immutable01",
    "plan_revision": 1,
    "arguments": {"repository": "repo", "remote": "origin"},
    "operation_targets": targets,
    "authority_grant_id": "grant-immutable01",
    "deadline": "2099-08-11T12:00:00Z",
}

errors: list[str] = []
if validate_invocation(invocation, registry):
    errors.append("valid immutable fetch targets were rejected")
if validate_operation_targets("git.fetch", targets, registry):
    errors.append("valid immutable fetch target contract was rejected")

mutations = []
drifted = json.loads(json.dumps(targets))
drifted["items"][0]["object_id"] = "2" * 40
mutations.append(("target digest drift", drifted))
duplicate = fetch_targets([targets["items"][0], targets["items"][0]])
mutations.append(("duplicate target", duplicate))
unsorted = fetch_targets([
    {"ref": "refs/heads/z", "object_id": "3" * 40},
    {"ref": "refs/heads/a", "object_id": "4" * 40},
])
mutations.append(("unsorted targets", unsorted))
escaped = {"kind": "eval-bundle-archives", "items": [{"relative_path": "../outside.zip", "sha256": "5" * 64, "size_bytes": 1}]}
escaped = {**escaped, "digest": canonical_target_digest(escaped)}
mutations.append(("bundle path escape", escaped))

for label, value in mutations:
    capability = "git.import_bundle" if value["kind"] == "eval-bundle-archives" else "git.fetch"
    if not validate_operation_targets(capability, value, registry):
        errors.append(f"{label} was accepted")

for error in errors:
    print(f"ERROR: {error}")
if errors:
    raise SystemExit(1)
print("Validated immutable operation-target identity and negative drift mutations.")
