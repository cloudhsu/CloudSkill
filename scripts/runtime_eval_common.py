from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "runtime" / "cases" / "canary.json"
DEFAULT_SCHEMA = ROOT / "evals" / "runtime" / "schemas" / "routing-decision.schema.json"
MANIFEST = ROOT / "SKILL_MANIFEST.json"
VERSION_FILE = ROOT / "VERSION"
ROUTER_SKILL = "using-cloudskill"
EXPECTED_DECISION_KEYS = {
    "primary_skill",
    "supporting_skills",
    "rejected_skills",
    "execution_order",
    "reason",
    "confidence",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path: Path = DEFAULT_CASES) -> dict[str, Any]:
    return load_json(path)


def load_schema(path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    return load_json(path)


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    return load_json(path)


def skill_ids(manifest: dict[str, Any]) -> set[str]:
    return {item["name"] for item in manifest["skills"]}


def validate_decision_shape(decision: Any, valid_skills: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(decision, dict):
        return ["decision is not an object"]
    keys = set(decision)
    if keys != EXPECTED_DECISION_KEYS:
        errors.append(
            f"decision keys differ: missing={sorted(EXPECTED_DECISION_KEYS - keys)} "
            f"extra={sorted(keys - EXPECTED_DECISION_KEYS)}"
        )
        return errors

    primary = decision["primary_skill"]
    supporting = decision["supporting_skills"]
    rejected = decision["rejected_skills"]
    order = decision["execution_order"]
    reason = decision["reason"]
    confidence = decision["confidence"]

    if primary is not None and not isinstance(primary, str):
        errors.append("primary_skill must be a string or null")
    for name, value in (
        ("supporting_skills", supporting),
        ("rejected_skills", rejected),
        ("execution_order", order),
    ):
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{name} must be an array of strings")
        elif len(value) != len(set(value)):
            errors.append(f"{name} contains duplicates")

    if not isinstance(reason, str) or not reason.strip():
        errors.append("reason must be a non-empty string")
    if confidence not in {"high", "medium", "low"}:
        errors.append("confidence must be high, medium, or low")

    if errors:
        return errors

    all_ids = ([primary] if primary else []) + supporting + rejected + order
    unknown = sorted({item for item in all_ids if item not in valid_skills})
    if unknown:
        errors.append(f"unknown skill IDs: {unknown}")

    selected = ([primary] if primary else []) + supporting
    if len(selected) != len(set(selected)):
        errors.append("primary and supporting skills overlap")
    if set(order) != set(selected):
        errors.append("execution_order must contain every selected skill exactly once")
    if set(rejected) & set(selected):
        errors.append("rejected skills overlap selected skills")
    if primary is None and (supporting or order):
        errors.append("no-skill decisions must have empty supporting_skills and execution_order")
    return errors


def selected_skills(decision: dict[str, Any]) -> list[str]:
    primary = decision.get("primary_skill")
    supporting = decision.get("supporting_skills") or []
    return ([primary] if primary else []) + supporting


def grade_decision(
    case: dict[str, Any], decision: Any, valid_skills: set[str]
) -> dict[str, Any]:
    expected = case["expected"]
    shape_errors = validate_decision_shape(decision, valid_skills)
    if shape_errors:
        checks = {
            "valid_output": False,
            "primary_skill": False,
            "required_supporting_skills": False,
            "additional_supporting_skills": False,
            "forbidden_selected_skills": False,
            "execution_order": False,
            "router_not_downstream": False,
        }
        return {
            "passed": False,
            "checks": checks,
            "errors": shape_errors,
        }

    primary = decision["primary_skill"]
    supporting = decision["supporting_skills"]
    selected = set(selected_skills(decision))
    required = set(expected["required_supporting_skills"])
    forbidden = set(expected["forbidden_selected_skills"])
    allow_extra = expected.get("allow_additional_supporting_skills", False)

    checks = {
        "valid_output": True,
        "primary_skill": primary == expected["primary_skill"],
        "required_supporting_skills": required.issubset(set(supporting)),
        "additional_supporting_skills": allow_extra or set(supporting) == required,
        "forbidden_selected_skills": not bool(selected & forbidden),
        "execution_order": decision["execution_order"] == expected["execution_order"],
        "router_not_downstream": ROUTER_SKILL not in selected,
    }
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": all(checks.values()), "checks": checks, "errors": errors}
