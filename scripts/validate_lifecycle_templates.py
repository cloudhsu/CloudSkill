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

from review_assurance_contract import LEVELS

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
    "exclusion_facts",
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
REQUIRED_GATE_FIELDS = {"gate_id", "owner", "required_evidence", "transition"}
REQUIRED_RESUME_FIELDS = {
    "checkpoint_owner",
    "reconcile_before_resume",
    "on_unreconciled",
    "required_evidence",
}
REQUIRED_REUSE_FIELDS = {
    "reuse_when",
    "invalidate_when",
    "unaffected_evidence",
    "on_invalidation",
}
DELTA_FIELDS = (
    "external_side_effect",
    "authority_or_state",
    "sensitive_or_privileged",
    "platform_or_compatibility",
    "irreversible_or_unreconciled",
    "outside_verified_envelope",
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def is_nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def is_unique_nonempty_string_list(value: Any) -> bool:
    return is_nonempty_string_list(value) and len(value) == len(set(value))


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
        exclusions = entry["exclusions"] if isinstance(entry.get("exclusions"), list) else []
        if not is_unique_nonempty_string_list(exclusions):
            fail(errors, f"{prefix}: exclusions must be unique non-empty strings")
        exclusion_facts = entry.get("exclusion_facts")
        if not isinstance(exclusion_facts, dict) or not exclusion_facts:
            fail(errors, f"{prefix}: exclusion_facts must be a non-empty object")
        else:
            mapped_conditions: list[str] = []
            for fact_name, definition in exclusion_facts.items():
                if not isinstance(fact_name, str) or not fact_name:
                    fail(errors, f"{prefix}: exclusion fact names must be non-empty strings")
                    continue
                if not isinstance(definition, dict) or set(definition) != {"type", "condition"}:
                    fail(errors, f"{prefix}: exclusion fact {fact_name!r} has an invalid schema")
                    continue
                if definition["type"] != "boolean":
                    fail(errors, f"{prefix}: exclusion fact {fact_name!r} must be boolean")
                condition = definition["condition"]
                if not isinstance(condition, str) or condition not in exclusions:
                    fail(errors, f"{prefix}: exclusion fact {fact_name!r} must map to a declared exclusion")
                else:
                    mapped_conditions.append(condition)
            if set(mapped_conditions) != set(exclusions) or len(mapped_conditions) != len(set(mapped_conditions)):
                fail(errors, f"{prefix}: exclusion facts must map one-to-one to declared exclusions")
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
        owners = entry["owners"] if isinstance(entry["owners"], dict) else {}
        if not owners:
            fail(errors, f"{prefix}: owners must be an object")
        else:
            if set(owners) != REQUIRED_OWNER_KEYS:
                fail(errors, f"{prefix}: owners must declare exactly {sorted(REQUIRED_OWNER_KEYS)!r}")
            for owner_name, owner_id in owners.items():
                if not isinstance(owner_id, str) or not owner_id.strip():
                    fail(errors, f"{prefix}: owners/{owner_name} must be a non-empty string")
            if owners.get("lifecycle_plan") != "development-process-tailoring":
                fail(errors, f"{prefix}: lifecycle ownership must remain development-process-tailoring")
        if entry["review_level"] not in LEVELS:
            fail(errors, f"{prefix}: review_level must be a declared assurance level")

        required_evidence = entry["required_evidence"]
        if not is_unique_nonempty_string_list(required_evidence):
            fail(errors, f"{prefix}: required_evidence must be unique non-empty strings")
        evidence_set = set(required_evidence) if is_unique_nonempty_string_list(required_evidence) else set()
        if not is_unique_nonempty_string_list(entry["stages"]):
            fail(errors, f"{prefix}: stages must be unique non-empty identifiers")
        stage_set = set(entry["stages"]) if is_unique_nonempty_string_list(entry["stages"]) else set()
        gate_ids: set[str] = set()
        gates = entry["gates"] if isinstance(entry["gates"], list) else []
        for gate in gates:
            gate_prefix = f"{prefix}: gate"
            if not isinstance(gate, dict):
                fail(errors, f"{gate_prefix} must be an object")
                continue
            missing_gate_fields = REQUIRED_GATE_FIELDS - set(gate)
            if missing_gate_fields:
                fail(errors, f"{gate_prefix} missing {sorted(missing_gate_fields)!r}")
                continue
            gate_id = gate["gate_id"]
            if not isinstance(gate_id, str) or not gate_id.strip():
                fail(errors, f"{gate_prefix} gate_id must be a non-empty string")
            elif gate_id in gate_ids:
                fail(errors, f"{gate_prefix} gate_id must be unique: {gate_id!r}")
            else:
                gate_ids.add(gate_id)
            if not isinstance(gate["owner"], str) or gate["owner"] not in set(owners.values()):
                fail(errors, f"{gate_prefix} owner must be a declared template owner")
            if not is_unique_nonempty_string_list(gate["required_evidence"]):
                fail(errors, f"{gate_prefix} required_evidence must be unique non-empty strings")
            elif not set(gate["required_evidence"]) <= evidence_set:
                fail(errors, f"{gate_prefix} required_evidence must be declared by the template")
            transition = gate["transition"]
            if not isinstance(transition, dict) or set(transition) != {"on_pass", "on_fail"}:
                fail(errors, f"{gate_prefix} transition must declare exactly on_pass and on_fail")
            else:
                if not isinstance(transition["on_pass"], str) or transition["on_pass"] not in stage_set | {"complete"}:
                    fail(errors, f"{gate_prefix} on_pass must enter a template stage or complete")
                if transition["on_fail"] != "escalation_required":
                    fail(errors, f"{gate_prefix} on_fail must fail closed to escalation_required")

        resume = entry["resume_reconciliation"]
        if not isinstance(resume, dict) or set(resume) != REQUIRED_RESUME_FIELDS:
            fail(errors, f"{prefix}: resume_reconciliation has an invalid schema")
        else:
            if resume["checkpoint_owner"] != owners.get("state"):
                fail(errors, f"{prefix}: resume checkpoint_owner must be the state owner")
            if resume["reconcile_before_resume"] is not True:
                fail(errors, f"{prefix}: resume must reconcile before resuming")
            if resume["on_unreconciled"] != "reconciliation_required":
                fail(errors, f"{prefix}: unreconciled resume must fail closed")
            if not is_unique_nonempty_string_list(resume["required_evidence"]):
                fail(errors, f"{prefix}: resume required_evidence must be unique non-empty strings")
            elif not set(resume["required_evidence"]) <= evidence_set:
                fail(errors, f"{prefix}: resume evidence must be declared by the template")

        reuse = entry["reuse_invalidation"]
        if not isinstance(reuse, dict) or set(reuse) != REQUIRED_REUSE_FIELDS:
            fail(errors, f"{prefix}: reuse_invalidation has an invalid schema")
        else:
            reuse_when = reuse["reuse_when"]
            invalidate_when = reuse["invalidate_when"]
            valid_reuse_when = is_unique_nonempty_string_list(reuse_when)
            valid_invalidate_when = is_unique_nonempty_string_list(invalidate_when)
            if not valid_reuse_when:
                fail(errors, f"{prefix}: reuse_when must be unique non-empty strings")
            if not valid_invalidate_when:
                fail(errors, f"{prefix}: invalidate_when must be unique non-empty strings")
            if valid_reuse_when and valid_invalidate_when and set(reuse_when) & set(invalidate_when):
                fail(errors, f"{prefix}: reuse and invalidation conditions must not overlap")
            if reuse["unaffected_evidence"] != "preserve":
                fail(errors, f"{prefix}: unaffected evidence must be preserved")
            if reuse["on_invalidation"] != "new_plan_revision":
                fail(errors, f"{prefix}: invalidation must require a new plan revision")

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


def selector_propagation_errors(
    registry: dict[str, Any],
    load_templates: Any,
    assess_template: Any,
) -> list[str]:
    """Prove the supplied loader and selector consume the supplied registry."""
    errors: list[str] = []
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
            propagated = load_templates(path)
        except Exception as exc:
            fail(errors, f"synthetic registry template did not propagate through loader: {exc}")
        else:
            if synthetic_id not in propagated.get("templates", {}):
                fail(errors, "synthetic registry template did not appear through shared loader")
            else:
                facts = {
                    **propagated["templates"][synthetic_id]["applicability"],
                    **{
                        field: False
                        for field in propagated["templates"][synthetic_id]["exclusion_facts"]
                    },
                    "external_side_effect": False,
                    "authority_or_state": False,
                    "sensitive_or_privileged": False,
                    "platform_or_compatibility": False,
                    "irreversible_or_unreconciled": False,
                    "outside_verified_envelope": False,
                }
                try:
                    resolution = assess_template(synthetic_id, facts, propagated)
                except Exception as exc:
                    fail(errors, f"synthetic registry template was unreachable from selector: {exc}")
                else:
                    if resolution.get("status") != "selected":
                        fail(errors, "synthetic registry template did not select through shared selector")
    return errors


def fixture_load_templates(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_driven_fixture_selector(
    template_id: str, facts: dict[str, Any], registry: dict[str, Any]
) -> dict[str, str]:
    template = registry.get("templates", {}).get(template_id)
    if template is None or template.get("status") != "implemented":
        return {"status": "unsupported"}
    if any(facts.get(key) != value for key, value in template["applicability"].items()):
        return {"status": "escalation_required"}
    return {"status": "selected"}


def copied_fixture_selector(
    template_id: str, facts: dict[str, Any], registry: dict[str, Any]
) -> dict[str, str]:
    """Deliberate stale mapping mutation: it ignores a new registry entry."""
    copied_ids = frozenset(IMPLEMENTED_TEMPLATE_IDS)
    if template_id not in copied_ids:
        return {"status": "unsupported"}
    return registry_driven_fixture_selector(template_id, facts, registry)


def run_negative_drift_proof(registry: dict[str, Any]) -> None:
    """Prove this validator rejects the exact copied-selector regression."""
    correct_errors = selector_propagation_errors(
        registry,
        fixture_load_templates,
        registry_driven_fixture_selector,
    )
    if correct_errors:
        raise AssertionError(f"registry-driven selector fixture failed: {correct_errors!r}")
    copied_errors = selector_propagation_errors(
        registry,
        fixture_load_templates,
        copied_fixture_selector,
    )
    if not any("did not select through shared selector" in error for error in copied_errors):
        raise AssertionError("copied selector mutation was accepted")


def run_contract_mutations(registry: dict[str, Any]) -> list[str]:
    """Exercise the future shared contract with the same anti-drift proof."""
    errors: list[str] = []
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    try:
        contract = importlib.import_module("lifecycle_template_contract")
    except Exception as exc:  # pragma: no cover - guarded by the RED prerequisite
        return [f"cannot load shared lifecycle template contract: {exc}"]
    for name in ("load_templates", "assess_template", "compose_templates"):
        if not callable(getattr(contract, name, None)):
            fail(errors, f"shared lifecycle template contract is missing {name}()")
    if errors:
        return errors
    if getattr(contract, "LEVELS", None) is not LEVELS:
        fail(errors, "shared lifecycle template contract does not use canonical assurance LEVELS")
        return errors
    try:
        loaded = contract.load_templates(REGISTRY_PATH)
    except Exception as exc:
        return [f"shared lifecycle template contract cannot load registry: {exc}"]
    if loaded != registry:
        fail(errors, "shared lifecycle template loader changed authoritative registry content")
    errors.extend(loader_lifecycle_structure_errors(registry, contract.load_templates))
    errors.extend(selector_contract_errors(registry, contract.assess_template))
    errors.extend(composition_contract_errors(registry, contract.compose_templates))
    return errors + selector_propagation_errors(
        registry,
        contract.load_templates,
        contract.assess_template,
    )


def composition_contract_errors(registry: dict[str, Any], compose_templates: Any) -> list[str]:
    """Exercise deterministic composition and every fail-closed boundary."""
    errors: list[str] = []
    templates = registry["templates"]
    base_id = "bounded-feature"
    overlay_id = "skill-evolution"
    facts = {
        **selection_facts(templates[base_id]),
        **selection_facts(templates[overlay_id]),
    }

    unsupported_cases = (
        ("unknown-template", [], "base:template_unknown"),
        ("release", [], "base:template_deferred"),
        (base_id, ["unknown-template"], "overlay:unknown-template:template_unknown"),
        (base_id, ["release"], "overlay:release:template_deferred"),
    )
    for requested_base, overlays, reason in unsupported_cases:
        result = compose_templates(requested_base, overlays, facts, registry)
        if result.get("status") != "unsupported" or reason not in result.get("reasons", []):
            fail(errors, f"composition did not reject unsupported request {requested_base!r}/{overlays!r}")

    duplicate = compose_templates(base_id, [overlay_id, overlay_id], facts, registry)
    if duplicate.get("status") != "conflict" or duplicate.get("reasons") != [
        f"overlay_duplicate:{overlay_id}"
    ]:
        fail(errors, "composition accepted a duplicated overlay")

    repeated_base = compose_templates(base_id, [base_id], facts, registry)
    if repeated_base.get("status") != "conflict" or repeated_base.get("reasons") != [
        f"overlay_duplicates_base:{base_id}"
    ]:
        fail(errors, "composition accepted its base as an overlay")

    incompatible = compose_templates("lightweight-change", [overlay_id], facts, registry)
    if incompatible.get("status") != "conflict" or incompatible.get("reasons") != [
        f"overlay_incompatible:lightweight-change:{overlay_id}"
    ]:
        fail(errors, "composition accepted an undeclared overlay")

    owner_conflict = compose_templates(base_id, [overlay_id], facts, registry)
    if owner_conflict.get("status") != "conflict" or not any(
        reason.startswith("owner_conflict:") for reason in owner_conflict.get("reasons", [])
    ):
        fail(errors, "composition accepted conflicting scalar owners")
    owner_keyset_registry = copy.deepcopy(registry)
    owner_keyset_registry["templates"][base_id]["owners"]["undeclared"] = "shadow-owner"
    try:
        compose_templates(base_id, [], facts, owner_keyset_registry)
    except ValueError:
        pass
    except Exception as exc:
        fail(errors, f"owner-keyset drift did not fail closed as ValueError: {exc}")
    else:
        fail(errors, "composition accepted a differing owner keyset")

    escalated_facts = {**facts, "outside_verified_envelope": True}
    escalated = compose_templates(base_id, [], escalated_facts, registry)
    if escalated.get("status") != "escalation_required" or (
        "base:delta:outside_verified_envelope:true" not in escalated.get("reasons", [])
    ):
        fail(errors, "composition normalized a true bounded delta to selected")

    compatible = copy.deepcopy(registry)
    base_owners = copy.deepcopy(compatible["templates"][base_id]["owners"])
    compatible_overlay = compatible["templates"][overlay_id]
    compatible_overlay["owners"] = base_owners
    for gate in compatible_overlay["gates"]:
        gate["owner"] = base_owners["policy"]
    if registry_errors(compatible):
        fail(errors, "validator fixture could not express a compatible owner overlay")
        return errors

    selected = compose_templates(base_id, [overlay_id], facts, compatible)
    repeated = compose_templates(base_id, [overlay_id], facts, compatible)
    if selected != repeated:
        fail(errors, "composition was not deterministic for identical normalized input")
    if selected.get("status") != "selected":
        fail(errors, "declared compatible overlay did not compose")
        return errors
    if selected.get("template_ids") != [base_id, overlay_id]:
        fail(errors, "composition did not retain base-first template IDs")
    if selected.get("composition_order") != [base_id, overlay_id]:
        fail(errors, "composition did not persist its deterministic order")
    if selected.get("contract_versions") != {base_id: 1, overlay_id: 1}:
        fail(errors, "composition did not retain every template contract version")
    expected_stages = list(dict.fromkeys(templates[base_id]["stages"] + templates[overlay_id]["stages"]))
    if selected.get("resolved_stages") != expected_stages:
        fail(errors, "composition did not merge stages in precedence order")
    expected_evidence = list(
        dict.fromkeys(
            templates[base_id]["required_evidence"] + templates[overlay_id]["required_evidence"]
        )
    )
    if selected.get("resolved_required_evidence") != expected_evidence:
        fail(errors, "composition dropped or reordered required evidence")
    if selected.get("resolved_owners") != base_owners:
        fail(errors, "composition did not resolve owners deterministically")
    if selected.get("resolved_review_level") != "L2_SINGLE_FAMILY_QUAD":
        fail(errors, "composition weakened the strongest review level")
    if {gate.get("gate_id") for gate in selected.get("resolved_gates", [])} != {
        gate["gate_id"]
        for template_id in (base_id, overlay_id)
        for gate in templates[template_id]["gates"]
    }:
        fail(errors, "composition dropped a required gate")
    delta_hash = selected.get("delta_evidence_hash")
    if not isinstance(delta_hash, str) or len(delta_hash) != 64:
        fail(errors, "composition did not produce a deterministic delta evidence hash")
    if selected.get("resolution_schema_version") != 1:
        fail(errors, "composition did not version its selected-resolution contract")
    if selected.get("resolution_provenance") != "lifecycle_template_contract.compose_templates":
        fail(errors, "composition did not identify its selected-resolution provenance")
    integrity_hash = selected.get("resolution_integrity_hash")
    if not isinstance(integrity_hash, str) or len(integrity_hash) != 64:
        fail(errors, "composition did not seal its selected resolution")

    gate_conflict_registry = copy.deepcopy(compatible)
    conflicting_gate = gate_conflict_registry["templates"][overlay_id]["gates"][0]
    conflicting_gate["gate_id"] = "verification"
    conflicting_gate["owner"] = base_owners["evidence"]
    gate_conflict = compose_templates(base_id, [overlay_id], facts, gate_conflict_registry)
    if gate_conflict.get("status") != "conflict" or (
        "gate_transition_conflict:verification" not in gate_conflict.get("reasons", [])
    ):
        fail(errors, "composition accepted conflicting gate completion semantics")
    return errors


def selection_facts(template: dict[str, Any]) -> dict[str, Any]:
    """Return the smallest hand-derived fact record for an exact match."""
    return {
        **template["applicability"],
        **{field: False for field in template.get("exclusion_facts", {})},
        **{field: False for field in DELTA_FIELDS},
    }


def loader_lifecycle_structure_errors(registry: dict[str, Any], load_templates: Any) -> list[str]:
    """Prove the shared loader rejects structurally weak implemented entries."""
    errors: list[str] = []
    mutations = {
        "empty applicability": lambda value: value["templates"]["lightweight-change"].__setitem__(
            "applicability", {}
        ),
        "empty exclusions": lambda value: value["templates"]["lightweight-change"].__setitem__(
            "exclusions", []
        ),
        "missing typed exclusion facts": lambda value: value["templates"]["lightweight-change"].pop(
            "exclusion_facts"
        ),
        "missing lifecycle stages": lambda value: value["templates"]["lightweight-change"].pop(
            "stages"
        ),
        "missing owner": lambda value: value["templates"]["lightweight-change"]["owners"].pop(
            "lifecycle_plan"
        ),
        "extra owner key": lambda value: value["templates"]["lightweight-change"]["owners"].__setitem__(
            "undeclared", "shadow-owner"
        ),
        "missing gate evidence": lambda value: value["templates"]["lightweight-change"]["gates"][
            0
        ].pop("required_evidence"),
        "weakened resume reconciliation": lambda value: value["templates"]["lightweight-change"][
            "resume_reconciliation"
        ].__setitem__("reconcile_before_resume", False),
        "weakened reuse invalidation": lambda value: value["templates"]["lightweight-change"][
            "reuse_invalidation"
        ].__setitem__("on_invalidation", "ignore"),
        "unknown review level": lambda value: value["templates"]["lightweight-change"].__setitem__(
            "review_level", "L9_UNKNOWN"
        ),
    }
    for label, mutate in mutations.items():
        altered = copy.deepcopy(registry)
        mutate(altered)
        with tempfile.TemporaryDirectory(prefix="cloudbox-lifecycle-template-load-") as temp_name:
            path = Path(temp_name) / "lifecycle-templates.json"
            path.write_text(json.dumps(altered), encoding="utf-8")
            try:
                load_templates(path)
            except ValueError:
                continue
            except Exception as exc:
                fail(errors, f"shared lifecycle template loader had unexpected {label} failure: {exc}")
            else:
                fail(errors, f"shared lifecycle template loader accepted {label}")
    return errors


def selector_contract_errors(registry: dict[str, Any], assess_template: Any) -> list[str]:
    """Exercise direct selection and fail-closed bounded-delta behavior."""
    errors: list[str] = []
    templates = registry["templates"]

    for template_id in sorted(IMPLEMENTED_TEMPLATE_IDS):
        template = templates[template_id]
        resolution = assess_template(template_id, selection_facts(template), registry)
        if resolution.get("status") != "selected":
            fail(errors, f"implemented template {template_id!r} did not select on its exact applicability facts")
            continue
        if resolution.get("template_id") != template_id:
            fail(errors, f"selected template {template_id!r} did not retain its exact template ID")
        if resolution.get("contract_version") != template["contract_version"]:
            fail(errors, f"selected template {template_id!r} did not retain its contract version")
        if resolution.get("full_risk_calculation_required") is not False:
            fail(errors, f"selected template {template_id!r} required a full risk calculation")
        if resolution.get("reasons") != []:
            fail(errors, f"selected template {template_id!r} had unexpected reasons")
        if resolution.get("matched_conditions") != template["applicability"]:
            fail(errors, f"selected template {template_id!r} did not record exact matched applicability")
        if resolution.get("delta_answers") != {field: False for field in DELTA_FIELDS}:
            fail(errors, f"selected template {template_id!r} did not record the all-false bounded delta")
        exclusion_facts = template.get("exclusion_facts")
        if not isinstance(exclusion_facts, dict) or not exclusion_facts:
            fail(errors, f"selected template {template_id!r} has no typed exclusion-fact mapping")
        else:
            expected_exclusion_answers = {field: False for field in exclusion_facts}
            if resolution.get("exclusion_answers") != expected_exclusion_answers:
                fail(
                    errors,
                    f"selected template {template_id!r} did not record all explicit exclusion answers",
                )

    for template_id in sorted(DEFERRED_TEMPLATE_IDS):
        resolution = assess_template(template_id, {}, registry)
        if resolution.get("status") != "unsupported":
            fail(errors, f"deferred template {template_id!r} did not return unsupported")
        if resolution.get("reasons") != ["template_deferred"]:
            fail(errors, f"deferred template {template_id!r} did not report template_deferred")
        if resolution.get("full_risk_calculation_required") is not True:
            fail(errors, f"deferred template {template_id!r} did not require full risk calculation")

    unknown = assess_template("unknown-template", {}, registry)
    if unknown.get("status") != "unsupported":
        fail(errors, "unknown template selected through a default fallback")
    if unknown.get("reasons") != ["template_unknown"]:
        fail(errors, "unknown template did not report template_unknown")
    if unknown.get("full_risk_calculation_required") is not True:
        fail(errors, "unknown template did not require full risk calculation")

    template_id = "lightweight-change"
    base_facts = selection_facts(templates[template_id])
    for field in DELTA_FIELDS:
        true_facts = {**base_facts, field: True}
        true_result = assess_template(template_id, true_facts, registry)
        expected_true_reason = f"delta:{field}:true"
        if (
            true_result.get("status") != "escalation_required"
            or true_result.get("reasons") != [expected_true_reason]
            or true_result.get("full_risk_calculation_required") is not True
        ):
            fail(errors, f"true delta {field!r} did not fail closed with {expected_true_reason!r}")

        missing_facts = dict(base_facts)
        del missing_facts[field]
        missing_result = assess_template(template_id, missing_facts, registry)
        expected_unknown_reason = f"delta:{field}:missing_or_unknown"
        if (
            missing_result.get("status") != "escalation_required"
            or missing_result.get("reasons") != [expected_unknown_reason]
            or missing_result.get("full_risk_calculation_required") is not True
        ):
            fail(errors, f"missing delta {field!r} did not fail closed with {expected_unknown_reason!r}")

        unknown_result = assess_template(template_id, {**base_facts, field: "unknown"}, registry)
        if (
            unknown_result.get("status") != "escalation_required"
            or unknown_result.get("reasons") != [expected_unknown_reason]
            or unknown_result.get("full_risk_calculation_required") is not True
        ):
            fail(errors, f"unknown delta {field!r} did not fail closed with {expected_unknown_reason!r}")

    mismatched = assess_template(template_id, {**base_facts, "scope": "bounded"}, registry)
    if (
        mismatched.get("status") != "escalation_required"
        or mismatched.get("reasons") != ["applicability:scope:mismatch"]
        or mismatched.get("full_risk_calculation_required") is not True
    ):
        fail(errors, "positive applicability mismatch did not fail closed")

    exclusion_facts = templates[template_id].get("exclusion_facts", {})
    material_change = "material_semantic_change"
    if material_change not in exclusion_facts:
        fail(errors, "lightweight-change does not map material_semantic_change to a registry exclusion")
        return errors
    legacy_exclusion = assess_template(
        template_id,
        {**base_facts, "triggered_exclusions": [templates[template_id]["exclusions"][0]]},
        registry,
    )
    if (
        legacy_exclusion.get("status") != "escalation_required"
        or legacy_exclusion.get("reasons") != ["legacy_triggered_exclusions_unsupported"]
        or legacy_exclusion.get("full_risk_calculation_required") is not True
    ):
        fail(errors, "legacy caller-precomputed exclusions did not fail closed")
    for implemented_id in sorted(IMPLEMENTED_TEMPLATE_IDS):
        implemented_template = templates[implemented_id]
        implemented_facts = selection_facts(implemented_template)
        for exclusion_fact, definition in sorted(implemented_template["exclusion_facts"].items()):
            if not isinstance(definition, dict) or not isinstance(definition.get("condition"), str):
                fail(errors, f"typed exclusion fact {implemented_id}/{exclusion_fact} has no condition")
                continue
            condition = definition["condition"]
            excluded = assess_template(
                implemented_id,
                {**implemented_facts, exclusion_fact: True},
                registry,
            )
            if (
                excluded.get("status") != "escalation_required"
                or excluded.get("matched_exclusions") != [condition]
                or excluded.get("reasons") != [f"exclusion:{condition}"]
                or excluded.get("full_risk_calculation_required") is not True
            ):
                fail(errors, f"true typed exclusion fact {implemented_id}/{exclusion_fact} did not fail closed")
            missing_exclusion_facts = dict(implemented_facts)
            del missing_exclusion_facts[exclusion_fact]
            expected_reason = f"exclusion_fact:{exclusion_fact}:missing_or_unknown"
            missing_exclusion = assess_template(
                implemented_id,
                missing_exclusion_facts,
                registry,
            )
            if (
                missing_exclusion.get("status") != "escalation_required"
                or missing_exclusion.get("reasons") != [expected_reason]
                or missing_exclusion.get("full_risk_calculation_required") is not True
            ):
                fail(
                    errors,
                    f"missing typed exclusion fact {implemented_id}/{exclusion_fact} did not fail closed",
                )
            for invalid_value in (None, "unknown", 1):
                unknown_exclusion = assess_template(
                    implemented_id,
                    {**implemented_facts, exclusion_fact: invalid_value},
                    registry,
                )
                if (
                    unknown_exclusion.get("status") != "escalation_required"
                    or unknown_exclusion.get("reasons") != [expected_reason]
                    or unknown_exclusion.get("full_risk_calculation_required") is not True
                ):
                    fail(
                        errors,
                        f"unknown typed exclusion fact {implemented_id}/{exclusion_fact} did not fail closed",
                    )
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

    if registry is not None and not registry_errors(registry):
        run_negative_drift_proof(registry)

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
        gate_owner_removed = copy.deepcopy(registry)
        del gate_owner_removed["templates"]["lightweight-change"]["gates"][0]["owner"]
        mutation_must_fail(gate_owner_removed, "gate owner removed")
        gate_evidence_removed = copy.deepcopy(registry)
        del gate_evidence_removed["templates"]["lightweight-change"]["gates"][0]["required_evidence"]
        mutation_must_fail(gate_evidence_removed, "gate evidence removed")
        gate_transition_weakened = copy.deepcopy(registry)
        gate_transition_weakened["templates"]["lightweight-change"]["gates"][0]["transition"]["on_fail"] = "complete"
        mutation_must_fail(gate_transition_weakened, "gate failure transition weakened")
        duplicate_stage = copy.deepcopy(registry)
        duplicate_stage["templates"]["skill-evolution"]["stages"][3] = "verify_red"
        mutation_must_fail(duplicate_stage, "duplicate stage identity accepted")
        ambiguous_stage_target = copy.deepcopy(registry)
        ambiguous_stage_target["templates"]["skill-evolution"]["gates"][0]["transition"]["on_pass"] = "verify"
        mutation_must_fail(ambiguous_stage_target, "ambiguous stage target accepted")
        resume_reconciliation_removed = copy.deepcopy(registry)
        resume_reconciliation_removed["templates"]["bounded-feature"]["resume_reconciliation"]["reconcile_before_resume"] = False
        mutation_must_fail(resume_reconciliation_removed, "resume reconciliation weakened")
        invalidation_weakened = copy.deepcopy(registry)
        invalidation_weakened["templates"]["skill-evolution"]["reuse_invalidation"]["on_invalidation"] = "ignore"
        mutation_must_fail(invalidation_weakened, "reuse invalidation weakened")
        deferred_reclassified = copy.deepcopy(registry)
        deferred_reclassified["templates"]["release"]["status"] = "implemented"
        mutation_must_fail(deferred_reclassified, "deferred status removed")
        exclusion_type_weakened = copy.deepcopy(registry)
        exclusion_type_weakened["templates"]["lightweight-change"]["exclusion_facts"][
            "material_semantic_change"
        ]["type"] = "string"
        mutation_must_fail(exclusion_type_weakened, "typed exclusion fact weakened")
        exclusion_mapping_weakened = copy.deepcopy(registry)
        exclusion_mapping_weakened["templates"]["lightweight-change"]["exclusion_facts"][
            "material_semantic_change"
        ]["condition"] = "not a declared exclusion"
        mutation_must_fail(exclusion_mapping_weakened, "typed exclusion mapping disconnected")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("Validated authoritative lifecycle template registry and shared-consumer propagation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
