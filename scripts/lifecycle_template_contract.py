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
    matched_exclusions = _matched_exclusions(normalized_facts, template["exclusions"])
    delta_answers = _delta_answers(normalized_facts)
    delta_reasons = _delta_reasons(delta_answers)
    reasons = applicability_reasons + [
        f"exclusion:{exclusion}" for exclusion in matched_exclusions
    ] + delta_reasons
    if reasons:
        return _result(
            template_id=template_id,
            contract_version=contract_version,
            status="escalation_required",
            matched_conditions=matched_conditions,
            matched_exclusions=matched_exclusions,
            delta_answers=delta_answers,
            reasons=reasons,
        )
    return _result(
        template_id=template_id,
        contract_version=contract_version,
        status="selected",
        matched_conditions=matched_conditions,
        matched_exclusions=matched_exclusions,
        delta_answers=delta_answers,
        reasons=[],
    )


def _validate_registry(registry: Any) -> None:
    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        raise ValueError("invalid lifecycle template registry")
    templates = registry.get("templates")
    if not isinstance(templates, dict):
        raise ValueError("invalid lifecycle template registry")
    for template_id, template in templates.items():
        if not isinstance(template_id, str) or not isinstance(template, dict):
            raise ValueError("invalid lifecycle template registry")
        if template.get("template_id") != template_id:
            raise ValueError("invalid lifecycle template registry")
        if not isinstance(template.get("contract_version"), int):
            raise ValueError("invalid lifecycle template registry")
        status = template.get("status")
        if status not in {"implemented", "deferred"}:
            raise ValueError("invalid lifecycle template registry")
        if status == "implemented":
            if not isinstance(template.get("applicability"), dict) or not isinstance(
                template.get("exclusions"), list
            ):
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


def _matched_exclusions(facts: dict[str, Any], exclusions: list[Any]) -> list[str]:
    """Return known registry exclusions explicitly reported by task facts."""
    triggered = facts.get("triggered_exclusions", [])
    if not isinstance(triggered, list):
        return []
    declared = {exclusion for exclusion in exclusions if isinstance(exclusion, str)}
    return sorted(
        {
            exclusion
            for exclusion in triggered
            if isinstance(exclusion, str) and exclusion in declared
        }
    )


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
) -> dict[str, Any]:
    return {
        "template_id": template_id,
        "contract_version": contract_version,
        "status": status,
        "matched_conditions": matched_conditions or {},
        "matched_exclusions": matched_exclusions or [],
        "delta_answers": delta_answers,
        "reasons": reasons,
        "full_risk_calculation_required": status != "selected",
    }
