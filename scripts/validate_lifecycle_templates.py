#!/usr/bin/env python3
"""RED/GREEN contract checks for the authoritative lifecycle-template catalog.

Task 1 intentionally leaves the shared loader and selector absent.  This
validator therefore fails closed until Task 2 supplies
``lifecycle_template_contract.py``; its mutation checks then become executable
anti-drift evidence instead of a second template implementation.
"""

from __future__ import annotations

import copy
import importlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REGISTRY_PATH = ROOT / "config" / "lifecycle-templates.json"
CONTRACT_PATH = SCRIPTS / "lifecycle_template_contract.py"

IMPLEMENTED_TEMPLATE_IDS = {
    "lightweight-change",
    "bounded-feature",
    "skill-evolution",
}
DEFERRED_TEMPLATE_IDS = {
    "iterative-discovery",
    "architecture-change",
    "brownfield-refactor",
    "hotfix",
    "release",
    "hardware-integration",
    "incident-recovery",
}
REQUIRED_IMPLEMENTED_FIELDS = {
    "template_id",
    "status",
    "contract_version",
    "applicability",
    "exclusions",
    "stages",
    "gates",
    "owners",
    "required_evidence",
    "review_level",
    "resume_reconciliation",
    "reuse_invalidation",
    "compatible_overlays",
    "escalation_conditions",
}
REQUIRED_OWNER_KEYS = {
    "lifecycle_plan",
    "state",
    "policy",
    "action",
    "evidence",
}
REQUIRED_CONSUMER_PATHS = {"scripts/lifecycle_template_contract.py"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def registry_errors(registry: Any) -> list[str]:
    """Return deterministic schema and lifecycle-authority failures."""
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["lifecycle template registry must be an object"]
    if registry.get("schema_version") != 1:
        fail(errors, "lifecycle template registry schema_version must be integer 1")

    templates = registry.get("templates")
    if not isinstance(templates, dict):
        return errors + ["lifecycle template registry must contain a templates object"]

    expected_ids = IMPLEMENTED_TEMPLATE_IDS | DEFERRED_TEMPLATE_IDS
    actual_ids = set(templates)
    missing_ids = expected_ids - actual_ids
    if missing_ids:
        fail(
            errors,
            "lifecycle template registry is missing required IDs: "
            f"expected={sorted(expected_ids)!r} actual={sorted(actual_ids)!r}",
        )

    for template_id, entry in templates.items():
        prefix = f"templates/{template_id}"
        if not isinstance(entry, dict):
            fail(errors, f"{prefix}: entry must be an object")
            continue
        if entry.get("template_id") != template_id:
            fail(errors, f"{prefix}: template_id must match its registry key")
        if entry.get("contract_version") != 1:
            fail(errors, f"{prefix}: contract_version must be integer 1")

        expected_status = "deferred" if template_id in DEFERRED_TEMPLATE_IDS else "implemented"
        if entry.get("status") != expected_status:
            fail(errors, f"{prefix}: status must be {expected_status!r}")

        if template_id in DEFERRED_TEMPLATE_IDS:
            reason = entry.get("deferred_reason")
            if not isinstance(reason, str) or not reason.strip():
                fail(errors, f"{prefix}: deferred template requires a deferred_reason")
            extra_mechanics = REQUIRED_IMPLEMENTED_FIELDS - {"template_id", "status", "contract_version"}
            if extra_mechanics & set(entry):
                fail(errors, f"{prefix}: deferred template must not define implementation mechanics")
            continue

        missing = REQUIRED_IMPLEMENTED_FIELDS - set(entry)
        if missing:
            fail(errors, f"{prefix}: missing required fields {sorted(missing)!r}")
            continue
        if not isinstance(entry["applicability"], dict) or not entry["applicability"]:
            fail(errors, f"{prefix}: applicability must be a non-empty object")
        for field in (
            "exclusions",
            "stages",
            "gates",
            "required_evidence",
            "escalation_conditions",
        ):
            if not isinstance(entry[field], list) or not entry[field]:
                fail(errors, f"{prefix}: {field} must be a non-empty list")
        if not isinstance(entry["compatible_overlays"], list):
            fail(errors, f"{prefix}: compatible_overlays must be a list")
        if not isinstance(entry["owners"], dict):
            fail(errors, f"{prefix}: owners must be an object")
        else:
            missing_owners = REQUIRED_OWNER_KEYS - set(entry["owners"])
            if missing_owners:
                fail(errors, f"{prefix}: owners missing {sorted(missing_owners)!r}")
            if entry["owners"].get("lifecycle_plan") != "development-process-tailoring":
                fail(errors, f"{prefix}: lifecycle ownership must remain development-process-tailoring")
        if not isinstance(entry["review_level"], str) or not entry["review_level"]:
            fail(errors, f"{prefix}: review_level must be a non-empty string")
        for field in ("resume_reconciliation", "reuse_invalidation"):
            if not isinstance(entry[field], dict) or not entry[field]:
                fail(errors, f"{prefix}: {field} must be a non-empty object")

    required_consumers = registry.get("required_consumer_paths")
    if not isinstance(required_consumers, list) or set(required_consumers) != REQUIRED_CONSUMER_PATHS:
        fail(
            errors,
            "lifecycle template registry required_consumer_paths must name the shared contract",
        )
    return errors


def mutation_must_fail(registry: dict[str, Any], label: str) -> None:
    if not registry_errors(registry):
        raise AssertionError(f"lifecycle template negative mutation was accepted: {label}")


def run_contract_mutations(registry: dict[str, Any]) -> list[str]:
    """Exercise future contract propagation without copying selector policy here."""
    errors: list[str] = []
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    try:
        contract = importlib.import_module("lifecycle_template_contract")
    except Exception as exc:  # pragma: no cover - guarded by the RED prerequisite
        return [f"cannot load shared lifecycle template contract: {exc}"]

    for name in ("load_templates", "assess_template"):
        if not callable(getattr(contract, name, None)):
            fail(errors, f"shared lifecycle template contract is missing {name}()")
    if errors:
        return errors

    try:
        loaded = contract.load_templates(REGISTRY_PATH)
    except Exception as exc:
        return [f"shared lifecycle template contract cannot load registry: {exc}"]
    if loaded != registry:
        fail(errors, "shared lifecycle template loader changed authoritative registry content")

    synthetic_id = "validator-synthetic-template"
    synthetic = copy.deepcopy(registry)
    synthetic_entry = copy.deepcopy(synthetic["templates"]["lightweight-change"])
    synthetic_entry["template_id"] = synthetic_id
    synthetic["templates"][synthetic_id] = synthetic_entry
    synthetic_errors = registry_errors(synthetic)
    if synthetic_errors:
        return [
            "adding an implemented lifecycle template to the authoritative registry "
            f"was rejected: {error}"
            for error in synthetic_errors
        ]
    with tempfile.TemporaryDirectory(prefix="cloudbox-lifecycle-template-") as temp_name:
        path = Path(temp_name) / "lifecycle-templates.json"
        path.write_text(json.dumps(synthetic), encoding="utf-8")
        try:
            propagated = contract.load_templates(path)
        except Exception as exc:
            fail(errors, f"synthetic registry template did not propagate through shared loader: {exc}")
        else:
            if synthetic_id not in propagated.get("templates", {}):
                fail(errors, "synthetic registry template did not appear through shared loader")
            else:
                facts = {
                    **propagated["templates"][synthetic_id]["applicability"],
                    "external_side_effect": False,
                    "authority_or_state": False,
                    "sensitive_or_privileged": False,
                    "platform_or_compatibility": False,
                    "irreversible_or_unreconciled": False,
                    "outside_verified_envelope": False,
                }
                try:
                    resolution = contract.assess_template(synthetic_id, facts, propagated)
                except Exception as exc:
                    fail(errors, f"synthetic registry template was unreachable from selector: {exc}")
                else:
                    if resolution.get("status") != "selected":
                        fail(errors, "synthetic registry template did not select through shared selector")
                try:
                    stale_resolution = contract.assess_template(synthetic_id, facts, registry)
                except Exception as exc:
                    fail(errors, f"stale consumer mapping did not fail closed: {exc}")
                else:
                    if stale_resolution.get("status") != "unsupported":
                        fail(errors, "stale consumer mapping did not return unsupported")

    # A consumer that hand-copies the current IDs must be detected as stale as
    # soon as the authoritative registry gains a template.
    copied_consumer_ids = set(registry["templates"])
    if copied_consumer_ids == set(synthetic["templates"]):
        fail(errors, "copied consumer mapping was not detected as stale")
    return errors


def main() -> int:
    errors: list[str] = []
    registry: dict[str, Any] | None = None
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(errors, "missing authoritative lifecycle template registry: config/lifecycle-templates.json")
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"cannot read authoritative lifecycle template registry: {exc}")
    else:
        errors.extend(registry_errors(registry))

    if not CONTRACT_PATH.is_file():
        fail(errors, "missing shared lifecycle template contract: scripts/lifecycle_template_contract.py")
    elif registry is not None and not registry_errors(registry):
        errors.extend(run_contract_mutations(registry))

    if registry is not None and not registry_errors(registry):
        owner_removed = copy.deepcopy(registry)
        del owner_removed["templates"]["lightweight-change"]["owners"]["lifecycle_plan"]
        mutation_must_fail(owner_removed, "lifecycle ownership removed")
        evidence_removed = copy.deepcopy(registry)
        del evidence_removed["templates"]["bounded-feature"]["required_evidence"]
        mutation_must_fail(evidence_removed, "required evidence removed")
        deferred_reclassified = copy.deepcopy(registry)
        deferred_reclassified["templates"]["release"]["status"] = "implemented"
        mutation_must_fail(deferred_reclassified, "deferred status removed")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Validated authoritative lifecycle template registry and shared-consumer propagation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
