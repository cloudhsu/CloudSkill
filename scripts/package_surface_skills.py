"""Package individual Skills as claude.ai / Claude Desktop Custom Skill zips.

claude.ai and Claude Desktop upload one Skill at a time as a zip through
Customize/Settings -> Skills -> Upload, and require the skill folder itself
to sit at the root of the archive (`<skill-name>/SKILL.md`, not a nested or
flattened layout) -- this is different from the whole-repository plugin
marketplace bundle `cloudskill-eval`/`install.sh` produce for Codex/Claude
Code CLI.

Only packages Skills classified `portable` or `hybrid` in
`config/skill-portability.json`; `cli-only` Skills assume filesystem/
subprocess access to this repository that a sandboxed surface does not have,
per the requirements confirmed in Anthropic's Agent Skills documentation
(https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
PORTABILITY_PATH = ROOT / "config" / "skill-portability.json"
DEFAULT_OUTPUT_DIR = ROOT / ".local" / "surface-packages"


def load_portability() -> dict[str, Any]:
    return json.loads(PORTABILITY_PATH.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package Skills as individual claude.ai/Claude Desktop Custom Skill zips."
    )
    parser.add_argument(
        "--skill", action="append", default=[], help="Package only this Skill (repeatable). Default: all eligible Skills."
    )
    parser.add_argument(
        "--include-cli-only",
        action="store_true",
        help="Also package cli-only Skills. They will not function on a sandboxed surface; use only for local inspection.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def package_skill(skill_name: str, output_dir: Path) -> Path:
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.is_dir():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise FileNotFoundError(f"{skill_name}: missing SKILL.md")

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{skill_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_dir():
                continue
            if path.name in {".DS_Store"} or "__pycache__" in path.parts:
                continue
            # Archive name is relative to SKILLS_DIR so the skill folder
            # itself -- not an absolute path, not the bare file -- sits at
            # the root of the zip, per claude.ai's required structure.
            archive.write(path, arcname=str(path.relative_to(SKILLS_DIR)))
    return zip_path


def verify_zip_structure(zip_path: Path, skill_name: str) -> list[str]:
    """Structural self-check matching claude.ai's documented requirement:
    opening the archive, the skill folder is the first thing you see, and
    SKILL.md sits directly inside it -- not nested deeper, not flattened."""
    errors: list[str] = []
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    expected_skill_md = f"{skill_name}/SKILL.md"
    if expected_skill_md not in names:
        errors.append(f"{zip_path.name}: {expected_skill_md} not found at the expected root-relative path")
    if any(not name.startswith(f"{skill_name}/") for name in names):
        errors.append(f"{zip_path.name}: contains an entry outside the {skill_name}/ folder")
    return errors


def main() -> int:
    args = parse_args()
    portability = load_portability()
    skills = portability.get("skills", {})

    if args.skill:
        targets = args.skill
        unknown = [name for name in targets if name not in skills]
        if unknown:
            print(f"ERROR: unknown Skill(s), not in {PORTABILITY_PATH.relative_to(ROOT)}: {unknown}", file=sys.stderr)
            return 2
    else:
        allowed_tiers = {"portable", "hybrid"} | ({"cli-only"} if args.include_cli_only else set())
        targets = [name for name, tier in skills.items() if tier in allowed_tiers]

    errors: list[str] = []
    packaged: list[Path] = []
    for skill_name in sorted(targets):
        tier = skills.get(skill_name, "unknown")
        if tier == "cli-only" and not args.include_cli_only:
            print(f"SKIP {skill_name}: cli-only tier, will not function on a sandboxed surface", file=sys.stderr)
            continue
        try:
            zip_path = package_skill(skill_name, args.output_dir)
        except FileNotFoundError as exc:
            errors.append(str(exc))
            continue
        errors.extend(verify_zip_structure(zip_path, skill_name))
        packaged.append(zip_path)
        print(f"{tier}: {zip_path}")

    print(f"Packaged {len(packaged)} Skill(s) to {args.output_dir}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
