from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents/skills"
DEVELOPING_SKILLS = SKILLS_DIR / "developing-skills/SKILL.md"

# Default per-skill SKILL.md budget in UTF-8 bytes. SKILL.md loads into
# context when the router selects that skill; conditional detail belongs in
# references/, not here. This is a repository gate measured from
# read_bytes(), not a provider tokenizer or billing-token measurement.
#
# Updated 2026-08-25 by explicit repository-owner decision from 10,500 to
# 20,000 bytes after inventorying all 41 current Skills: the largest main
# file was 14,876 bytes and all current files fit below the new ceiling.
DEFAULT_MAX_BYTES = 20_000

# The historical grandfathered ceilings were retired with the 20,000-byte
# policy. Keep the named constant so the validation/reporting flow remains
# explicit and future policy changes have one place to review.
GRANDFATHERED_CEILINGS = {}


def main() -> int:
    errors = []
    reports = []

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        skill_id = skill_dir.name
        data = skill_md.read_bytes()
        budget = GRANDFATHERED_CEILINGS.get(skill_id, DEFAULT_MAX_BYTES)
        if len(data) > budget:
            note = " (frozen ceiling, pending a slimming pass)" if skill_id in GRANDFATHERED_CEILINGS else ""
            errors.append(
                f"{skill_id}: SKILL.md is {len(data)} bytes; budget is {budget}{note}"
            )
        else:
            reports.append(f"{skill_id}: {len(data)} bytes (budget {budget})")

    text = DEVELOPING_SKILLS.read_text(encoding="utf-8")
    required_main_invariants = {
        "RED evidence": "RED evidence",
        "authoritative owner": "authoritative owner",
        "Never store raw transcripts": "Never store raw transcripts",
        "Report execution truthfully": "Report execution truthfully",
    }
    for label, marker in required_main_invariants.items():
        if marker.lower() not in text.lower():
            errors.append(f"developing-skills: missing universal main-file invariant: {label}")

    required_routes = {
        "lifecycle and release": "references/skill-lifecycle-standard.md",
    }
    for label, path in required_routes.items():
        if path not in text:
            errors.append(
                f"developing-skills: missing direct conditional reference route: {label} -> {path}"
            )

    developing_eval = SKILLS_DIR / "developing-eval/SKILL.md"
    if developing_eval.is_file():
        eval_text = developing_eval.read_text(encoding="utf-8")
        eval_routes = {
            "interaction capture": "references/interaction-eval-capture.md",
            "conversation/project mining": "references/conversation-derived-optimization.md",
        }
        for label, path in eval_routes.items():
            if path not in eval_text:
                errors.append(
                    f"developing-eval: missing direct conditional reference route: {label} -> {path}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Validated SKILL.md context budget for {len(reports)} skills (default budget {DEFAULT_MAX_BYTES} bytes).")
    if GRANDFATHERED_CEILINGS:
        print(f"Grandfathered (frozen, no growth room): {', '.join(sorted(GRANDFATHERED_CEILINGS))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
