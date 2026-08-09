from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "manage_skill.py"

spec = importlib.util.spec_from_file_location("cloudskill_manage_skill", MODULE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f"cannot load {MODULE_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

errors = module.audit(check=False)

# The standardization owner must declare the lifecycle reference and CLI.
developing = (ROOT / ".agents/skills/developing-skills/SKILL.md").read_text(encoding="utf-8")
for marker in (
    "references/skill-lifecycle-standard.md",
    "scripts/manage_skill.py",
    "draft",
    "experimental",
    "active",
    "stable",
    "deprecated",
):
    if marker not in developing:
        errors.append(f"developing-skills missing lifecycle marker: {marker}")

# The policy and templates are release-critical.
for relative in (
    "config/skill-lifecycle-policy.json",
    ".agents/skills/developing-skills/references/skill-lifecycle-standard.md",
    ".agents/skills/developing-skills/assets/SKILL_PROPOSAL.template.md",
    ".agents/skills/developing-skills/assets/SKILL_LIFECYCLE.template.json",
    ".agents/skills/developing-skills/assets/SKILL_RELEASE_EVIDENCE.template.md",
):
    if not (ROOT / relative).is_file():
        errors.append(f"missing lifecycle standard file: {relative}")

for error in errors:
    print(f"ERROR: {error}")
print(f"Validated standardized lifecycle evidence for {len(module.skill_names())} skills.")
sys.exit(1 if errors else 0)
