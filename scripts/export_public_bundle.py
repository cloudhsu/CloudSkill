"""Export the public/marketplace-safe subset of this repository.

Reads config/skill-distribution.json as the single source of truth for which
skills are 'core' (public) vs 'evolution-pack' (private-only), then copies
every git-tracked file EXCEPT:

- .agents/skills/<name>/ for any evolution-pack skill
- private-plugin/ and private-gemini-plugin/ (private-only distributions)
- any evals/behavior/cases/*.json whose top-level "skill" field names an
  evolution-pack skill
- evals/skill-routing-cases.csv, with rows whose expected_skill is an
  evolution-pack skill dropped (the file itself is shared, not exclusive)
- .agents/plugins/marketplace.json and .claude-plugin/marketplace.json, with
  any plugin entry whose name contains "private" dropped (the files themselves
  are shared, not exclusive)
- .claude-plugin/plugin.json and .codex-plugin/plugin.json, with
  homepage/repository/websiteURL rewritten from the private repo URL to the
  public PUBLIC_REPO_URL (this repo's own plugin.json is correctly
  self-referential to the private repo; the public mirror needs its own URL,
  not a copy of the private one -- see the 2026-08-15 incident where this got
  fixed by hand once and would have silently regressed on the next sync
  without this rewrite)

This exists so "which files are safe to publish" is answered by running this
script against config/skill-distribution.json, not by a person remembering
to filter during a sync -- see the 2026-08-15 incident where the temporary
full-sync exception mirrored all three evolution-pack skills into the public
CloudSkill repo unfiltered.

Usage:
    python3 scripts/export_public_bundle.py --dest /path/to/CloudSkill [--ref HEAD]

After running, regenerate SKILL_MANIFEST.json in --dest with
`python3 scripts/validate_pack.py` (run from --dest) so it reflects only the
copied skills, then run `python3 scripts/run_all_checks.py` there before
committing.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

PRIVATE_REPO_URL = "https://github.com/cloudhsu/cloudbox-skills"
PUBLIC_REPO_URL = "https://github.com/cloudhsu/CloudSkill"

# Private mining/evolution infrastructure that lives outside any tiered skill
# folder (shared scripts/config/workflow, not skill content) -- found by an
# explicit audit on 2026-08-15. Extend this list if a future private-only
# script/config/workflow is added outside .agents/skills/.
PRIVATE_INFRASTRUCTURE_PATHS = {
    "scripts/capture_eval_candidate.py",
    "scripts/sync_eval_exchange.py",
    "scripts/validate_interaction_capture.py",
    "scripts/import_eval_candidates.py",
    "config/cloudbox-skills-config.template.json",
    # Runtime-eval/multimodel-panel harness: "the runtime-eval harness used
    # to maintain CloudBox's own routing accuracy" per skill-distribution.json's
    # own evolution-pack definition. Added 2026-08-15 alongside moving the
    # README's "Runtime model evaluations" section to private-plugin/README.md.
    "scripts/run_runtime_evals.py",
    # Real-execution ablation-study runner, same category as run_runtime_evals.py
    # above (imports runtime_eval_common.py / claude_eval_adapter.py directly).
    # Added 2026-08-22 alongside the first real ablation run (Vikunja
    # cloudbox-skills #10).
    "scripts/run_ablation_study.py",
    "scripts/grade_runtime_evals.py",
    "scripts/validate_runtime_evals.py",
    "scripts/validate_multimodel_panel.py",
    "scripts/multimodel_panel_contract.py",
    "scripts/run_multimodel_panel.py",
    "scripts/claude_eval_adapter.py",
    "scripts/codex_eval_adapter.py",
    "scripts/providers_contract.py",
    "scripts/validate_providers_contract.py",
    "scripts/run_local_eval_review.py",
    "scripts/validate_local_eval_debugging.py",
    "scripts/validate_codex_eval_path.py",
    "cloudbox-skills-eval",
    "cloudbox-skills-eval-codex",
    "cloudbox-skills-eval-claude",
    # These three exist only to check consistency across the runtime-eval
    # harness scripts above (every consumer of behavior_output_contract.py /
    # runtime_eval_common.py / canary.json / routing-decision.schema.json is
    # itself already excluded) -- confirmed by an explicit consumer audit
    # 2026-08-15 before excluding, not assumed from the filename.
    "scripts/validate_behavior_contract.py",
    "scripts/behavior_output_contract.py",
    "scripts/runtime_eval_common.py",
    # Advisory helpers for reviewing private Eval Inbox candidates
    # (developing-eval, private-meta) -- meaningless to a public consumer,
    # who has no .local/eval-inbox/ to run them against. rule_strength.py
    # added 2026-08-21; detect_candidate_similarity.py and
    # prioritize_eval_inbox.py added 2026-08-22, same category, gated
    # before this script's first export run touching them.
    "scripts/rule_strength.py",
    "scripts/detect_candidate_similarity.py",
    "scripts/prioritize_eval_inbox.py",
    # Syncs private-plugin/codex-skills/ from the canonical evolution-pack
    # Skills -- both source and destination are private-only, so this script
    # is a no-op in a public checkout (private-plugin/ is already excluded
    # above). Caught 2026-08-21 during the first real export run.
    "scripts/sync_private_codex_plugin.py",
    "evals/runtime/contracts/behavior-output-contract.json",
    "evals/runtime/schemas/routing-decision.schema.json",
    "evals/runtime/cases/canary.json",
    # Product-specific game benchmark and taxonomy are private alongside the
    # game Skills; do not mirror them into the public Core export.
    "evals/runtime/cases/game-skills-benchmark.json",
    "evals/runtime/cases/game-skills-behavior-rubrics.json",
    # Mixes private-game (cloudbox-game-migration, game-quality-and-release-
    # gates, gameplay-core-modernization) and private-meta
    # (local-runtime-eval-debugging) routing prompts in one file, same
    # pattern as canary.json above -- excluded wholesale rather than split.
    # Added 2026-08-22, caught before this script's first export run
    # touching it.
    "evals/runtime/cases/worst-margin-skills-routing.json",
    # Same runtime-eval-harness-is-private-infrastructure category as
    # canary.json and worst-margin-skills-routing.json above; negative
    # routing cases for skills touched during this run's 52-case pass.
    # Added 2026-08-22, caught before this script's first export run
    # touching it.
    "evals/runtime/cases/touched-skills-negative-routing.json",
    # Same category, first-routing-pass sweep across all untested skills;
    # mixes private-game (cloudbox-game-migration, game-quality-and-
    # release-gates, gameplay-core-modernization) and private-meta
    # (local-runtime-eval-debugging) prompts with public-tier skills.
    # Added 2026-08-22, caught before this script's first export run
    # touching it.
    "evals/runtime/cases/coverage-sweep-first-routing-pass.json",
    "config/skill-domain-catalog.json",
    "docs/GAME_SKILL_CATALOG.md",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_tracked_files(ref: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def dest_tracked_files(dest_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=dest_root, capture_output=True, text=True,
    )
    if result.returncode:
        return []
    return [line for line in result.stdout.splitlines() if line]


# Files the public repo legitimately owns and this script never sources from
# the private repo -- never prune these even though they aren't in copied_paths.
DEST_ONLY_KEEP = {"LICENSE"}


def read_at_ref(ref: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=ROOT, capture_output=True, check=True,
    )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", required=True, help="Path to the public repo working tree")
    parser.add_argument("--ref", default="HEAD", help="Git ref to export from (default: HEAD)")
    args = parser.parse_args()

    dest_root = Path(args.dest).resolve()
    if not dest_root.is_dir():
        print(f"ERROR: --dest does not exist or is not a directory: {dest_root}", file=sys.stderr)
        return 1

    distribution = load_json(ROOT / "config" / "skill-distribution.json")
    tiers = distribution.get("skills", {})
    # Any tier other than "core" is private -- this covers evolution-pack's
    # sub-tiers (private-meta, private-game, private-operation, private-art,
    # and any future private sub-tier) without needing a script edit each
    # time a new private sub-tier is introduced.
    evolution_names = sorted(name for name, tier in tiers.items() if tier != "core")
    evolution_prefixes = tuple(f".agents/skills/{name}/" for name in evolution_names)

    excluded_paths: list[str] = []
    copied_paths: list[str] = []

    for relative in git_tracked_files(args.ref):
        if relative.startswith(evolution_prefixes):
            excluded_paths.append(relative)
            continue
        if relative == "private-plugin" or relative.startswith("private-plugin/"):
            excluded_paths.append(relative)
            continue
        if relative == "private-gemini-plugin" or relative.startswith("private-gemini-plugin/"):
            excluded_paths.append(relative)
            continue
        if relative in PRIVATE_INFRASTRUCTURE_PATHS:
            excluded_paths.append(relative)
            continue

        content = read_at_ref(args.ref, relative)

        if relative.startswith("evals/behavior/cases/") and relative.endswith(".json"):
            try:
                case_doc = json.loads(content)
            except json.JSONDecodeError:
                case_doc = {}
            if case_doc.get("skill") in evolution_names:
                excluded_paths.append(relative)
                continue

        dest_path = dest_root / relative
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if relative == "evals/skill-routing-cases.csv":
            text = content.decode("utf-8")
            reader = csv.DictReader(text.splitlines())
            fieldnames = reader.fieldnames or []
            kept_rows = [row for row in reader if row.get("expected_skill") not in evolution_names]
            with dest_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(kept_rows)
            copied_paths.append(f"{relative} (filtered)")
            continue

        if relative in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
            doc = json.loads(content)
            doc["plugins"] = [p for p in doc.get("plugins", []) if "private" not in p.get("name", "")]
            dest_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            copied_paths.append(f"{relative} (filtered)")
            continue

        if relative in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            text = content.decode("utf-8").replace(PRIVATE_REPO_URL, PUBLIC_REPO_URL)
            dest_path.write_text(text, encoding="utf-8")
            copied_paths.append(f"{relative} (URL rewritten)")
            continue

        dest_path.write_bytes(content)
        copied_paths.append(relative)

    # Prune anything already tracked in --dest that this run did not write --
    # a copy-only export leaves stale leftovers from an earlier, less careful
    # sync (e.g. evolution-pack folders mirrored before this script existed)
    # sitting there forever. See the 2026-08-15 incident: this is exactly how
    # the original leak would have kept surviving every future export.
    written = {p.split(" (")[0] for p in copied_paths}
    pruned_paths: list[str] = []
    for relative in dest_tracked_files(dest_root):
        if relative in written or relative in DEST_ONLY_KEEP:
            continue
        target = dest_root / relative
        if target.is_file():
            target.unlink()
            pruned_paths.append(relative)
    # Remove now-empty directories left behind by pruned files.
    for dirpath, dirnames, filenames in list(os.walk(dest_root, topdown=False)):
        if ".git" in Path(dirpath).parts:
            continue
        p = Path(dirpath)
        if p != dest_root and not any(p.iterdir()):
            p.rmdir()

    print(f"Exported {len(copied_paths)} files to {dest_root}")
    print(f"Excluded {len(excluded_paths)} evolution-pack/private-only paths:")
    for path in excluded_paths:
        print(f"  - {path}")
    print(f"Pruned {len(pruned_paths)} stale files no longer sourced from the private repo:")
    for path in pruned_paths:
        print(f"  - {path}")
    print()
    print("Next: cd into --dest, run scripts/validate_pack.py to regenerate")
    print("SKILL_MANIFEST.json, then scripts/run_all_checks.py before committing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
