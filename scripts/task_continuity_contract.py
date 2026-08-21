from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from json_schema_interpreter import json_equal, schema_errors

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


def _value_at(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


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
            if not json_equal(result.get("contract_validation"), row.get("contract_validation")):
                continue
            if not json_equal(result.get("behavior_execution"), row.get("behavior_execution")):
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
    errors = schema_errors(payload, schema, schema)
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
    errors = schema_errors(case, case_schema, schema)
    if isinstance(case, dict):
        errors.extend(_validate_invariants(case, case_schema))
    return errors


def validate_result(result: dict) -> list[str]:
    """Validate a structural or future behavior-evidence result record."""
    try:
        schema = _read_json(RESULT_SCHEMA_PATH)
    except ValueError as exc:
        return [str(exc)]
    errors = schema_errors(result, schema, schema)
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
