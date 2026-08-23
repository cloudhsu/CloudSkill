from __future__ import annotations

"""Rank Skills by how valuable their NEXT real model execution would be.

This formalizes what this run did by hand all night ("pick the worst-margin
skill, test it first"): a deterministic, safety-biased multi-armed-bandit
allocator over all Skills, not just the ones that happened to get case-
authoring attention.

Each Skill is an arm with an unknown true pass rate. Its posterior is
Beta(alpha0 + k, beta0 + n - k) from evals/runtime/execution-ledger.json's
real outcomes (k successes of n executed cases); a Skill with zero ledger
entries gets the bare prior Beta(alpha0, beta0) -- untested, maximally
uncertain, exactly Beta(1, 1)'s uniform variance by default.

Priority score is a lower confidence bound (LCB), not the posterior mean:

    LCB = mean - z * stddev

Ranking by ascending LCB (not by descending uncertainty alone) is a
deliberate choice: it prioritizes a Skill that might actually be failing
over one that is merely unmeasured but has no reason for suspicion, while
still ranking every untested Skill above any Skill already confirmed solid
-- an untested Skill's wide prior variance pulls its LCB down close to
already-concerning territory by construction. This is the same principle
safety-critical bandit literature calls pessimistic/LCB-based arm selection,
applied here to "which Skill's real behavior most needs verifying next"
rather than to reward-maximization.

This is advisory only -- not wired into run_all_checks.py, does not block
release, and does not choose *which case* to run within a Skill, only which
Skill's queue to pull from next. It also cannot see the two structural
findings this run surfaced by hand (a routing-caused content gap, and a
"feels trivial" routing trap repeated across independent Skills) -- read the
Skill's own lifecycle.json notes before treating a low rank as the only
signal worth acting on.
"""

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
LEDGER = ROOT / "evals" / "runtime" / "execution-ledger.json"

DEFAULT_ALPHA0 = 1.0
DEFAULT_BETA0 = 1.0
DEFAULT_Z = 1.96  # ~95% one-sided lower bound under a normal approximation

SUCCESS_RESULTS = {"PASS", "PASS_DEVIATION_ROUTING", "PASS_DEVIATION_MINOR"}
FAILURE_RESULTS = {"FAIL_CONTENT", "FAIL_ROUTING"}


def load_ledger_outcomes() -> dict[str, dict[str, int]]:
    if not LEDGER.is_file():
        return {}
    entries = json.loads(LEDGER.read_text(encoding="utf-8")).get("entries", [])
    out: dict[str, dict[str, int]] = {}
    for e in entries:
        result = e.get("result")
        if result not in SUCCESS_RESULTS and result not in FAILURE_RESULTS:
            continue
        bucket = out.setdefault(e["skill"], {"k": 0, "n": 0})
        bucket["n"] += 1
        if result in SUCCESS_RESULTS:
            bucket["k"] += 1
    return out


def authored_case_count(lifecycle: dict) -> int:
    routing = lifecycle.get("routing_case_ids") or []
    behavior = lifecycle.get("behavior_case_ids") or []
    return len(routing) + len(behavior)


def beta_stats(a: float, b: float) -> tuple[float, float]:
    mean = a / (a + b)
    var = (a * b) / ((a + b) ** 2 * (a + b + 1))
    return mean, math.sqrt(var)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--alpha0", type=float, default=DEFAULT_ALPHA0, help=f"prior alpha (default {DEFAULT_ALPHA0})")
    parser.add_argument("--beta0", type=float, default=DEFAULT_BETA0, help=f"prior beta (default {DEFAULT_BETA0})")
    parser.add_argument("--z", type=float, default=DEFAULT_Z, help=f"LCB z-score (default {DEFAULT_Z})")
    parser.add_argument("--top", type=int, default=0, help="show only the top N (0 = show all)")
    args = parser.parse_args()

    if args.alpha0 <= 0 or args.beta0 <= 0:
        parser.error("--alpha0 and --beta0 must be positive")

    outcomes = load_ledger_outcomes()
    rows = []
    for path in sorted(SKILLS.iterdir()):
        lc_path = path / "lifecycle.json"
        if not lc_path.is_file():
            continue
        name = path.name
        lifecycle = json.loads(lc_path.read_text(encoding="utf-8"))
        authored = authored_case_count(lifecycle)
        bucket = outcomes.get(name, {"k": 0, "n": 0})
        k, n = bucket["k"], bucket["n"]
        a, b = args.alpha0 + k, args.beta0 + n - k
        mean, stddev = beta_stats(a, b)
        lcb = max(0.0, mean - args.z * stddev)
        rows.append({
            "skill": name,
            "authored": authored,
            "executed_n": n,
            "executed_k": k,
            "mean": mean,
            "stddev": stddev,
            "lcb": lcb,
        })

    rows.sort(key=lambda r: (r["lcb"], -r["stddev"]))
    if args.top > 0:
        rows = rows[: args.top]

    print(f"{'skill':<42} {'authored':>8} {'exec n':>7} {'exec k':>7} {'mean':>7} {'stddev':>7} {'LCB':>7}")
    for r in rows:
        print(
            f"{r['skill']:<42} {r['authored']:>8} {r['executed_n']:>7} {r['executed_k']:>7} "
            f"{r['mean']*100:>6.1f}% {r['stddev']*100:>6.1f}% {r['lcb']*100:>6.1f}%"
        )
    print()
    print(
        "Read as: lowest LCB = highest-priority Skill for the next real execution. "
        "An untested Skill (exec n=0) ranks by the bare prior's wide uncertainty alone; "
        "an executed Skill with any real FAIL ranks by its actual observed rate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
