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

semantic_cases = [
    ({"introduced_version": "unreleased", "last_reviewed_version": "5.8.0"}, "5.8.0", "shipped Skill cannot remain unreleased"),
    ({"introduced_version": "5.7.0", "last_reviewed_version": "5.6.0", "next_review_triggers": ["the skill has not been reviewed for two feature releases"]}, "5.8.0", "two feature releases require review"),
]
for payload, current_version, label in semantic_cases:
    if not module.lifecycle_semantic_errors(payload, current_version):
        raise SystemExit(f"lifecycle semantic mutation was accepted: {label}")
if module.lifecycle_semantic_errors(
    {"introduced_version": "5.7.0", "last_reviewed_version": "5.8.0", "next_review_triggers": ["the skill has not been reviewed for two feature releases"]},
    "6.0.0",
):
    raise SystemExit("major-version boundary was falsely counted as two known feature releases")

# Mechanical refresh must preserve manually sourced lifecycle truth rather than
# inventing release/review evidence to make an audit green.
preserved = module.lifecycle_payload(
    "fixture", policy={"review_triggers": []}, routing={}, behavior={},
    existing={"stage": "experimental", "introduced_version": "unreleased", "last_reviewed_version": "5.6.0"},
    default_stage="active",
)
if (preserved["stage"], preserved["introduced_version"], preserved["last_reviewed_version"]) != ("experimental", "unreleased", "5.6.0"):
    raise SystemExit("mechanical refresh invented lifecycle evidence")

original_version_path = module.VERSION
module.VERSION = ROOT / "missing-version-fixture"
try:
    missing_version_errors = module.audit(check=False)
except FileNotFoundError as exc:
    raise SystemExit(f"missing VERSION crashed lifecycle audit: {exc}") from exc
finally:
    module.VERSION = original_version_path
if not any("VERSION" in error for error in missing_version_errors):
    raise SystemExit("missing VERSION did not produce an auditable lifecycle error")

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
