"""Synchronize Gemini extension Skill projections from canonical Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".agents" / "skills"
PUBLIC = ROOT / "gemini-plugin" / "skills"
PRIVATE = ROOT / "private-gemini-plugin" / "skills"


def tiered_names() -> tuple[list[str], list[str]]:
    distribution = json.loads(
        (ROOT / "config" / "skill-distribution.json").read_text(encoding="utf-8")
    )
    skills = distribution.get("skills", {})
    public = sorted(name for name, tier in skills.items() if tier == "core")
    private = sorted(name for name, tier in skills.items() if tier != "core")
    return public, private


def files(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed in Gemini projection: {path}")
        if path.is_file():
            relative = str(path.relative_to(root)).replace("\\", "/")
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def projection_matches(target: Path, names: list[str]) -> bool:
    actual = sorted(path.name for path in target.iterdir() if path.is_dir()) if target.is_dir() else []
    if actual != names:
        return False
    return all(files(CANONICAL / name) == files(target / name) for name in names)


def sync_projection(target: Path, names: list[str]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    wanted = set(names)
    for child in target.iterdir():
        if child.name not in wanted:
            if child.is_symlink() or child.is_file():
                child.unlink()
            else:
                shutil.rmtree(child)
    for name in names:
        source = CANONICAL / name
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"canonical Skill is missing: {name}")
        files(source)  # Reject source symlinks before copying.
        destination = target / name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify projections without writing")
    args = parser.parse_args()
    public, private = tiered_names()

    if args.check:
        errors = []
        if not projection_matches(PUBLIC, public):
            errors.append("public Gemini projection is stale")
        private_sources_exist = all((CANONICAL / name).is_dir() for name in private)
        if private_sources_exist and not projection_matches(PRIVATE, private):
            errors.append("private Gemini projection is stale")
        if not private_sources_exist and PRIVATE.parent.exists():
            errors.append("public checkout must not contain the private Gemini projection")
        for error in errors:
            print(f"ERROR: {error}")
        if errors:
            return 1
        print("Gemini Skill projections match canonical distribution tiers")
        return 0

    sync_projection(PUBLIC, public)
    if all((CANONICAL / name).is_dir() for name in private):
        sync_projection(PRIVATE, private)
    print("Synchronized Gemini Skill projections from canonical Skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
