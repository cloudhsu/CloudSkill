from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SKILLS_DIR = ROOT / ".agents" / "skills"
PORTABILITY_PATH = ROOT / "config" / "skill-portability.json"

errors: list[str] = []

try:
    portability = json.loads(PORTABILITY_PATH.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"ERROR: cannot read {PORTABILITY_PATH.relative_to(ROOT)}: {exc}")
    sys.exit(1)

tiers = portability.get("tiers")
skills_classified = portability.get("skills")
if not isinstance(tiers, dict) or not tiers:
    errors.append("skill-portability.json must declare a non-empty 'tiers' object")
    tiers = {}
if not isinstance(skills_classified, dict) or not skills_classified:
    errors.append("skill-portability.json must declare a non-empty 'skills' object")
    skills_classified = {}

actual_skill_names = sorted(
    path.parent.name for path in SKILLS_DIR.glob("*/SKILL.md")
)
classified_names = sorted(skills_classified)

_distribution_path = ROOT / "config" / "skill-distribution.json"
_evolution_names = set()
if _distribution_path.exists():
    _tiers = json.loads(_distribution_path.read_text(encoding="utf-8")).get("skills", {})
    _evolution_names = {name for name, tier in _tiers.items() if tier == "evolution-pack"}

if actual_skill_names != classified_names:
    missing = sorted(set(actual_skill_names) - set(classified_names))
    # An evolution-pack skill legitimately has no directory in a public
    # checkout (scripts/export_public_bundle.py never copies it) -- its
    # classification staying in skill-portability.json is expected, not stale.
    orphaned = sorted(set(classified_names) - set(actual_skill_names) - _evolution_names)
    if missing:
        errors.append(f"skill-portability.json is missing classification for: {missing}")
    if orphaned:
        errors.append(f"skill-portability.json classifies Skill(s) that no longer exist: {orphaned}")

for skill_name, tier in skills_classified.items():
    if tier not in tiers:
        errors.append(f"skill-portability.json/{skill_name}: tier {tier!r} is not declared in 'tiers'")

# Positive/negative signal check: a Skill classified "portable" must not
# actually reference CloudSkill-repository-relative CLI tooling. This is the
# safety-critical direction -- shipping a "portable" Skill that silently
# depends on scripts/*.py would break the moment someone uploads it to a
# sandboxed surface. The reverse (cli-only/hybrid with no matched signal) is
# not flagged: a Skill can legitimately need CLI access for reasons this
# regex heuristic cannot see.
CLI_DEPENDENCY_PATTERN = re.compile(
    r"scripts/[a-z_]+\.py|cloudskill-(eval|resume)|\.local/|CloudSkill repository|repository-relative"
)
for skill_name in actual_skill_names:
    tier = skills_classified.get(skill_name)
    if tier != "portable":
        continue
    skill_dir = SKILLS_DIR / skill_name
    hits = [
        str(path.relative_to(ROOT))
        for path in skill_dir.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json", ".yaml"}
        and CLI_DEPENDENCY_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore"))
    ]
    if hits:
        errors.append(
            f"skill-portability.json/{skill_name}: classified 'portable' but references "
            f"CloudSkill-repository-relative tooling: {hits}"
        )

# Executable proof, not just data validation: actually package every
# portable/hybrid Skill and verify each zip has the exact structure
# claude.ai/Desktop require (skill folder at the archive root, SKILL.md
# directly inside it).
spec = importlib.util.spec_from_file_location(
    "cloudskill_package_surface_skills", SCRIPTS / "package_surface_skills.py"
)
if spec is None or spec.loader is None:
    errors.append("cannot load scripts/package_surface_skills.py")
    packager = None
else:
    packager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packager)

if packager is not None:
    with tempfile.TemporaryDirectory(prefix="cloudskill-surface-package-") as tmp_name:
        tmp = Path(tmp_name)
        # Only attempt to package a skill that actually has a directory in
        # this checkout -- an evolution-pack skill classified here but absent
        # from a public checkout is expected, not a packaging failure.
        eligible = [
            name for name, tier in skills_classified.items()
            if tier in {"portable", "hybrid"} and name in actual_skill_names
        ]
        for skill_name in sorted(eligible):
            try:
                zip_path = packager.package_skill(skill_name, tmp)
            except FileNotFoundError as exc:
                errors.append(f"packaging {skill_name} failed: {exc}")
                continue
            errors.extend(packager.verify_zip_structure(zip_path, skill_name))

        # Negative safety check: a cli-only Skill must never be produced by
        # a default (no --include-cli-only) packaging run.
        cli_only = [name for name, tier in skills_classified.items() if tier == "cli-only"]
        for skill_name in cli_only:
            if (tmp / f"{skill_name}.zip").exists():
                errors.append(
                    f"{skill_name}: cli-only Skill was packaged without --include-cli-only being requested"
                )

# Documentation currency: every classified Skill name must appear in the
# human-readable matrix doc, so its tier tables cannot silently drift from
# the authoritative JSON when a Skill is added, removed, or reclassified.
matrix_path = ROOT / "docs" / "PLATFORM_SUPPORT_MATRIX.md"
if not matrix_path.is_file():
    errors.append(f"missing {matrix_path.relative_to(ROOT)}")
else:
    matrix_text = matrix_path.read_text(encoding="utf-8")
    for skill_name in actual_skill_names:
        if skill_name not in matrix_text:
            errors.append(f"docs/PLATFORM_SUPPORT_MATRIX.md does not mention Skill: {skill_name}")

print(
    f"Validated Skill portability classification for {len(actual_skill_names)} Skill(s) "
    f"and the claude.ai/Desktop packaging zip structure."
)
print("NOTE: this validator does not upload anything or call Codex, Ollama, Claude, or another model.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
