from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRICS = ROOT / "evals" / "runtime" / "cases" / "behavior-rubrics.json"
GRADER = ROOT / "scripts" / "grade_behavior_evals.py"
CONTRACT_VALIDATOR = ROOT / "scripts" / "validate_behavior_contract.py"

errors: list[str] = []

for path in (RUBRICS, GRADER, CONTRACT_VALIDATOR):
    if not path.exists():
        errors.append(f"missing Behavior Eval file: {path.relative_to(ROOT)}")

try:
    payload = json.loads(RUBRICS.read_text(encoding="utf-8")) if RUBRICS.exists() else {}
except json.JSONDecodeError as exc:
    errors.append(f"invalid Behavior Eval rubric JSON: {exc}")
    payload = {}

if payload.get("schema_version") != 1:
    errors.append("Behavior Eval rubric schema_version must be 1")

cases = payload.get("cases")
if not isinstance(cases, dict) or not cases:
    errors.append("Behavior Eval rubrics must contain a non-empty cases object")
    cases = {}

for case_id, rubric in cases.items():
    if not isinstance(case_id, str) or not case_id:
        errors.append("Behavior Eval rubric has an empty case ID")
        continue
    if not isinstance(rubric, dict):
        errors.append(f"{case_id}: rubric must be an object")
        continue
    passing = rubric.get("passing_score")
    if not isinstance(passing, (int, float)) or not 0 <= passing <= 100:
        errors.append(f"{case_id}: passing_score must be between 0 and 100")
    criteria = rubric.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        errors.append(f"{case_id}: criteria must be a non-empty array")
        continue
    ids: set[str] = set()
    weight_total = 0
    for criterion in criteria:
        if not isinstance(criterion, dict):
            errors.append(f"{case_id}: criterion must be an object")
            continue
        cid = criterion.get("id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"{case_id}: criterion ID is empty")
            continue
        if cid in ids:
            errors.append(f"{case_id}: duplicate criterion ID {cid}")
        ids.add(cid)
        weight = criterion.get("weight")
        if not isinstance(weight, int) or weight <= 0:
            errors.append(f"{case_id}/{cid}: weight must be a positive integer")
        else:
            weight_total += weight
        groups = criterion.get("all_groups")
        if not isinstance(groups, list) or not groups:
            errors.append(f"{case_id}/{cid}: all_groups must be a non-empty array")
        else:
            for group in groups:
                if (
                    not isinstance(group, list)
                    or not group
                    or any(not isinstance(item, str) or not item for item in group)
                ):
                    errors.append(
                        f"{case_id}/{cid}: each all_groups item must be a non-empty string array"
                    )
    if weight_total != 100:
        errors.append(f"{case_id}: criterion weights must total 100, found {weight_total}")

if GRADER.exists():
    text = GRADER.read_text(encoding="utf-8")
    for marker in ("grade_output", "passing_score", "penalty_points", "render_markdown"):
        if marker not in text:
            errors.append(f"Behavior grader missing marker: {marker}")

print(f"Validated deterministic Behavior Eval rubrics for {len(cases)} case(s).")
print(
    "NOTE: output-contract integration is validated separately by validate_behavior_contract.py; this validator does not copy prompt markers."
)
print("NOTE: rubric validation does not call a model.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
