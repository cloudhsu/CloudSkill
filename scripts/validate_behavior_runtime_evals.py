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

# Regression fixture: 2026-08-09 grader-precision hotfixes.
#
# Round 1: the R07 "assumptions-unknowns" and "restart-reconstruction"
# criteria were proven to false-negative against real captured Runtime Eval
# output (CloudSkill-local-eval-review-local-review-20260809-113507.zip)
# because the regex patterns did not tolerate common numbered/bulleted
# heading markers, markdown emphasis, plural "assumptions:", or a
# "physical/material state" phrasing.
#
# Round 2: the first-ever live Codex Runtime Eval
# (local-review-20260809-155256) scored a genuinely strong answer 78/100
# because "verification-scenarios" only recognized "test that X"/"inject a
# X" phrasing (not a numbered "N. <imperative verb> ... Expect ..." style),
# and "state-authority" only recognized "authoritative state"/"state
# authority" (not an "Authority matrix"/"sole authority" table). Re-grading
# the same captured output after the fix (no new model call) raised Codex
# 78->100, the Ollama repeat=3 bundle 79.8->83.8, and the earlier Claude
# bundle 78->84 -- consistent across all three providers, confirming this was
# grader precision, not a content quality gap.
#
# Round 3: the live Claude repeat=3 run
# (local-review-20260809-180816) used numbered bold Markdown scenario titles
# followed by ``Expected:``. All three answers contained concrete scenarios,
# but the deterministic grader awarded 0/8. Preserve that exact formatting
# family here so future re-grades do not repeat the false negative.
#
# Re-run the deterministic grader against representative synthetic text on
# every check so these precision regressions cannot silently reappear.
r07 = cases.get("R07-english-equipment-architecture")
if isinstance(r07, dict) and r07.get("criteria"):
    sys.path.insert(0, str(GRADER.parent))
    from grade_behavior_evals import grade_output  # noqa: E402

    def _criterion_passed(report: dict, criterion_id: str) -> bool:
        for item in report["criteria"]:
            if item["id"] == criterion_id:
                return bool(item["passed"])
        return False

    positive_text = (
        "Restart Reconstruction\n"
        "Upon reboot, the controller must reconstruct the physical/material state "
        "from sensor readback before accepting new commands.\n\n"
        "9. **Assumptions & Unresolved Inputs**\n"
        "- Assumptions: sensors report within 100ms.\n"
        "- Unresolved: fencing token width.\n\n"
        "Authority matrix\n"
        "Chamber physical state and sensor quality: sole authority is the chamber IPC service.\n\n"
        "Fault-injection verification\n"
        "1. Disconnect a chamber IPC after command acceptance. Expect quarantine on reconnect "
        "and readback reconciliation before new work is accepted.\n"
        "2. **Restart during an in-flight move.** Expected: the reservation remains "
        "RecoveryRequired until current occupancy and position evidence reconcile.\n"
    )
    negative_text = (
        "The system restarts and continues processing commands without "
        "recording any design caveats, open questions, ownership assignment, "
        "or failure scenarios.\n"
    )

    positive_report = grade_output(positive_text, r07)
    negative_report = grade_output(negative_text, r07)

    for criterion_id in (
        "restart-reconstruction",
        "assumptions-unknowns",
        "state-authority",
        "verification-scenarios",
    ):
        if not _criterion_passed(positive_report, criterion_id):
            errors.append(
                f"R07-english-equipment-architecture/{criterion_id}: regression fixture "
                "expected this criterion to match numbered/bulleted real-world phrasing "
                "but the grader did not detect it"
            )
        if _criterion_passed(negative_report, criterion_id):
            errors.append(
                f"R07-english-equipment-architecture/{criterion_id}: negative-control "
                "fixture unexpectedly matched; the pattern may have become too permissive"
            )

print(f"Validated deterministic Behavior Eval rubrics for {len(cases)} case(s).")
print(
    "NOTE: output-contract integration is validated separately by validate_behavior_contract.py; this validator does not copy prompt markers."
)
print("NOTE: rubric validation does not call a model.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
