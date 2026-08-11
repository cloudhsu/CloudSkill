"""Pure, deterministic selection and composition for lifecycle templates.

This module only turns explicit task facts and the versioned registry into an
evidence record.  It does not execute work, persist state, or invoke models.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from review_assurance_contract import LEVELS


DELTA_FIELDS = (
    "external_side_effect",
    "authority_or_state",
    "sensitive_or_privileged",
    "platform_or_compatibility",
    "irreversible_or_unreconciled",
    "outside_verified_envelope",
)
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
REQUIRED_OWNER_KEYS = {"lifecycle_plan", "state", "policy", "action", "evidence"}
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
RESOLUTION_PROVENANCE = "lifecycle_template_contract.compose_templates"


def load_templates(path: Path) -> dict[str, Any]:
    """Load one registry without adding defaults or changing its contents."""
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load lifecycle template registry: {exc}") from exc
    _validate_registry(registry)
    return registry


def assess_template(
    template_id: str, facts: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any]:
    """Return the fail-closed selection evidence for one requested template.

    All six bounded-delta answers must be literal booleans before a template can
    use the fast path.  Missing and non-boolean values are recorded as unknown,
    never normalized to safe.
    """
    _validate_registry(registry)
    normalized_facts = _normalize_facts(facts)
    templates = registry["templates"]
    template = templates.get(template_id)
    if template is None:
        return _result(
            template_id=template_id,
            contract_version=None,
            status="unsupported",
            delta_answers=_delta_answers(normalized_facts),
            reasons=["template_unknown"],
        )

    contract_version = template["contract_version"]
    if template["status"] == "deferred":
        return _result(
            template_id=template_id,
            contract_version=contract_version,
            status="unsupported",
            delta_answers=_delta_answers(normalized_facts),
            reasons=["template_deferred"],
        )

    matched_conditions, applicability_reasons = _assess_applicability(
        normalized_facts, template["applicability"]
    )
    exclusion_answers, matched_exclusions, exclusion_reasons = _assess_exclusions(
        normalized_facts, template["exclusion_facts"]
    )
    delta_answers = _delta_answers(normalized_facts)
    delta_reasons = _delta_reasons(delta_answers)
    legacy_exclusion_reasons = (
        ["legacy_triggered_exclusions_unsupported"]
        if "triggered_exclusions" in normalized_facts
        else []
    )
    reasons = applicability_reasons + legacy_exclusion_reasons + exclusion_reasons + delta_reasons
    if reasons:
        return _result(
            template_id=template_id,
            contract_version=contract_version,
            status="escalation_required",
            matched_conditions=matched_conditions,
            matched_exclusions=matched_exclusions,
            exclusion_answers=exclusion_answers,
            delta_answers=delta_answers,
            reasons=reasons,
        )
    return _result(
        template_id=template_id,
        contract_version=contract_version,
        status="selected",
        matched_conditions=matched_conditions,
        matched_exclusions=matched_exclusions,
        exclusion_answers=exclusion_answers,
        delta_answers=delta_answers,
        reasons=[],
    )


def compose_templates(
    base_id: str,
    overlay_ids: list[str],
    facts: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    """Resolve one base and declared overlays without weakening constraints."""
    _validate_registry(registry)
    if not isinstance(base_id, str) or not base_id:
        return _composition_result("unsupported", [], {}, ["base:template_unknown"])
    if not isinstance(overlay_ids, list) or any(
        not isinstance(template_id, str) or not template_id for template_id in overlay_ids
    ):
        return _composition_result("conflict", [base_id], {}, ["overlay_ids_invalid"])

    duplicate = next(
        (template_id for template_id in overlay_ids if overlay_ids.count(template_id) > 1),
        None,
    )
    if duplicate is not None:
        return _composition_result(
            "conflict", [base_id, *overlay_ids], {}, [f"overlay_duplicate:{duplicate}"]
        )
    if base_id in overlay_ids:
        return _composition_result(
            "conflict",
            [base_id, *overlay_ids],
            {},
            [f"overlay_duplicates_base:{base_id}"],
        )

    template_ids = [base_id, *overlay_ids]
    assessments: dict[str, dict[str, Any]] = {}
    unsupported_reasons: list[str] = []
    escalation_reasons: list[str] = []
    for index, template_id in enumerate(template_ids):
        assessment = assess_template(template_id, facts, registry)
        assessments[template_id] = assessment
        prefix = "base" if index == 0 else f"overlay:{template_id}"
        if assessment["status"] == "unsupported":
            unsupported_reasons.extend(f"{prefix}:{reason}" for reason in assessment["reasons"])
        elif assessment["status"] == "escalation_required":
            escalation_reasons.extend(f"{prefix}:{reason}" for reason in assessment["reasons"])
    contract_versions = {
        template_id: assessments[template_id]["contract_version"] for template_id in template_ids
    }
    if unsupported_reasons:
        return _composition_result(
            "unsupported", template_ids, contract_versions, unsupported_reasons, assessments
        )

    templates = registry["templates"]
    base = templates[base_id]
    incompatible = [
        overlay_id
        for overlay_id in overlay_ids
        if overlay_id not in base["compatible_overlays"]
    ]
    if incompatible:
        return _composition_result(
            "conflict",
            template_ids,
            contract_versions,
            [f"overlay_incompatible:{base_id}:{overlay_id}" for overlay_id in incompatible],
            assessments,
        )
    if escalation_reasons:
        return _composition_result(
            "escalation_required",
            template_ids,
            contract_versions,
            escalation_reasons,
            assessments,
        )

    owner_conflicts = _owner_conflicts(template_ids, templates)
    gate_conflicts, resolved_gates = _resolve_gates(template_ids, templates)
    scalar_conflicts = _completion_scalar_conflicts(template_ids, templates)
    conflicts = owner_conflicts + gate_conflicts + scalar_conflicts
    if conflicts:
        return _composition_result(
            "conflict", template_ids, contract_versions, conflicts, assessments
        )

    resolved_stages = _merge_template_lists(template_ids, templates, "stages")
    resolved_evidence = _merge_template_lists(template_ids, templates, "required_evidence")
    review_level = max(
        (templates[template_id]["review_level"] for template_id in template_ids),
        key=LEVELS.index,
    )
    delta_evidence = {
        "composition_order": template_ids,
        "contract_versions": contract_versions,
        "templates": {
            template_id: {
                "matched_conditions": assessments[template_id]["matched_conditions"],
                "matched_exclusions": assessments[template_id]["matched_exclusions"],
                "exclusion_answers": assessments[template_id]["exclusion_answers"],
                "delta_answers": assessments[template_id]["delta_answers"],
            }
            for template_id in template_ids
        },
    }
    delta_evidence_hash = _canonical_hash(delta_evidence)
    result = _composition_result(
        "selected", template_ids, contract_versions, [], assessments
    )
    result.update(
        {
            "delta_evidence_hash": delta_evidence_hash,
            "resolved_owners": copy.deepcopy(base["owners"]),
            "resolved_required_evidence": resolved_evidence,
            "resolved_stages": resolved_stages,
            "resolved_gates": resolved_gates,
            "resolved_review_level": review_level,
            "resolved_resume_reconciliation": _resolve_resume(template_ids, templates),
            "resolved_reuse_invalidation": _resolve_reuse(template_ids, templates),
            "resolution_schema_version": 1,
            "resolution_provenance": RESOLUTION_PROVENANCE,
        }
    )
    result["resolution_integrity_hash"] = _canonical_hash(result)
    return result


def validate_selected_resolution(resolution: Any) -> None:
    """Reject unsealed, relabeled, or mutated composition output."""
    if not isinstance(resolution, dict):
        raise ValueError("plan requires composer-selected resolution provenance and integrity")
    integrity_hash = resolution.get("resolution_integrity_hash")
    payload = {
        key: copy.deepcopy(value)
        for key, value in resolution.items()
        if key != "resolution_integrity_hash"
    }
    required = {
        "status",
        "template_ids",
        "contract_versions",
        "composition_order",
        "assessments",
        "reasons",
        "full_risk_calculation_required",
        "delta_evidence_hash",
        "resolved_owners",
        "resolved_required_evidence",
        "resolved_stages",
        "resolved_gates",
        "resolved_review_level",
        "resolved_resume_reconciliation",
        "resolved_reuse_invalidation",
        "resolution_schema_version",
        "resolution_provenance",
    }
    template_ids = resolution.get("template_ids")
    versions = resolution.get("contract_versions")
    assessments = resolution.get("assessments")
    if (
        not required <= set(resolution)
        or resolution.get("status") != "selected"
        or resolution.get("full_risk_calculation_required") is not False
        or resolution.get("reasons") != []
        or resolution.get("resolution_schema_version") != 1
        or resolution.get("resolution_provenance") != RESOLUTION_PROVENANCE
        or not _is_hash(integrity_hash)
        or integrity_hash != _canonical_hash(payload)
        or not isinstance(template_ids, list)
        or not template_ids
        or any(not isinstance(value, str) or not value for value in template_ids)
        or len(template_ids) != len(set(template_ids))
        or resolution.get("composition_order") != template_ids
        or not isinstance(versions, dict)
        or set(versions) != set(template_ids)
        or any(type(value) is not int or value < 1 for value in versions.values())
        or not isinstance(assessments, dict)
        or set(assessments) != set(template_ids)
        or any(
            not isinstance(assessment, dict) or assessment.get("status") != "selected"
            for assessment in assessments.values()
        )
        or not _is_hash(resolution.get("delta_evidence_hash"))
        or resolution.get("resolved_review_level") not in LEVELS
    ):
        raise ValueError("plan requires composer-selected resolution provenance and integrity")


def _composition_result(
    status: str,
    template_ids: list[str],
    contract_versions: dict[str, int | None],
    reasons: list[str],
    assessments: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "template_ids": copy.deepcopy(template_ids),
        "contract_versions": copy.deepcopy(contract_versions),
        "composition_order": copy.deepcopy(template_ids),
        "assessments": copy.deepcopy(assessments or {}),
        "reasons": reasons,
        "full_risk_calculation_required": status != "selected",
    }


def _owner_conflicts(
    template_ids: list[str], templates: dict[str, dict[str, Any]]
) -> list[str]:
    base_owners = templates[template_ids[0]]["owners"]
    return [
        f"owner_conflict:{owner}:{template_ids[0]}:{overlay_id}"
        for overlay_id in template_ids[1:]
        for owner in base_owners
        if templates[overlay_id]["owners"][owner] != base_owners[owner]
    ]


def _resolve_gates(
    template_ids: list[str], templates: dict[str, dict[str, Any]]
) -> tuple[list[str], list[dict[str, Any]]]:
    conflicts: list[str] = []
    resolved: list[dict[str, Any]] = []
    positions: dict[str, int] = {}
    for template_id in template_ids:
        for gate in templates[template_id]["gates"]:
            gate_id = gate["gate_id"]
            if gate_id not in positions:
                positions[gate_id] = len(resolved)
                resolved.append(copy.deepcopy(gate))
                continue
            current = resolved[positions[gate_id]]
            if current["owner"] != gate["owner"]:
                conflicts.append(f"gate_owner_conflict:{gate_id}")
                continue
            if current["transition"] != gate["transition"]:
                conflicts.append(f"gate_transition_conflict:{gate_id}")
                continue
            current["required_evidence"] = list(
                dict.fromkeys(current["required_evidence"] + gate["required_evidence"])
            )
    return conflicts, resolved


def _completion_scalar_conflicts(
    template_ids: list[str], templates: dict[str, dict[str, Any]]
) -> list[str]:
    conflicts: list[str] = []
    checks = (
        ("resume_reconciliation", "checkpoint_owner"),
        ("resume_reconciliation", "reconcile_before_resume"),
        ("resume_reconciliation", "on_unreconciled"),
        ("reuse_invalidation", "unaffected_evidence"),
        ("reuse_invalidation", "on_invalidation"),
    )
    for section, key in checks:
        expected = templates[template_ids[0]][section][key]
        for overlay_id in template_ids[1:]:
            if templates[overlay_id][section][key] != expected:
                conflicts.append(f"completion_semantics_conflict:{section}:{key}:{overlay_id}")
    return conflicts


def _merge_template_lists(
    template_ids: list[str], templates: dict[str, dict[str, Any]], key: str
) -> list[Any]:
    return list(
        dict.fromkeys(
            item
            for template_id in template_ids
            for item in templates[template_id][key]
        )
    )


def _resolve_resume(
    template_ids: list[str], templates: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    resolved = copy.deepcopy(templates[template_ids[0]]["resume_reconciliation"])
    resolved["required_evidence"] = list(
        dict.fromkeys(
            evidence
            for template_id in template_ids
            for evidence in templates[template_id]["resume_reconciliation"]["required_evidence"]
        )
    )
    return resolved


def _resolve_reuse(
    template_ids: list[str], templates: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    resolved = copy.deepcopy(templates[template_ids[0]]["reuse_invalidation"])
    for key in ("reuse_when", "invalidate_when"):
        resolved[key] = list(
            dict.fromkeys(
                condition
                for template_id in template_ids
                for condition in templates[template_id]["reuse_invalidation"][key]
            )
        )
    return resolved


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _is_hash(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_registry(registry: Any) -> None:
    if not isinstance(registry, dict) or type(registry.get("schema_version")) is not int or registry.get("schema_version") != 1:
        _invalid_registry()
    templates = registry.get("templates")
    if not isinstance(templates, dict) or not templates:
        _invalid_registry()
    for template_id, template in templates.items():
        if not isinstance(template_id, str) or not template_id or not isinstance(template, dict):
            _invalid_registry()
        if template.get("template_id") != template_id:
            _invalid_registry()
        if type(template.get("contract_version")) is not int or template.get("contract_version") != 1:
            _invalid_registry()
        status = template.get("status")
        if status not in {"implemented", "deferred"}:
            _invalid_registry()
        if status == "deferred":
            _validate_deferred_template(template)
        else:
            _validate_implemented_template(template)


def _validate_deferred_template(template: dict[str, Any]) -> None:
    if not isinstance(template.get("deferred_reason"), str) or not template["deferred_reason"].strip():
        _invalid_registry()
    mechanics = REQUIRED_IMPLEMENTED_FIELDS - {"template_id", "status", "contract_version"}
    if mechanics & set(template):
        _invalid_registry()


def _validate_implemented_template(template: dict[str, Any]) -> None:
    if not REQUIRED_IMPLEMENTED_FIELDS <= set(template):
        _invalid_registry()
    applicability = template["applicability"]
    if not isinstance(applicability, dict) or not applicability:
        _invalid_registry()
    if any(not isinstance(key, str) or not key for key in applicability):
        _invalid_registry()

    exclusions = template["exclusions"]
    if not _is_unique_nonempty_string_list(exclusions):
        _invalid_registry()
    _validate_exclusion_facts(template["exclusion_facts"], exclusions)

    if not _is_unique_nonempty_string_list(template["stages"]):
        _invalid_registry()
    stages = set(template["stages"])
    if not _is_unique_nonempty_string_list(template["required_evidence"]):
        _invalid_registry()
    evidence = set(template["required_evidence"])
    if not _is_unique_nonempty_string_list(template["escalation_conditions"]):
        _invalid_registry()
    if not _is_unique_nonempty_string_list(template["compatible_overlays"], allow_empty=True):
        _invalid_registry()
    if template["review_level"] not in LEVELS:
        _invalid_registry()

    owners = template["owners"]
    if not isinstance(owners, dict) or set(owners) != REQUIRED_OWNER_KEYS:
        _invalid_registry()
    if any(not isinstance(value, str) or not value for value in owners.values()):
        _invalid_registry()
    if owners["lifecycle_plan"] != "development-process-tailoring":
        _invalid_registry()

    gates = template["gates"]
    if not isinstance(gates, list) or not gates:
        _invalid_registry()
    gate_ids: set[str] = set()
    for gate in gates:
        if not isinstance(gate, dict) or not REQUIRED_GATE_FIELDS <= set(gate):
            _invalid_registry()
        gate_id = gate["gate_id"]
        if not isinstance(gate_id, str) or not gate_id or gate_id in gate_ids:
            _invalid_registry()
        gate_ids.add(gate_id)
        if not isinstance(gate["owner"], str) or gate["owner"] not in set(owners.values()):
            _invalid_registry()
        if not _is_unique_nonempty_string_list(gate["required_evidence"]):
            _invalid_registry()
        if not set(gate["required_evidence"]) <= evidence:
            _invalid_registry()
        transition = gate["transition"]
        if not isinstance(transition, dict) or set(transition) != {"on_pass", "on_fail"}:
            _invalid_registry()
        if not isinstance(transition["on_pass"], str) or transition["on_pass"] not in stages | {"complete"}:
            _invalid_registry()
        if transition["on_fail"] != "escalation_required":
            _invalid_registry()

    resume = template["resume_reconciliation"]
    if not isinstance(resume, dict) or set(resume) != REQUIRED_RESUME_FIELDS:
        _invalid_registry()
    if (
        resume["checkpoint_owner"] != owners["state"]
        or resume["reconcile_before_resume"] is not True
        or resume["on_unreconciled"] != "reconciliation_required"
        or not _is_unique_nonempty_string_list(resume["required_evidence"])
        or not set(resume["required_evidence"]) <= evidence
    ):
        _invalid_registry()

    reuse = template["reuse_invalidation"]
    if not isinstance(reuse, dict) or set(reuse) != REQUIRED_REUSE_FIELDS:
        _invalid_registry()
    if not _is_unique_nonempty_string_list(reuse["reuse_when"]):
        _invalid_registry()
    if not _is_unique_nonempty_string_list(reuse["invalidate_when"]):
        _invalid_registry()
    if set(reuse["reuse_when"]) & set(reuse["invalidate_when"]):
        _invalid_registry()
    if reuse["unaffected_evidence"] != "preserve" or reuse["on_invalidation"] != "new_plan_revision":
        _invalid_registry()


def _validate_exclusion_facts(exclusion_facts: Any, exclusions: list[str]) -> None:
    if not isinstance(exclusion_facts, dict) or not exclusion_facts:
        _invalid_registry()
    conditions: list[str] = []
    for fact_name, definition in exclusion_facts.items():
        if not isinstance(fact_name, str) or not fact_name:
            _invalid_registry()
        if not isinstance(definition, dict) or set(definition) != {"type", "condition"}:
            _invalid_registry()
        if definition["type"] != "boolean":
            _invalid_registry()
        condition = definition["condition"]
        if not isinstance(condition, str) or condition not in exclusions:
            _invalid_registry()
        conditions.append(condition)
    if set(conditions) != set(exclusions) or len(conditions) != len(set(conditions)):
        _invalid_registry()


def _is_unique_nonempty_string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(isinstance(item, str) and item for item in value)
        and len(value) == len(set(value))
    )


def _invalid_registry() -> None:
    raise ValueError("invalid lifecycle template registry")


def _normalize_facts(facts: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(facts, dict):
        return {}
    return copy.deepcopy(facts)


def _assess_applicability(
    facts: dict[str, Any], applicability: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    matched: dict[str, Any] = {}
    reasons: list[str] = []
    for condition, expected in applicability.items():
        actual = facts.get(condition)
        if type(actual) is type(expected) and actual == expected:
            matched[condition] = expected
        else:
            reasons.append(f"applicability:{condition}:mismatch")
    return matched, reasons


def _assess_exclusions(
    facts: dict[str, Any], exclusion_facts: dict[str, dict[str, str]]
) -> tuple[dict[str, bool | None], list[str], list[str]]:
    """Require an explicit boolean answer for every registry-backed exclusion."""
    answers: dict[str, bool | None] = {}
    matched: list[str] = []
    reasons: list[str] = []
    for fact_name in sorted(exclusion_facts):
        value = facts.get(fact_name)
        answer = value if type(value) is bool else None
        answers[fact_name] = answer
        if answer is True:
            condition = exclusion_facts[fact_name]["condition"]
            matched.append(condition)
            reasons.append(f"exclusion:{condition}")
        elif answer is None:
            reasons.append(f"exclusion_fact:{fact_name}:missing_or_unknown")
    return answers, matched, reasons


def _delta_answers(facts: dict[str, Any]) -> dict[str, bool | None]:
    return {
        field: value if type(value) is bool else None
        for field in DELTA_FIELDS
        for value in [facts.get(field)]
    }


def _delta_reasons(delta_answers: dict[str, bool | None]) -> list[str]:
    reasons: list[str] = []
    for field in DELTA_FIELDS:
        value = delta_answers[field]
        if value is True:
            reasons.append(f"delta:{field}:true")
        elif value is not False:
            reasons.append(f"delta:{field}:missing_or_unknown")
    return reasons


def _result(
    *,
    template_id: str,
    contract_version: int | None,
    status: str,
    delta_answers: dict[str, bool | None],
    reasons: list[str],
    matched_conditions: dict[str, Any] | None = None,
    matched_exclusions: list[str] | None = None,
    exclusion_answers: dict[str, bool | None] | None = None,
) -> dict[str, Any]:
    return {
        "template_id": template_id,
        "contract_version": contract_version,
        "status": status,
        "matched_conditions": matched_conditions or {},
        "matched_exclusions": matched_exclusions or [],
        "exclusion_answers": exclusion_answers or {},
        "delta_answers": delta_answers,
        "reasons": reasons,
        "full_risk_calculation_required": status != "selected",
    }
