from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

required_markers = {
    "CLOUDBOX_SKILLS_AGENT_HANDOFF.md": [
        "## Current increment",
        "## Read order",
        "## Standard continuation commands",
        "## Evidence handoff contract",
        "## Behavior output contract authority",
        "Consumer registry",
        "## Eval Inbox import path",
    ],
    "docs/history/AGENT_HANDOFF_ARCHIVE.md": [
        "## Current repository state",
        "## Latest verified evidence before this increment",
        "## Open evolution items",
        "## New-conversation bootstrap",
    ],
    "docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md": [
        "## Design purpose",
        "## Problems it is intended to solve",
        "## Simple end-to-end flow",
        "## Runtime Eval layers",
        "## Behavior output contract authority",
        "Consumer registry",
        "## Evolution rule",
    ],
    "docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md": [
        "# CloudSkill evolution change history",
        "## 2026-08-09",
        "Single-source Behavior output contract",
        "Consumer registry",
        "## Maintenance rule",
    ],
}

for relative, markers in required_markers.items():
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing evolution document: {relative}")
        continue
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < 800:
        errors.append(f"evolution document is unexpectedly short: {relative}")
    for marker in markers:
        if marker not in text:
            errors.append(f"{relative} missing marker: {marker}")

# Living-document byte budgets. These two files are meant to be read in
# full on demand (CLOUDBOX_SKILLS_AGENT_HANDOFF.md is required reading
# before Skill/Eval/grader/runtime-tooling work) -- an unbounded, ever-
# appended file is a real and growing token cost, not just an aesthetic
# concern. CLOUDBOX_SKILLS_AGENT_HANDOFF.md was 1898 lines / ~110KB before
# a 2026-08-18 manual archival pass (see docs/history/AGENT_HANDOFF_ARCHIVE.md)
# reset it -- this budget exists so growth back to that size fails CI
# immediately instead of silently accumulating for another 9+ days.
# Mirrors scripts/validate_skill_context_budget.py's GRANDFATHERED_CEILINGS
# pattern: a frozen ceiling is zero further growth room, not a permanent
# exemption. Shrinking a file below its budget (or eliminating the ceiling
# entry once a file no longer needs one) is always allowed.
LIVING_DOC_BUDGET_BYTES = {
    # Live budget: real headroom for a handful of upcoming increments
    # before the next archival pass is needed.
    "CLOUDBOX_SKILLS_AGENT_HANDOFF.md": 20_000,
    # Frozen ceiling: this file was already 159_084 bytes (2781 lines) when
    # this check was introduced (2026-08-18), with an explicit "add a new
    # entry at the top every increment" maintenance rule and no archival
    # step -- the same unbounded-growth shape CLOUDBOX_SKILLS_AGENT_HANDOFF.md
    # had. Frozen rather than immediately demanding a fix, matching
    # docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md's MAP-R08 (recorded, not yet
    # implemented): the real fix is an index-based rewrite of this file's
    # maintenance rule, not a one-time trim.
    "docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md": 159_084,
}
for relative, budget in LIVING_DOC_BUDGET_BYTES.items():
    path = ROOT / relative
    if not path.is_file():
        continue
    size = len(path.read_bytes())
    if size > budget:
        errors.append(
            f"{relative} is {size} bytes; living-document budget is {budget}"
        )

handoff = ROOT / "CLOUDBOX_SKILLS_AGENT_HANDOFF.md"
if handoff.is_file():
    text = handoff.read_text(encoding="utf-8")
    for forbidden in (
        "access token:",
        "api key:",
    ):
        if re.search(re.escape(forbidden), text, re.I):
            errors.append(f"handoff must not contain credential material marker: {forbidden}")
    for command in (
        "./cloudbox-skills-resume --provider ollama --force-eval",
        "./cloudbox-skills-resume --provider codex --force-eval",
        "./cloudbox-skills-resume --provider claude --force-eval",
    ):
        if command not in text:
            errors.append(f"handoff missing continuation command: {command}")

print("Validated CloudSkill design, history, and agent-handoff documentation")
print(f"Living-document budgets checked: {', '.join(sorted(LIVING_DOC_BUDGET_BYTES))}")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
