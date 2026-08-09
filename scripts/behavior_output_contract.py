from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "evals" / "runtime" / "contracts" / "behavior-output-contract.json"


def _load_contract() -> dict[str, Any]:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise RuntimeError("Behavior output contract schema_version must be 1")
    if payload.get("contract_id") != "behavior-final-json-v1":
        raise RuntimeError("Unexpected Behavior output contract ID")
    if payload.get("output_key") != "final":
        raise RuntimeError("Behavior output contract output_key must be final")

    minimum = payload.get("minimum_characters")
    if not isinstance(minimum, dict):
        raise RuntimeError("Behavior output contract minimum_characters is missing")
    for name in ("behavior", "refinement"):
        value = minimum.get(name)
        if not isinstance(value, int) or value < 1:
            raise RuntimeError(
                f"Behavior output contract minimum {name} must be positive"
            )

    requirements = payload.get("prompt_requirements")
    if not isinstance(requirements, list) or not requirements or any(
        not isinstance(item, str) or not item.strip() for item in requirements
    ):
        raise RuntimeError(
            "Behavior output contract prompt_requirements is invalid"
        )

    patterns = payload.get("internal_planning_patterns")
    if not isinstance(patterns, list) or not patterns or any(
        not isinstance(item, str) or not item for item in patterns
    ):
        raise RuntimeError(
            "Behavior output contract internal_planning_patterns is invalid"
        )
    for pattern in patterns:
        re.compile(pattern, re.I | re.S)

    consumers = payload.get("required_consumer_paths")
    if not isinstance(consumers, list) or not consumers or any(
        not isinstance(item, str)
        or not item.startswith("scripts/")
        or not item.endswith(".py")
        for item in consumers
    ):
        raise RuntimeError(
            "Behavior output contract required_consumer_paths is invalid"
        )
    if len(set(consumers)) != len(consumers):
        raise RuntimeError(
            "Behavior output contract required_consumer_paths contains duplicates"
        )

    return payload


CONTRACT = _load_contract()
BEHAVIOR_OUTPUT_CONTRACT_ID = str(CONTRACT["contract_id"])
BEHAVIOR_MIN_FINAL_CHARACTERS = int(
    CONTRACT["minimum_characters"]["behavior"]
)
REFINEMENT_MIN_FINAL_CHARACTERS = int(
    CONTRACT["minimum_characters"]["refinement"]
)
INTERNAL_PLANNING_PATTERNS = tuple(
    str(item) for item in CONTRACT["internal_planning_patterns"]
)
REQUIRED_CONSUMER_PATHS = tuple(
    str(item) for item in CONTRACT["required_consumer_paths"]
)


def contract_fingerprint() -> str:
    canonical = json.dumps(
        CONTRACT,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT = contract_fingerprint()


def final_schema(minimum_characters: int) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["final"],
        "properties": {
            "final": {
                "type": "string",
                "minLength": minimum_characters,
            }
        },
    }


BEHAVIOR_DELIVERABLE_SCHEMA = final_schema(
    BEHAVIOR_MIN_FINAL_CHARACTERS
)
REFINEMENT_DELIVERABLE_SCHEMA = final_schema(
    REFINEMENT_MIN_FINAL_CHARACTERS
)


def render_contract_prompt(*, minimum_characters: int) -> str:
    lines = [
        f"Output contract ID: {BEHAVIOR_OUTPUT_CONTRACT_ID}.",
        (
            "Output contract fingerprint: "
            f"{BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT}."
        ),
        *[str(item) for item in CONTRACT["prompt_requirements"]],
        (
            "The final value must contain at least "
            f"{minimum_characters} characters."
        ),
    ]
    return "\n".join(lines)


def extract_final_value(
    text: str,
    *,
    minimum_characters: int,
    allow_legacy_terminal: bool = True,
) -> tuple[str, bool, str]:
    stripped = text.strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        value = None

    if isinstance(value, dict) and set(value) == {"final"}:
        candidate = value.get("final")
        if (
            isinstance(candidate, str)
            and len(candidate.strip()) >= minimum_characters
        ):
            return (
                candidate.strip(),
                True,
                BEHAVIOR_OUTPUT_CONTRACT_ID,
            )

    legacy = CONTRACT.get("legacy_terminal_final") or {}
    if allow_legacy_terminal and legacy.get("allowed") is True:
        matches = list(
            re.finditer(
                r"<final>\s*(.*?)\s*</final>",
                text,
                re.I | re.S,
            )
        )
        for match in reversed(matches):
            candidate = match.group(1).strip()
            if (
                legacy.get("must_terminate_response") is True
                and text[match.end() :].strip()
            ):
                continue
            if len(candidate) < minimum_characters:
                continue
            return candidate, True, "terminal-final-legacy"

    return stripped, False, "unstructured"


def first_internal_planning_pattern(text: str) -> str | None:
    for pattern in INTERNAL_PLANNING_PATTERNS:
        if re.search(pattern, text, re.I | re.S):
            return pattern
    return None
