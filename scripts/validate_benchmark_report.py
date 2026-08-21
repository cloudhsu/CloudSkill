from __future__ import annotations

import json
import tempfile
from pathlib import Path

from render_benchmark_report import build_report, render_markdown


def pair(value: dict | None = None) -> tuple[dict | None, Path | None]:
    return value, Path("fixture.json") if value else None


routing_red = {"provider": ["luna"], "model": ["high"], "metrics": {"record_count": 10, "overall_pass_rate": 0.7}, "gate": {"passed": False}}
routing_green = {"provider": ["sol"], "model": ["high"], "metrics": {"record_count": 10, "overall_pass_rate": 0.9}, "gate": {"passed": True}}
behavior_red = {"average_score": 70, "graded_records": 3, "passed_records": 2, "gate": {"passed": False}, "results": []}
behavior_green = {"average_score": 85, "graded_records": 3, "passed_records": 3, "gate": {"passed": True}, "results": []}
panel = {"status": "DEGRADED", "workers": [{"family": "gpt", "role": "frontier", "provider": "codex", "selected_model": "sol", "canonical_model": "sol", "status": "PASS", "verdict": "PASS"}]}
lifecycle = {"stage": "experimental", "last_reviewed_version": "7.6.32", "routing_case_ids": ["R1"], "behavior_case_ids": ["B1", "B2"]}

report = build_report(
    subject="fixture", generated_at="2026-08-20T00:00:00Z",
    routing_baseline=pair(routing_red), routing_candidate=pair(routing_green),
    behavior_baseline=pair(behavior_red), behavior_candidate=pair(behavior_green),
    panel=pair(panel), lifecycle=pair(lifecycle), issues=[],
)
assert report["report_status"] == "REPORT_RENDERED"
assert report["deltas"]["routing_overall_pass_rate"] == 0.2
assert report["deltas"]["behavior_average_score"] == 15.0
assert report["panel"]["status"] == "DEGRADED"  # Renderer must not promote source status.
markdown = render_markdown(report)
for marker in ("Evidence summary", "Model evidence", "Review panel", "Lifecycle record", "no grading or release authority"):
    assert marker in markdown

missing = build_report(
    subject="missing", generated_at="2026-08-20T00:00:00Z",
    routing_baseline=pair(), routing_candidate=pair(), behavior_baseline=pair(), behavior_candidate=pair(),
    panel=pair(), lifecycle=pair(), issues=[],
)
assert missing["routing"]["candidate"]["status"] == "NOT_PROVIDED"
assert missing["report_status"] == "REPORT_RENDERED"

with tempfile.TemporaryDirectory() as directory:
    bad = Path(directory) / "bad.json"
    bad.write_text("[not an object]", encoding="utf-8")
    issues: list[str] = []
    from render_benchmark_report import load_json
    assert load_json(bad, "bad", issues) is None and issues

print("Validated unified Benchmark evidence report rendering and truthful status preservation")
