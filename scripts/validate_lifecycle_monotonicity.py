from __future__ import annotations

"""Structurally enforce this repository's own "append, never overwrite"
convention for a Skill's `lifecycle.json` `notes` field.

This is the discrete-math side of the two follow-ups discussed alongside
scripts/eval_confidence_report.py: a grow-only (join-semilattice) merge --
every commit's `notes` value must be the previous commit's value with text
appended, never replaced or shortened. That gives a structural guarantee
("this Skill's recorded history never loses a fact") independent of any
statistical evidence about whether a given change was actually an
improvement.

Compares each `.agents/skills/*/lifecycle.json` at HEAD against the same
path at HEAD~1 (skipped entirely if HEAD~1 doesn't resolve, e.g. a
single-commit history, or if the file didn't exist at HEAD~1, e.g. a new
Skill). Wired into run_all_checks.py -- this is a structural CI-time check,
not an advisory tool.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
RESET_MARKER_RE = re.compile(r"materially refactored", re.IGNORECASE)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_support import run_git_command  # noqa: E402


def show_at(ref: str, relative: str) -> str | None:
    result = run_git_command(["show", f"{ref}:{relative}"], cwd=ROOT)
    if not result.ok:
        return None
    return result.stdout


def main() -> int:
    parent_check = run_git_command(["rev-parse", "--verify", "HEAD~1"], cwd=ROOT)
    if not parent_check.ok:
        print("HEAD~1 does not resolve (single-commit history) -- nothing to compare, skipping.")
        return 0

    diff_result = run_git_command(
        ["diff", "--name-only", "HEAD~1", "HEAD", "--", ".agents/skills/*/lifecycle.json"],
        cwd=ROOT,
    )
    if not diff_result.ok:
        print("ERROR: could not compute changed lifecycle.json files", file=sys.stderr)
        return 1

    changed = [line.strip() for line in diff_result.stdout.splitlines() if line.strip()]
    errors: list[str] = []
    checked = 0

    for relative in changed:
        old_text = show_at("HEAD~1", relative)
        new_text = show_at("HEAD", relative)
        if old_text is None:
            continue  # new Skill this commit; nothing prior to compare against
        if new_text is None:
            errors.append(f"{relative}: existed at HEAD~1 but is missing at HEAD (deleted lifecycle.json)")
            continue
        try:
            old_notes = json.loads(old_text).get("notes", "")
            new_notes = json.loads(new_text).get("notes", "")
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON, cannot check monotonicity ({exc})")
            continue
        checked += 1
        if not isinstance(old_notes, str) or not isinstance(new_notes, str):
            continue
        if not new_notes.startswith(old_notes.rstrip()):
            # A material Skill refactor/split (e.g. developing-eval carved out
            # of developing-skills at 7.6.9) legitimately starts a fresh
            # evidence baseline instead of appending to a now-inaccurate
            # history -- this repository already has that exact convention
            # (see e.g. wph-equipment-simulator-development's own notes).
            # Require it to say so explicitly rather than silently allowing
            # any reset: the same self-disclosure bar every other honesty
            # claim in this repo is held to.
            if RESET_MARKER_RE.search(new_notes[:200]):
                print(
                    f"NOTE: {relative}: notes field was reset, not appended -- allowed because "
                    "it self-discloses a material refactor ('materially refactored') near the "
                    "start of the new text."
                )
                continue
            errors.append(
                f"{relative}: notes field was not appended to -- previous content is not a "
                "prefix of the new content (overwritten or shortened, violating the "
                "append-only convention). If this is a deliberate reset after a material "
                "Skill refactor/split, say so explicitly: start the new notes with "
                "'Materially refactored ...' to self-disclose it, matching this "
                "repository's existing convention."
            )

    print(f"Checked {checked} changed lifecycle.json file(s) for append-only notes.")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
