from __future__ import annotations

"""Bayesian companion to eval_confidence_report.py.

eval_confidence_report.py answers "how tight a margin WOULD n authored
cases support, if every one had been executed" (Hoeffding, distribution-free,
worst-case, and -- critically -- blind to actual outcomes). It cannot get
tighter than that no matter how many PASSes actually occur, because it never
reads any.

This script answers a different, complementary question: "given the cases
that have ACTUALLY been executed and their real PASS/FAIL outcomes (from
evals/runtime/execution-ledger.json), what does a Beta-Binomial posterior
say about the skill's true pass rate?" A Bayesian credible interval over
real outcomes is tighter than Hoeffding's worst-case bound at the same
sample size, and it is the only one of the two that can ever report a
pass-rate ESTIMATE (Hoeffding only ever reports an achievable MARGIN around
an unknown rate).

Model: each executed case is a Bernoulli trial. PASS and PASS_DEVIATION_*
count as a success (the case's required/forbidden behaviors were satisfied,
even if routing landed on a different skill); FAIL_CONTENT and FAIL_ROUTING
count as a failure. Prior: Beta(alpha0, beta0), default Beta(1, 1) (uniform,
uninformative) unless overridden. Posterior after k successes in n trials is
Beta(alpha0 + k, beta0 + n - k). Reported interval is the equal-tailed
credible interval at the requested confidence level, computed via the
regularized incomplete beta function (no scipy dependency).

This is advisory only -- not wired into run_all_checks.py, does not block
release, and does not replace eval_confidence_report.py's authored-case-count
report (skills with zero executed cases have nothing to say here; use the
Hoeffding report for those). Read each skill's lifecycle.json notes before
citing either report as evidence of anything beyond what it actually
measures.
"""

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "evals" / "runtime" / "execution-ledger.json"

DEFAULT_ALPHA0 = 1.0
DEFAULT_BETA0 = 1.0
DEFAULT_CONFIDENCE = 0.95

SUCCESS_RESULTS = {"PASS", "PASS_DEVIATION_ROUTING", "PASS_DEVIATION_MINOR"}
FAILURE_RESULTS = {"FAIL_CONTENT", "FAIL_ROUTING"}


def _log_beta(a: float, b: float) -> float:
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _betacf(a: float, b: float, x: float) -> float:
    # Continued-fraction evaluation for the regularized incomplete beta
    # function (Numerical Recipes' betacf, standard textbook algorithm).
    MAXIT, EPS, FPMIN = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break
    return h


def regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """I_x(a, b), the CDF of Beta(a, b) at x. Pure-Python, no scipy."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.log(x) * a + math.log(1.0 - x) * b - _log_beta(a, b))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def beta_quantile(p: float, a: float, b: float, tol: float = 1e-10) -> float:
    """Inverse CDF via bisection -- monotonic, robust, no scipy dependency."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if regularized_incomplete_beta(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


def load_ledger() -> list[dict]:
    if not LEDGER.is_file():
        return []
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    return data.get("entries", [])


def per_skill_outcomes(entries: list[dict]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for e in entries:
        result = e.get("result")
        if result not in SUCCESS_RESULTS and result not in FAILURE_RESULTS:
            continue
        skill = e["skill"]
        bucket = out.setdefault(skill, {"k": 0, "n": 0})
        bucket["n"] += 1
        if result in SUCCESS_RESULTS:
            bucket["k"] += 1
    return out


def report_one(skill: str, k: int, n: int, alpha0: float, beta0: float, confidence: float) -> str:
    a = alpha0 + k
    b = beta0 + n - k
    mean = a / (a + b)
    tail = (1.0 - confidence) / 2.0
    lo = beta_quantile(tail, a, b)
    hi = beta_quantile(1.0 - tail, a, b)
    lines = [
        f"{skill}: k={k} success / n={n} executed (real outcomes, not authored-case count)",
        f"  Beta({alpha0:g}+{k}, {beta0:g}+{n - k}) posterior -> mean pass rate {mean * 100:.1f}%",
        f"  {int(confidence * 100)}% credible interval: [{lo * 100:.1f}%, {hi * 100:.1f}%]"
        f"  (width +/-{(hi - lo) / 2 * 100:.1f} pts)",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill", nargs="*", help="Skill name(s) to report on; default: every skill with ledger entries")
    parser.add_argument("--alpha0", type=float, default=DEFAULT_ALPHA0, help=f"prior alpha (default {DEFAULT_ALPHA0})")
    parser.add_argument("--beta0", type=float, default=DEFAULT_BETA0, help=f"prior beta (default {DEFAULT_BETA0})")
    parser.add_argument("--confidence", type=float, default=DEFAULT_CONFIDENCE, help=f"credible-interval mass (default {DEFAULT_CONFIDENCE})")
    args = parser.parse_args()

    if not (0 < args.confidence < 1):
        parser.error("--confidence must be between 0 and 1")
    if args.alpha0 <= 0 or args.beta0 <= 0:
        parser.error("--alpha0 and --beta0 must be positive")

    entries = load_ledger()
    if not entries:
        print(f"No execution-ledger entries found at {LEDGER.relative_to(ROOT)}.")
        print("This report only covers cases that have actually been run against a live model.")
        return 0

    outcomes = per_skill_outcomes(entries)
    names = args.skill or sorted(outcomes)
    missing = [n for n in names if n not in outcomes]
    for n in missing:
        print(f"{n}: no real execution outcomes in the ledger -- nothing to report here; see eval_confidence_report.py for the authored-case-count view.")
        print()

    for name in names:
        if name not in outcomes:
            continue
        bucket = outcomes[name]
        print(report_one(name, bucket["k"], bucket["n"], args.alpha0, args.beta0, args.confidence))
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
