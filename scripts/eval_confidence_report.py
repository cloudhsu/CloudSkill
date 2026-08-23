from __future__ import annotations

"""Report the statistical confidence a Skill's current case count actually
supports, using Hoeffding's inequality on routing/behavior cases treated as
Bernoulli pass/fail trials.

This exists to replace a qualitative "NOT RUN" / "case/contract-layer only"
disclosure with a quantified one when writing an Evolution-workflow release
report (see developing-skills/SKILL.md's "Report execution truthfully" step).
It reads case *counts* already recorded in each Skill's lifecycle.json --
no new data collection, no schema change, no live model execution.

Formula: for n Bernoulli trials, a two-sided confidence interval of
half-width epsilon at confidence (1 - delta) requires

    n >= ln(2 / delta) / (2 * epsilon^2)

Equivalently, solving for the margin epsilon actually supported by an
existing n:

    epsilon = sqrt(ln(2 / delta) / (2 * n))

This is advisory only -- not wired into run_all_checks.py, does not block
release. It also does not by itself prove non-regression: it only says how
tight a claim the *existing case count* could support if every case had
actually been executed against a live model, which for most Skills in this
repository it has not (see each Skill's own lifecycle.json notes for
executed-vs-authored status). Read the notes before citing this report as
evidence of anything beyond "how much evidence would be enough."
"""

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"

DEFAULT_DELTA = 0.05
REFERENCE_EPSILONS = (0.30, 0.20, 0.10, 0.05)


def case_count(lifecycle: dict) -> int:
    routing = lifecycle.get("routing_case_ids") or []
    behavior = lifecycle.get("behavior_case_ids") or []
    return len(routing) + len(behavior)


def epsilon_at_n(n: int, delta: float) -> float | None:
    """Margin epsilon supported by n trials at confidence (1 - delta)."""
    if n <= 0:
        return None
    return math.sqrt(math.log(2.0 / delta) / (2.0 * n))


def n_required_for_epsilon(epsilon: float, delta: float) -> int:
    return math.ceil(math.log(2.0 / delta) / (2.0 * epsilon ** 2))


def report_one(name: str, delta: float) -> str:
    path = SKILLS / name / "lifecycle.json"
    if not path.is_file():
        return f"{name}: no lifecycle.json found"
    lifecycle = json.loads(path.read_text(encoding="utf-8"))
    n = case_count(lifecycle)
    eps = epsilon_at_n(n, delta)
    lines = [f"{name}: n={n} case(s) (routing + behavior)"]
    if eps is None:
        lines.append("  n=0 -- no confidence claim of any kind is supported.")
    else:
        lines.append(
            f"  at {int((1 - delta) * 100)}% confidence, current n supports a margin of "
            f"+/-{eps * 100:.0f} percentage points on true pass rate"
        )
        lines.append("  cases needed for tighter margins at the same confidence level:")
        for target_eps in REFERENCE_EPSILONS:
            needed = n_required_for_epsilon(target_eps, delta)
            gap = needed - n
            gap_note = f"({gap} more needed)" if gap > 0 else "(already sufficient)"
            lines.append(f"    +/-{target_eps * 100:.0f} pts -> n>={needed}  {gap_note}")
    lines.append(
        "  reminder: this counts AUTHORED cases, not executed ones -- see the Skill's "
        "own lifecycle.json notes for whether any case has actually been run against "
        "a live model."
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill", nargs="*", help="Skill name(s) to report on")
    parser.add_argument("--all", action="store_true", help="report on every Skill under .agents/skills/")
    parser.add_argument("--delta", type=float, default=DEFAULT_DELTA, help=f"confidence parameter (default {DEFAULT_DELTA} -> 95%% confidence)")
    args = parser.parse_args()

    if not (0 < args.delta < 1):
        parser.error("--delta must be between 0 and 1")

    if args.all:
        names = sorted(p.name for p in SKILLS.iterdir() if (p / "lifecycle.json").is_file())
    elif args.skill:
        names = args.skill
    else:
        parser.error("pass one or more skill names, or --all")
        return 2

    for name in names:
        print(report_one(name, args.delta))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
