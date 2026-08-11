from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/developing-skills/SKILL.md"
MAX_BYTES = 10_500


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    data = text.encode("utf-8")
    errors = []

    if len(data) > MAX_BYTES:
        errors.append(
            f"developing-skills default context is {len(data)} bytes; "
            f"budget is {MAX_BYTES}"
        )

    required_main_invariants = {
        "RED evidence": "RED evidence",
        "authoritative owner": "authoritative owner",
        "Never store raw transcripts": "Never store raw transcripts",
        "Report execution truthfully": "Report execution truthfully",
    }
    for label, marker in required_main_invariants.items():
        if marker.lower() not in text.lower():
            errors.append(f"missing universal main-file invariant: {label}")

    required_routes = {
        "interaction capture": "references/interaction-eval-capture.md",
        "conversation/project mining": "references/conversation-derived-optimization.md",
        "lifecycle and release": "references/skill-lifecycle-standard.md",
    }
    for label, path in required_routes.items():
        if path not in text:
            errors.append(f"missing direct conditional reference route: {label} -> {path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    approx_tokens = (len(data) + 3) // 4
    print(
        "Validated developing-skills context budget: "
        f"{len(text.splitlines())} lines, {len(text.split())} words, "
        f"{len(data)} bytes, ~{approx_tokens} comparative tokens"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
