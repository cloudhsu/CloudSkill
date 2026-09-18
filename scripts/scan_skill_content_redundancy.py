from __future__ import annotations

"""Flag near-duplicate paragraphs WITHIN one Skill's own content (SKILL.md
plus its references/*.md files) -- deterministic, no model call.

Gap this closes (Forgejo #2, cloudbox-skills): the mutation-testing
methodology in `evals/runtime/README.md` already lets a human/agent
confirm or reject whether ONE named paragraph is load-bearing for ONE named
behavior case, by temporarily reverting it and re-running the case (see
also `run_ablation_study.py` for the cross-skill composition variant). That
answers "is this paragraph load-bearing for a case we already have," but it
cannot by itself find TWO paragraphs saying the same thing when no case
exercises either one -- both would read "not load-bearing" under mutation
testing, which looks identical to genuine dead weight but is not the same
finding. This script is the other half of the two-stage pipeline the
project's own ablation backlog named as unbuilt (2026-09-06): a cheap,
explainable PROPOSAL stage that surfaces likely-duplicate paragraph pairs
for a human or the mutation-testing methodology to then CONFIRM or REJECT.
It never ablates, edits, deletes, or judges load-bearing-ness itself.

Method: token-set Jaccard similarity per paragraph pair, the same
deterministic, explainable metric already used by
`detect_candidate_similarity.py` for Eval-Inbox candidates -- reused here
for consistency, not reinvented. A "paragraph" is a blank-line-delimited
block of prose after stripping markdown table rows, bare bullet lists
under a length floor, and code fences (those produce spurious overlap --
shared punctuation/keywords, not shared prose meaning). Comparison is
scoped to ONE skill's own SKILL.md + references/*.md at a time, per #2's
own framing ("a single skill's own content") -- cross-skill duplication
(the same generic advice repeated in several different skills) is a
different, real question this script does not answer.

Advisory only, like its Eval-Inbox sibling: a flagged pair is a candidate
to actually go read, and if it looks like genuine dead weight, verify with
the real mutation-testing recipe in evals/runtime/README.md before cutting
anything -- this script's score is not evidence a paragraph is safe to
remove, only that it resembles another paragraph closely enough to be
worth a human's time.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".agents" / "skills"

_WORD_RE = re.compile(r"[a-z0-9]+")
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# Paragraphs shorter than this (in whitespace-collapsed characters) are
# skipped -- a two-line bullet or a lone heading produces noisy, low-value
# overlap ("Do not." matches "Do not." everywhere) rather than a genuine
# duplicated-explanation signal.
MIN_PARAGRAPH_CHARS = 120

# Calibrated the same way as detect_candidate_similarity.py's threshold:
# against real paragraph pairs in this repository rather than picked blind.
# See the --self-test fixture and the 2026-09-19 pilot run recorded in
# Forgejo #2 for the real pairs this was checked against.
DEFAULT_THRESHOLD = 0.35


class Paragraph(NamedTuple):
    source: str  # relative path, e.g. "SKILL.md" or "references/foo.md"
    index: int  # paragraph position within that file, 0-based
    text: str
    tokens: frozenset[str]


def _strip_code_fences(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text)


def _is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def extract_paragraphs(source: str, text: str) -> list[Paragraph]:
    text = _strip_code_fences(text)
    blocks = re.split(r"\n\s*\n", text)
    paragraphs: list[Paragraph] = []
    for i, block in enumerate(blocks):
        lines = [ln for ln in block.splitlines() if not _is_table_row(ln)]
        collapsed = " ".join(ln.strip() for ln in lines if ln.strip())
        # Drop a leading markdown heading marker so "## Scope Discipline"
        # alone (a 2-3 word heading with no body left after table-row
        # stripping) does not masquerade as a real paragraph.
        collapsed_for_length = re.sub(r"^#{1,6}\s*", "", collapsed)
        if len(collapsed_for_length) < MIN_PARAGRAPH_CHARS:
            continue
        tokens = frozenset(_WORD_RE.findall(collapsed.lower()))
        if not tokens:
            continue
        paragraphs.append(Paragraph(source=source, index=i, text=collapsed, tokens=tokens))
    return paragraphs


def jaccard_similarity(a: frozenset[str], b: frozenset[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def collect_skill_paragraphs(skill_dir: Path) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        paragraphs.extend(extract_paragraphs("SKILL.md", skill_md.read_text(encoding="utf-8")))
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for ref_path in sorted(refs_dir.glob("*.md")):
            rel = f"references/{ref_path.name}"
            paragraphs.extend(extract_paragraphs(rel, ref_path.read_text(encoding="utf-8")))
    return paragraphs


def find_near_duplicates(
    paragraphs: list[Paragraph], *, threshold: float = DEFAULT_THRESHOLD
) -> list[tuple[Paragraph, Paragraph, float]]:
    hits: list[tuple[Paragraph, Paragraph, float]] = []
    for i in range(len(paragraphs)):
        for j in range(i + 1, len(paragraphs)):
            a, b = paragraphs[i], paragraphs[j]
            score = jaccard_similarity(a.tokens, b.tokens)
            if score >= threshold:
                hits.append((a, b, score))
    hits.sort(key=lambda h: h[2], reverse=True)
    return hits


def _self_test() -> int:
    # A real, mechanically-obvious case: the same bullet-list warning
    # repeated verbatim in two different reference files of one skill
    # (a plausible copy-paste-and-forget pattern), contrasted with two
    # unrelated paragraphs of comparable length from this repo's own
    # style so the fixture is not an artificial toy sentence.
    real_duplicate_a = Paragraph(
        source="references/a.md",
        index=0,
        text=(
            "Do not pass a powerful facade or raw database object when a "
            "narrower port is sufficient. Examples: query-only port, "
            "command-only port, unit-of-work port, clock, id generator, "
            "external service contract, mapper."
        ),
        tokens=frozenset(),
    )
    real_duplicate_b = Paragraph(
        source="references/b.md",
        index=3,
        text=(
            "Do not hand a powerful facade or a raw database object to a "
            "new component when a narrower port would do. Examples of a "
            "narrower port: a query-only port, a command-only port, a "
            "unit-of-work port, a clock, an id generator, an external "
            "service contract, or a mapper."
        ),
        tokens=frozenset(),
    )
    distinct = Paragraph(
        source="references/c.md",
        index=0,
        text=(
            "Capture what the system does, including undesirable behavior "
            "that callers may depend on. Useful evidence: public method "
            "list, API status and error contracts, database state before "
            "and after, audit and event order, snapshot semantics, "
            "version and health output."
        ),
        tokens=frozenset(),
    )
    fixtures = [
        p._replace(tokens=frozenset(_WORD_RE.findall(p.text.lower())))
        for p in (real_duplicate_a, real_duplicate_b, distinct)
    ]

    hits = find_near_duplicates(fixtures)
    failures = []
    pairs = {(h[0].source, h[1].source) for h in hits}
    if ("references/a.md", "references/b.md") not in pairs:
        failures.append("expected a/b to be flagged as a near-duplicate pair, was not")
    if any("references/c.md" in pair for pair in pairs):
        failures.append("expected the unrelated paragraph c not to be flagged against a/b")
    if jaccard_similarity(frozenset(), frozenset()) != 1.0:
        failures.append("jaccard_similarity(empty, empty) should be defined as 1.0")
    if jaccard_similarity(frozenset({"x"}), frozenset()) != 0.0:
        failures.append("jaccard_similarity(non-empty, empty) should be 0.0")

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for failure in failures:
            print(" -", failure, file=sys.stderr)
        return 1
    print(f"SELF-TEST PASSED ({len(hits)} pair(s) flagged from 3 fixture paragraphs, as expected)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill", nargs="?", help="Skill id under .agents/skills/ to scan. Omit with --all to scan every skill.")
    parser.add_argument("--all", action="store_true", help="Scan every skill under .agents/skills/ (one report per skill).")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help=f"Jaccard similarity cutoff (default {DEFAULT_THRESHOLD})")
    parser.add_argument("--self-test", action="store_true", help="run built-in regression checks and exit")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if not args.skill and not args.all:
        parser.error("pass a skill id, or --all to scan every skill")

    skill_dirs: list[Path]
    if args.all:
        skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file())
    else:
        skill_dir = SKILLS_DIR / args.skill
        if not (skill_dir / "SKILL.md").is_file():
            print(f"no SKILL.md found under {skill_dir}", file=sys.stderr)
            return 1
        skill_dirs = [skill_dir]

    any_hits = False
    for skill_dir in skill_dirs:
        paragraphs = collect_skill_paragraphs(skill_dir)
        hits = find_near_duplicates(paragraphs, threshold=args.threshold)
        if not hits:
            if not args.all:
                print(f"{skill_dir.name}: no pairs scored >= {args.threshold} across {len(paragraphs)} paragraph(s) (SKILL.md + references/).")
            continue
        any_hits = True
        print(f"{skill_dir.name}: {len(hits)} possible near-duplicate paragraph pair(s) across {len(paragraphs)} paragraph(s) (threshold {args.threshold}):")
        print("  Advisory only -- read both, then verify with the real mutation-testing recipe (evals/runtime/README.md) before cutting anything.")
        for a, b, score in hits:
            print(f"  {score:.2f}  {a.source}#{a.index}  <->  {b.source}#{b.index}")
            print(f"       A: {a.text[:160]}{'...' if len(a.text) > 160 else ''}")
            print(f"       B: {b.text[:160]}{'...' if len(b.text) > 160 else ''}")

    if args.all and not any_hits:
        print(f"No pairs scored >= {args.threshold} in any skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
