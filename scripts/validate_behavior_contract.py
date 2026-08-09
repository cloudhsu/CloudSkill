from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

errors: list[str] = []

try:
    from behavior_output_contract import (
        BEHAVIOR_DELIVERABLE_SCHEMA,
        BEHAVIOR_MIN_FINAL_CHARACTERS,
        BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT,
        BEHAVIOR_OUTPUT_CONTRACT_ID,
        CONTRACT,
        CONTRACT_PATH,
        REFINEMENT_DELIVERABLE_SCHEMA,
        REFINEMENT_MIN_FINAL_CHARACTERS,
        REQUIRED_CONSUMER_PATHS,
        extract_final_value,
        first_internal_planning_pattern,
        render_contract_prompt,
    )
except Exception as exc:
    print(
        f"ERROR: cannot load Behavior output contract: {exc}"
    )
    raise SystemExit(1)

try:
    from runtime_eval_common import (
        BEHAVIOR_DELIVERABLE_SCHEMA as RUNTIME_SCHEMA,
        _behavior_system_prompt,
    )
    from run_local_eval_review import (
        BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT
        as LOCAL_REVIEW_FINGERPRINT,
        BEHAVIOR_OUTPUT_CONTRACT_ID as LOCAL_REVIEW_CONTRACT_ID,
        build_refiner_system_prompt,
        extract_refined_final,
    )
    from run_runtime_evals import (
        BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT
        as RUNTIME_FINGERPRINT,
        BEHAVIOR_OUTPUT_CONTRACT_ID as RUNTIME_CONTRACT_ID,
        extract_final_deliverable,
    )
except Exception as exc:
    print(
        f"ERROR: cannot import Behavior contract consumers: {exc}"
    )
    raise SystemExit(1)

if not CONTRACT_PATH.is_file():
    errors.append(
        "missing authoritative contract: "
        f"{CONTRACT_PATH.relative_to(ROOT)}"
    )
if CONTRACT.get("contract_id") != BEHAVIOR_OUTPUT_CONTRACT_ID:
    errors.append(
        "loaded contract ID does not match exported contract ID"
    )
if len(BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT) != 64:
    errors.append(
        "Behavior output contract fingerprint must be SHA-256"
    )
if RUNTIME_SCHEMA != BEHAVIOR_DELIVERABLE_SCHEMA:
    errors.append(
        "runtime Behavior schema drifted from authoritative contract"
    )
if RUNTIME_CONTRACT_ID != BEHAVIOR_OUTPUT_CONTRACT_ID:
    errors.append(
        "Runtime runner contract ID drifted from authoritative contract"
    )
if RUNTIME_FINGERPRINT != BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT:
    errors.append(
        "Runtime runner fingerprint drifted from authoritative contract"
    )
if LOCAL_REVIEW_CONTRACT_ID != BEHAVIOR_OUTPUT_CONTRACT_ID:
    errors.append(
        "local review contract ID drifted from authoritative contract"
    )
if LOCAL_REVIEW_FINGERPRINT != BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT:
    errors.append(
        "local review fingerprint drifted from authoritative contract"
    )

behavior_prompt = _behavior_system_prompt(
    decision={
        "primary_skill": "equipment-control-architecture",
        "supporting_skills": [],
    },
    skill_sections=[],
    reference_sections=[],
)
expected_behavior_contract = render_contract_prompt(
    minimum_characters=BEHAVIOR_MIN_FINAL_CHARACTERS
)
if expected_behavior_contract not in behavior_prompt:
    errors.append(
        "runtime Behavior prompt does not render authoritative contract"
    )

refiner_prompt = build_refiner_system_prompt()
expected_refiner_contract = render_contract_prompt(
    minimum_characters=REFINEMENT_MIN_FINAL_CHARACTERS
)
if expected_refiner_contract not in refiner_prompt:
    errors.append(
        "refiner prompt does not render authoritative contract"
    )

for prompt_name, prompt in (
    ("runtime", behavior_prompt),
    ("refiner", refiner_prompt),
):
    if BEHAVIOR_OUTPUT_CONTRACT_ID not in prompt:
        errors.append(
            f"{prompt_name} prompt is missing the contract ID"
        )
    if BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT not in prompt:
        errors.append(
            f"{prompt_name} prompt is missing contract fingerprint"
        )
    if "The first non-whitespace line must be <final>" in prompt:
        errors.append(
            f"{prompt_name} prompt still contains retired tag contract"
        )

if (
    BEHAVIOR_DELIVERABLE_SCHEMA["properties"]["final"]["minLength"]
    != BEHAVIOR_MIN_FINAL_CHARACTERS
):
    errors.append(
        "Behavior schema minimum drifted from authoritative contract"
    )
if (
    REFINEMENT_DELIVERABLE_SCHEMA["properties"]["final"]["minLength"]
    != REFINEMENT_MIN_FINAL_CHARACTERS
):
    errors.append(
        "refinement schema minimum drifted from authoritative contract"
    )

