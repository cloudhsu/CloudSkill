from __future__ import annotations

"""Fit a Wright's-Law-style power-law learning curve to real per-batch cost
data in evals/runtime/learning-curve-log.json.

Model: cost(n) = a * n^(-b), where n is the sequential batch index (not case
count) and cost is a chosen metric (default avg_latency_ms). Taking logs
turns this into a linear-regression problem:

    log(cost) = log(a) - b * log(n)

fit by ordinary least squares on (log n, log cost) pairs. b > 0 means cost
fell as sequence_index grew (a real per-batch speedup trend); b <= 0 means no
such trend in this data.

This is intentionally a thin, honest tool, not a proof of learning:

- With only a handful of points from ONE session, a fitted b is a rough
  trend line, not a validated law -- report R^2 alongside b and do not
  overstate a small-n fit.
- Every batch's own n_items and content differ (different skills, different
  case counts, different prompt complexity) -- this is a real confound this
  tool cannot control for. A literal Wright's Law application (same task
  repeated N times) would need a same-task-type repeated-trial dataset that
  does not exist yet; until it does, treat any fitted trend here as
  suggestive throughput movement, not a clean learning-curve measurement.
- Cross-session comparison (durable improvement vs. session-bound prompt-
  cache effect) requires at least two distinct session_id values in the log.
  With only one session_id present, this script can only report a within-
  session trend and must say so explicitly, not silently claim more.
"""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "evals" / "runtime" / "learning-curve-log.json"


def load_entries() -> list[dict]:
    if not LOG_PATH.is_file():
        return []
    return json.loads(LOG_PATH.read_text(encoding="utf-8")).get("entries", [])


def fit_power_law(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    """Least-squares fit of log(y) = log(a) - b*log(x). Returns (a, b, r_squared)."""
    xs = [math.log(x) for x, _ in points]
    ys = [math.log(y) for _, y in points]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    ss_xx = sum((x - mean_x) ** 2 for x in xs)
    if ss_xx == 0:
        return math.exp(mean_y), 0.0, 0.0
    slope = ss_xy / ss_xx  # this is -b
    intercept = mean_y - slope * mean_x  # log(a)
    b = -slope
    a = math.exp(intercept)
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    if ss_tot == 0:
        r_squared = 1.0
    else:
        predicted = [intercept + slope * x for x in xs]
        ss_res = sum((y - p) ** 2 for y, p in zip(ys, predicted))
        r_squared = 1.0 - ss_res / ss_tot
    return a, b, r_squared


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--metric", default="avg_latency_ms", help="metric field to fit (default avg_latency_ms)")
    parser.add_argument("--task-type", default=None, help="restrict to one task_type (default: all, grouped separately)")
    args = parser.parse_args()

    entries = load_entries()
    if not entries:
        print(f"No entries found in {LOG_PATH.relative_to(ROOT)}.")
        return 0

    entries = [e for e in entries if e.get("metric") == args.metric]
    if args.task_type:
        entries = [e for e in entries if e.get("task_type") == args.task_type]
    if not entries:
        print(f"No entries match metric={args.metric!r}" + (f" task_type={args.task_type!r}" if args.task_type else "") + ".")
        return 0

    session_ids = sorted({e["session_id"] for e in entries})
    print(f"Sessions represented: {len(session_ids)} ({', '.join(session_ids)})")
    if len(session_ids) < 2:
        print(
            "Only one session's data exists. This can report a WITHIN-SESSION trend "
            "only -- it cannot yet distinguish a durable improvement from a session-"
            "bound prompt-cache effect. That comparison needs a second session's data."
        )
    print()

    by_type: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_type[e.get("task_type", "unknown")].append(e)

    for task_type, rows in sorted(by_type.items()):
        rows.sort(key=lambda r: r["sequence_index"])
        points = [(float(r["sequence_index"]), float(r["value"])) for r in rows]
        print(f"task_type={task_type} ({len(points)} points, metric={args.metric})")
        for r in rows:
            print(f"  n={r['sequence_index']:>2}  {r['batch_label']:<28} {args.metric}={r['value']:.0f}  (items={r.get('n_items', '?')})")
        if len(points) < 3:
            print("  Fewer than 3 points -- not fitting a curve, not enough data for a meaningful trend line.")
            print()
            continue
        a, b, r2 = fit_power_law(points)
        direction = "falling" if b > 0 else "flat/rising"
        print(f"  Fit: cost(n) ~= {a:.0f} * n^(-{b:.3f})  |  R^2={r2:.2f}  |  trend: {direction} with sequence index")
        if r2 < 0.5:
            print("  R^2 < 0.5 -- weak fit, treat any apparent trend as noise until more data accumulates.")
        print(
            "  Caveat: batches differ in content/skill/complexity, not a literal same-task "
            "repeated trial -- read this as a rough throughput trend, not a validated learning curve."
        )
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
