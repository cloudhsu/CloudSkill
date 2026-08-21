"""Shared portable JSON-Schema subset interpreter.

Extracted from two independent, drifted implementations --
`task_continuity_contract.py::_validate_schema` (the narrower original) and
`task_continuity_runner.py::_task3_schema_errors` (a superset that had grown
`maxItems`, `contains`, `format: date`, `allOf`, `if`/`then`/`else`, `not`,
and `additionalProperties`-as-a-schema on top of the same core) -- see
`docs/plans/2026-08-17-validate-scripts-internal-audit.md` Milestone 8.

This module keeps the superset behavior. Before extracting it, both
implementations were run against every real schema and case file this
repository actually validates (`task-continuity.schema.json`,
`task-continuity-result.schema.json`, all 10 committed cases, and synthetic
result-shape samples) and produced byte-identical error lists in every case.
Two behavioral differences from the narrower original were found and
confirmed harmless because neither schema this repository validates has a
`"type": "number"` field: (1) the superset requires `math.isfinite` as part
of a `"number"` type match, correctly rejecting NaN/Infinity, which the
original silently accepted; (2) the superset's `"minimum"` check applies to
both `int` and `float`, where the original checked only `int`, silently
accepting an out-of-range float. Both are latent-bug fixes, not intentional
behavior this repository ever relied on.
"""

from __future__ import annotations

import json
import math
import re
from datetime import date
from typing import Any


def json_equal(left: Any, right: Any) -> bool:
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
            and all(json_equal(a, b) for a, b in zip(left, right))
        )
    if isinstance(left, dict) or isinstance(right, dict):
        return (
            isinstance(left, dict)
            and isinstance(right, dict)
            and set(left) == set(right)
            and all(json_equal(left[key], right[key]) for key in left)
        )
    return left == right


def join_path(parent: str, child: str | int) -> str:
    if isinstance(child, int):
        return f"{parent}[{child}]" if parent else f"[{child}]"
    return f"{parent}.{child}" if parent else child


def resolve_reference(schema: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    reference = schema.get("$ref")
    if not isinstance(reference, str):
        return schema
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported schema reference: {reference!r}")
    resolved: Any = root
    for part in reference[2:].split("/"):
        if not isinstance(resolved, dict) or part not in resolved:
            raise ValueError(f"unresolved schema reference: {reference!r}")
        resolved = resolved[part]
    if not isinstance(resolved, dict):
        raise ValueError(f"schema reference is not an object: {reference!r}")
    return resolved


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def schema_errors(
    value: Any, schema: dict[str, Any], root: dict[str, Any], location: str = ""
) -> list[str]:
    """Shared interpreter for this repository's published JSON-Schema subset."""
    schema = resolve_reference(schema, root)
    errors: list[str] = []
    label = location or "value"
    expected_type = schema.get("type")
    if expected_type is not None:
        expected = expected_type if isinstance(expected_type, list) else [expected_type]
        matches = {
            "object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value),
            "boolean": isinstance(value, bool), "null": value is None,
        }
        if not any(matches.get(item, False) for item in expected):
            return [f"{label} must have type {' or '.join(expected)}"]
    if "const" in schema and not json_equal(value, schema["const"]):
        errors.append(f"{label} must equal {schema['const']!r}")
    if "enum" in schema and not any(json_equal(value, member) for member in schema["enum"]):
        errors.append(f"{label} must be one of {schema['enum']!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{label} must contain at least {schema['minLength']} character(s)")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{label} must match pattern {pattern!r}")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{label} must be an ISO calendar date")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{label} must be at least {schema['minimum']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{label} must contain at least {schema['minItems']} item(s)")
        maximum = schema.get("maxItems")
        if isinstance(maximum, int) and len(value) > maximum:
            errors.append(f"{label} must contain at most {maximum} item(s)")
        if schema.get("uniqueItems") is True:
            serialized = [_canonical_json(item) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{label} must not contain duplicate items")
        items = schema.get("items")
        if isinstance(items, dict):
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, items, root, join_path(location, index)))
        contains = schema.get("contains")
        if isinstance(contains, dict) and not any(not schema_errors(item, contains, root, join_path(location, index)) for index, item in enumerate(value)):
            errors.append(f"{label} must contain an item matching its contains schema")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if isinstance(required, list):
            for name in required:
                if name not in value:
                    errors.append(f"{join_path(location, name)} is required")
        if isinstance(properties, dict):
            if schema.get("additionalProperties") is False:
                for name in sorted(set(value) - set(properties)):
                    errors.append(f"{label} has unexpected field {name!r}")
            elif isinstance(schema.get("additionalProperties"), dict):
                for name in sorted(set(value) - set(properties)):
                    errors.extend(schema_errors(value[name], schema["additionalProperties"], root, join_path(location, name)))
            for name, child_schema in properties.items():
                if name in value and isinstance(child_schema, dict):
                    errors.extend(schema_errors(value[name], child_schema, root, join_path(location, name)))
    for child in schema.get("allOf", []):
        if isinstance(child, dict):
            errors.extend(schema_errors(value, child, root, location))
        else:
            errors.append(f"{label}.allOf entry must be an object")
    condition = schema.get("if")
    if isinstance(condition, dict):
        branch = "then" if not schema_errors(value, condition, root, location) else "else"
        if isinstance(schema.get(branch), dict):
            errors.extend(schema_errors(value, schema[branch], root, location))
    negated = schema.get("not")
    if isinstance(negated, dict) and not schema_errors(value, negated, root, location):
        errors.append(f"{label} must not match its negated schema")
    return errors


def validate_schema_instance(value: Any, schema: dict[str, Any]) -> list[str]:
    """Validate an in-memory JSON value through the shared interpreter."""
    if not isinstance(schema, dict):
        return ["schema must be an object"]
    return schema_errors(value, schema, schema)