behavior_candidate = (
    "A" * (BEHAVIOR_MIN_FINAL_CHARACTERS + 20)
)
structured = json.dumps({"final": behavior_candidate})
value, extracted, contract = extract_final_value(
    structured,
    minimum_characters=BEHAVIOR_MIN_FINAL_CHARACTERS,
)
if (
    not extracted
    or value != behavior_candidate
    or contract != BEHAVIOR_OUTPUT_CONTRACT_ID
):
    errors.append(
        "authoritative structured extraction failed"
    )

value2, extracted2 = extract_final_deliverable(structured)
if not extracted2 or value2 != behavior_candidate:
    errors.append(
        "runtime wrapper drifted from authoritative extraction"
    )

refined_candidate = (
    "B" * (REFINEMENT_MIN_FINAL_CHARACTERS + 20)
)
value3, extracted3, contract3 = extract_refined_final(
    json.dumps({"final": refined_candidate})
)
if (
    not extracted3
    or value3 != refined_candidate
    or contract3 != BEHAVIOR_OUTPUT_CONTRACT_ID
):
    errors.append(
        "refiner wrapper drifted from authoritative extraction"
    )

mention = (
    "Planning says use <final> and </final>, "
    "then keeps reasoning."
)
value4, extracted4, contract4 = extract_final_value(
    mention,
    minimum_characters=BEHAVIOR_MIN_FINAL_CHARACTERS,
)
if (
    extracted4
    or value4 != mention
    or contract4 != "unstructured"
):
    errors.append(
        "tag mention was incorrectly accepted as final deliverable"
    )

legacy = (
    "planning\n<final>"
    + refined_candidate
    + "</final>"
)
value5, extracted5, contract5 = extract_final_value(
    legacy,
    minimum_characters=REFINEMENT_MIN_FINAL_CHARACTERS,
)
if (
    not extracted5
    or value5 != refined_candidate
    or contract5 != "terminal-final-legacy"
):
    errors.append(
        "strict terminal legacy fallback failed"
    )

trailing = legacy + "\nmore planning"
value6, extracted6, contract6 = extract_final_value(
    trailing,
    minimum_characters=REFINEMENT_MIN_FINAL_CHARACTERS,
)
if (
    extracted6
    or value6 != trailing
    or contract6 != "unstructured"
):
    errors.append(
        "non-terminal legacy block was incorrectly accepted"
    )

if (
    first_internal_planning_pattern(
        "We must first structure the deliverable."
    )
    is None
):
    errors.append(
        "authoritative planning detector missed regression phrase"
    )
if (
    first_internal_planning_pattern(
        "## Authority matrix\nChamber A owns readback."
    )
    is not None
):
    errors.append(
        "authoritative planning detector produced false positive"
    )

# Consumer registry validation.
if set(REQUIRED_CONSUMER_PATHS) != set(
    CONTRACT.get("required_consumer_paths") or []
):
    errors.append(
        "required consumer registry export drifted from contract data"
    )

for relative in REQUIRED_CONSUMER_PATHS:
    path = ROOT / relative
    if not path.is_file():
        errors.append(
            f"required Behavior contract consumer is missing: {relative}"
        )
        continue
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=relative)
    except SyntaxError as exc:
        errors.append(
            f"required consumer cannot be parsed: {relative}: {exc}"
        )
        continue

    imports_contract = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "behavior_output_contract"
        for node in ast.walk(tree)
    )
    if not imports_contract:
        errors.append(
            f"required consumer does not import shared contract: {relative}"
        )

    # These are retired duplicated contract artifacts. They may appear only
    # inside this dedicated anti-drift validator as forbidden test values.
    if relative != "scripts/validate_behavior_contract.py":
        forbidden_literals = (
            "json-final-v1",
            "Behavior prompt missing marker:",
            "The first non-whitespace line must be <final>",
        )
        for literal in forbidden_literals:
            if literal in source:
                errors.append(
                    f"required consumer contains retired duplicated "
                    f"contract literal {literal!r}: {relative}"
                )

# Cross-validator drift scan. Other validators must delegate Behavior output
# semantics to this validator instead of copying old API names or prompt text.
for path in sorted(SCRIPTS.glob("validate_*.py")):
    if path.name == "validate_behavior_contract.py":
        continue
    source = path.read_text(encoding="utf-8")
    relative = path.relative_to(ROOT).as_posix()
    forbidden = (
        "json-final-v1",
        "Behavior prompt missing marker:",
        "The first non-whitespace line must be <final>",
        "from run_local_eval_review import extract_final",
    )
    for literal in forbidden:
        if literal in source:
            errors.append(
                f"validator duplicates or references retired "
                f"Behavior contract artifact {literal!r}: {relative}"
            )

print(
    "Validated one authoritative Behavior output contract across "
    "runtime, refiner, schemas, extraction, planning checks, "
    "registered consumers, and validator drift scanning."
)
print(
    f"Contract: {BEHAVIOR_OUTPUT_CONTRACT_ID} "
    f"fingerprint={BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT}"
)
print(
    "NOTE: this validator does not call Codex, Ollama, "
    "OpenAI API, or another model."
)
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
