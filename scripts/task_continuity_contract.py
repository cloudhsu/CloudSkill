from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASE_SCHEMA_PATH = ROOT / "evals" / "agent" / "task-continuity.schema.json"
RESULT_SCHEMA_PATH = ROOT / "evals" / "agent" / "task-continuity-result.schema.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing task-continuity contract: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid task-continuity contract JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"task-continuity contract must be an object: {path}")
    return payload


def _reference(schema: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    reference = schema.get("$ref")
    if not isinstance(reference, str):
        return schema
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported task-continuity schema reference: {reference!r}")
    resolved: Any = root
    for part in reference[2:].split("/"):
        if not isinstance(resolved, dict) or part not in resolved:
            raise ValueError(f"unresolved task-continuity schema reference: {reference!r}")
        resolved = resolved[part]
    if not isinstance(resolved, dict):
        raise ValueError(f"task-continuity schema reference is not an object: {reference!r}")
    return resolved


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported task-continuity schema type: {expected!r}")


def _json_equal(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's bool-is-int equivalence."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left is right
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if isinstance(left, str) or isinstance(right, str):
        return isinstance(left, str) and isinstance(right, str) and left == right
    if isinstance(left, list) or isinstance(right, list):
        return (
            isinstance(left, list)
            and isinstance(right, list)
            and len(left) == len(right)
            and all(_json_equal(a, b) for a, b in zip(left, right))
        )
    if isinstance(left, dict) or isinstance(right, dict):
        return (
            isinstance(left, dict)
            and isinstance(right, dict)
            and set(left) == set(right)
            and all(_json_equal(left[key], right[key]) for key in left)
        )
    return left == right


def _path(parent: str, child: str | int) -> str:
    if isinstance(child, int):
        return f"{parent}[{child}]" if parent else f"[{child}]"
    return f"{parent}.{child}" if parent else child


def _value_at(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _validate_schema(
    value: Any, schema: dict[str, Any], root: dict[str, Any], location: str = ""
) -> list[str]:
    schema = _reference(schema, root)
    errors: list[str] = []
    label = location or "value"

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_matches_type(value, item) for item in expected_types):
            errors.append(f"{label} must have type {' or '.join(expected_types)}")
            return errors
    if "const" in schema and not _json_equal(value, schema["const"]):
        errors.append(f"{label} must equal {schema['const']!r}")
    if "enum" in schema and not any(_json_equal(value, member) for member in schema["enum"]):
        errors.append(f"{label} must be one of {schema['enum']!r}")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{label} must contain at least {schema['minLength']} character(s)")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{label} must match pattern {pattern!r}")

    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema:
        if value < schema["minimum"]:
            errors.append(f"{label} must be at least {schema['minimum']}")

    if isinstance(value, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{label} must contain at least {minimum} item(s)")
        if schema.get("uniqueItems") is True:
            serialized = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{label} must not contain duplicate items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_validate_schema(item, item_schema, root, _path(location, index)))

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if isinstance(required, list):
            for name in required:
                if name not in value:
                    errors.append(f"{_path(location, name)} is required")
        if schema.get("additionalProperties") is False and isinstance(properties, dict):
            for name in sorted(set(value) - set(properties)):
                errors.append(f"{label} has unexpected field {name!r}")
        if isinstance(properties, dict):
            for name, child_schema in properties.items():
                if name in value and isinstance(child_schema, dict):
                    errors.extend(_validate_schema(value[name], child_schema, root, _path(location, name)))
    return errors


def _validate_invariants(case: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for invariant in schema.get("x-cloudbox-invariants", []):
        name = invariant.get("name") if isinstance(invariant, dict) else None
        if name == "sequential_turns":
            turns = _value_at(case, invariant["path"])
            field = invariant["field"]
            start = invariant.get("start", 1)
            if isinstance(turns, list):
                for index, turn in enumerate(turns, start=start):
                    if isinstance(turn, dict) and turn.get(field) != index:
                        errors.append(
                            f"{invariant['path']}[{index - start}].{field} must equal {index} to preserve order"
                        )
        elif name == "disjoint_arrays":
            left_path = invariant["left"]
            right_path = invariant["right"]
            left = _value_at(case, left_path)
            right = _value_at(case, right_path)
            if isinstance(left, list) and isinstance(right, list):
                overlap = sorted(set(left) & set(right))
                if overlap:
                    errors.append(f"{invariant['label']} overlap: {overlap}")
        elif name == "attempts_authorized":
            attempts = _value_at(case, invariant["attempts"])
            allowed = _value_at(case, invariant["allowed"])
            prohibited = _value_at(case, invariant["prohibited"])
            if isinstance(attempts, list) and isinstance(allowed, list):
                unallowed = sorted(set(attempts) - set(allowed))
                if unallowed:
                    errors.append(
                        f"{invariant['attempts']} contains action(s) not in {invariant['allowed']}: {unallowed}"
                    )
            if isinstance(attempts, list) and isinstance(prohibited, list):
                prohibited_attempts = sorted(set(attempts) & set(prohibited))
                if prohibited_attempts:
                    errors.append(
                        f"{invariant['attempts']} contains prohibited action(s): {prohibited_attempts}"
                    )
        elif name == "identified_id":
            location = invariant["path"]
            identity = _value_at(case, location)
            if isinstance(identity, dict):
                identified = identity.get("identified")
                identifier = identity.get("id")
                if identified is True and (not isinstance(identifier, str) or not identifier.strip()):
                    errors.append(f"identified {location} must have a non-blank id")
                if identified is False and identifier is not None:
                    errors.append(f"unidentified {location} must have a null id")
                if location.endswith("parent") and identified is False and identity.get("status") != "unknown":
                    errors.append(f"unidentified {location} must have unknown status")
        else:
            errors.append(f"unsupported task-continuity invariant: {name!r}")
    return errors


def _case_schema() -> tuple[dict[str, Any], dict[str, Any]]:
    root = _read_json(CASE_SCHEMA_PATH)
    definition = _value_at(root, "$defs.case")
    if not isinstance(definition, dict):
        raise ValueError("task-continuity schema is missing $defs.case")
    return root, definition


def _validate_result_invariants(result: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for invariant in schema.get("x-cloudbox-invariants", []):
        name = invariant.get("name") if isinstance(invariant, dict) else None
        if name != "result_evidence_matrix":
            errors.append(f"unsupported task-continuity result invariant: {name!r}")
            continue
        matched = False
        for row in invariant.get("rows", []):
            if not isinstance(row, dict):
                continue
            if not _json_equal(result.get("contract_validation"), row.get("contract_validation")):
                continue
            if not _json_equal(result.get("behavior_execution"), row.get("behavior_execution")):
                continue
            error_rule = row.get("errors")
            result_errors = result.get("errors")
            if error_rule == "empty" and result_errors == []:
                matched = True
            if error_rule == "nonempty" and isinstance(result_errors, list) and result_errors:
                matched = True
        if not matched:
            errors.append(
                "result evidence state is incoherent: contract_validation, "
                "behavior_execution, and errors do not match the declared matrix"
            )
    return errors


def load_cases(path: Path) -> list[dict]:
    """Load cases validated by the authoritative published case schema."""
    payload = _read_json(path)
    schema = _read_json(CASE_SCHEMA_PATH)
    errors = _validate_schema(payload, schema, schema)
    if errors:
        raise ValueError("invalid task-continuity case suite: " + "; ".join(errors))
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("task-continuity cases payload must contain a cases array")
    case_schema = schema["$defs"]["case"]
    for case in cases:
        if isinstance(case, dict):
            case_errors = _validate_invariants(case, case_schema)
            if case_errors:
                raise ValueError("invalid task-continuity case suite: " + "; ".join(case_errors))
    return cases


def validate_case(case: dict) -> list[str]:
    """Return errors from the authoritative schema and its declared invariants."""
    try:
        schema, case_schema = _case_schema()
    except ValueError as exc:
        return [str(exc)]
    errors = _validate_schema(case, case_schema, schema)
    if isinstance(case, dict):
        errors.extend(_validate_invariants(case, case_schema))
    return errors


def validate_result(result: dict) -> list[str]:
    """Validate a structural or future behavior-evidence result record."""
    try:
        schema = _read_json(RESULT_SCHEMA_PATH)
    except ValueError as exc:
        return [str(exc)]
    errors = _validate_schema(result, schema, schema)
    if isinstance(result, dict):
        errors.extend(_validate_result_invariants(result, schema))
    return errors


def static_validation_result(case_id: str, errors: list[str]) -> dict[str, Any]:
    """Build the only result shape emitted by this structure-only validator."""
    return {
        "case_id": case_id,
        "contract_validation": "FAIL" if errors else "PASS",
        "behavior_execution": "NOT RUN",
        "errors": errors,
    }


def validation_summary(errors: list[str]) -> tuple[int, str]:
    """Return a CI-safe status and heading for this static contract check."""
    if errors:
        return 1, "FAILED task-continuity contract validation:"
    return 0, "Validated task-continuity contract expectations and canonical cases."
