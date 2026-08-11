"""Pure, deterministic selection for the authoritative lifecycle templates.

This module only turns explicit task facts and the versioned registry into an
evidence record.  It does not execute work, persist state, or invoke models.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


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
    if not isinstance(template["review_level"], str) or not template["review_level"]:
        _invalid_registry()

    owners = template["owners"]
    if not isinstance(owners, dict) or not REQUIRED_OWNER_KEYS <= set(owners):
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
