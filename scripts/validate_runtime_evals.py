from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from runtime_eval_common import (
    DEFAULT_CASES,
    DEFAULT_SCHEMA,
    MANIFEST,
    ROOT,
    ROUTER_SKILL,
    VERSION_FILE,
    grade_decision,
    load_cases,
    load_manifest,
    load_schema,
    skill_ids,
    validate_decision_shape,
)

errors: list[str] = []

for path in (
    DEFAULT_CASES,
    DEFAULT_SCHEMA,
    ROOT / "scripts" / "run_runtime_evals.py",
    ROOT / "scripts" / "grade_runtime_evals.py",
    ROOT / ".github" / "workflows" / "runtime-eval.yml",
    ROOT / "evals" / "runtime" / "README.md",
):
    if not path.exists():
        errors.append(f"missing runtime Eval file: {path.relative_to(ROOT)}")

try:
    manifest = load_manifest(MANIFEST)
    suite = load_cases(DEFAULT_CASES)
    schema = load_schema(DEFAULT_SCHEMA)
except (OSError, json.JSONDecodeError, KeyError) as exc:
    print(f"ERROR: failed to load runtime Eval metadata: {exc}")
    raise SystemExit(1)

version = VERSION_FILE.read_text(encoding="utf-8").strip()
if manifest.get("version") != version:
    errors.append("SKILL_MANIFEST version differs from VERSION")

valid_skills = skill_ids(manifest)
if len(valid_skills) != len(manifest.get("skills", [])):
    errors.append("SKILL_MANIFEST contains duplicate skill IDs")

required_schema_fields = {
    "primary_skill",
    "supporting_skills",
    "rejected_skills",
    "execution_order",
    "reason",
    "confidence",
}
if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
    errors.append("routing decision schema must be a closed object")
if set(schema.get("required", [])) != required_schema_fields:
    errors.append("routing decision schema required fields differ from contract")
if set(schema.get("properties", {})) != required_schema_fields:
    errors.append("routing decision schema properties differ from contract")

cases = suite.get("cases")
if not isinstance(cases, list):
    errors.append("runtime suite cases must be an array")
    cases = []
if len(cases) != 8:
    errors.append(f"Canary Suite must contain exactly 8 cases, found {len(cases)}")

ids: set[str] = set()
for case in cases:
    cid = case.get("id")
    if not isinstance(cid, str) or not cid:
        errors.append("runtime case has an empty ID")
        continue
    if cid in ids:
        errors.append(f"duplicate runtime case ID: {cid}")
    ids.add(cid)
    if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
        errors.append(f"{cid}: prompt is empty")
    expected = case.get("expected")
    if not isinstance(expected, dict):
        errors.append(f"{cid}: expected must be an object")
        continue
    required_expected = {
        "primary_skill",
        "required_supporting_skills",
        "forbidden_selected_skills",
        "execution_order",
        "allow_additional_supporting_skills",
    }
    if set(expected) != required_expected:
        errors.append(f"{cid}: expected fields differ from contract")
        continue
    all_expected_ids = []
    primary = expected["primary_skill"]
    if primary is not None:
        all_expected_ids.append(primary)
    for name in ("required_supporting_skills", "forbidden_selected_skills", "execution_order"):
        value = expected[name]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{cid}: {name} must be an array of strings")
            continue
        if len(value) != len(set(value)):
            errors.append(f"{cid}: {name} contains duplicates")
        all_expected_ids.extend(value)
    unknown = sorted({item for item in all_expected_ids if item not in valid_skills})
    if unknown:
        errors.append(f"{cid}: unknown expected skill IDs: {unknown}")
    if primary == ROUTER_SKILL or ROUTER_SKILL in expected["required_supporting_skills"]:
        errors.append(f"{cid}: router must not be selected downstream")
    selected = ([primary] if primary else []) + expected["required_supporting_skills"]
    if set(expected["execution_order"]) != set(selected):
        errors.append(f"{cid}: execution_order must contain expected selected skills exactly once")
    if primary is None and (expected["required_supporting_skills"] or expected["execution_order"]):
        errors.append(f"{cid}: no-skill case must not select supporting skills")

# Prove deterministic grading with one synthetic pass and one intentional failure.
if cases:
    first = cases[0]
    expected = first["expected"]
    passing = {
        "primary_skill": expected["primary_skill"],
        "supporting_skills": expected["required_supporting_skills"],
        "rejected_skills": expected["forbidden_selected_skills"],
        "execution_order": expected["execution_order"],
        "reason": "Synthetic validator fixture.",
        "confidence": "high",
    }
    shape_errors = validate_decision_shape(passing, valid_skills)
    if shape_errors:
        errors.append(f"synthetic passing decision failed shape validation: {shape_errors}")
    grade = grade_decision(first, passing, valid_skills)
    if not grade["passed"]:
        errors.append(f"synthetic passing decision failed grader: {grade}")
    failing = dict(passing)
    failing["primary_skill"] = None
    failing["supporting_skills"] = []
    failing["execution_order"] = []
    if grade_decision(first, failing, valid_skills)["passed"]:
        errors.append("synthetic failing decision unexpectedly passed grader")

workflow = ROOT / ".github" / "workflows" / "runtime-eval.yml"
if workflow.exists():
    text = workflow.read_text(encoding="utf-8")
    for marker in (
        "workflow_dispatch:",
        "OPENAI_API_KEY",
        "run_runtime_evals.py",
        "grade_runtime_evals.py",
        "upload-artifact@v4",
    ):
        if marker not in text:
            errors.append(f"runtime workflow missing marker: {marker}")

print(f"Validated executable Runtime Eval suite: {len(cases)} Canary cases, {len(valid_skills)} skill IDs")
print("NOTE: static validation and synthetic grader checks do not call a model API.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
