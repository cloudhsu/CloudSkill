from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

required_markers = {
    "CLOUDBOX_SKILLS_AGENT_HANDOFF.md": [
        "## Current repository state",
        "## Latest verified evidence before this increment",
        "## Open evolution items",
        "## Standard continuation commands",
        "## Evidence handoff contract",
        "## Behavior output contract authority",
        "Consumer registry",
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
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
