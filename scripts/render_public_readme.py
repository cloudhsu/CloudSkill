"""Render the public README Skill catalog from distribution and plugin data."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_distribution_contract import (  # noqa: E402
    PUBLIC_SKILL_TABLE_BEGIN,
    PUBLIC_SKILL_TABLE_END,
    render_public_skill_table,
    replace_marked_section,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    readme_path = root / "README.md"
    current = readme_path.read_text(encoding="utf-8")
    rendered = replace_marked_section(
        current,
        PUBLIC_SKILL_TABLE_BEGIN,
        PUBLIC_SKILL_TABLE_END,
        render_public_skill_table(root),
    )
    if current == rendered:
        print("Public README Skill table is current.")
        return 0
    if args.check:
        print("ERROR: public README Skill table is stale; run scripts/render_public_readme.py")
        return 1
    readme_path.write_text(rendered, encoding="utf-8")
    print("Updated public README Skill table.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
