"""Render existing CloudBox evidence into one human-readable Benchmark report.

This script does not run models, grade outputs, or decide release readiness.
It preserves the status already recorded by each authoritative input.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path | None, label: str, issues: list[str]) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(f"{label}: {type(exc).__name__}: {exc}")
        return None
    if not isinstance(value, dict):
        issues.append(f"{label}: root must be a JSON object")
        return None
    return value


def values(value: Any) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def gate_status(record: dict[str, Any] | None) -> str:
    if record is None:
        return "NOT_PROVIDED"
    passed = (record.get("gate") or {}).get("passed")
    if passed is True:
        return "PASS"
    if passed is False:
        return "FAIL"
    return "UNKNOWN"


def routing_view(record: dict[str, Any] | None, source: Path | None) -> dict[str, Any]:
    metrics = (record or {}).get("metrics") or {}
    return {
        "status": gate_status(record),
        "source": str(source) if source else None,
        "suite": (record or {}).get("suite"),
        "providers": values((record or {}).get("provider")),
        "models": values((record or {}).get("model")),
        "record_count": metrics.get("record_count", (record or {}).get("record_count")),
        "overall_pass_rate": metrics.get("overall_pass_rate"),
        "contract_valid_rate": metrics.get("contract_valid_rate"),
    }


def behavior_view(record: dict[str, Any] | None, source: Path | None) -> dict[str, Any]:
    results = (record or {}).get("results") or []
    providers = sorted({r.get("provider") for r in results if isinstance(r, dict) and r.get("provider")})
    models = sorted({r.get("model") for r in results if isinstance(r, dict) and r.get("model")})
    return {
        "status": gate_status(record),
        "source": str(source) if source else None,
        "providers": providers,
        "models": models,
        "graded_records": (record or {}).get("graded_records"),
        "passed_records": (record or {}).get("passed_records"),
        "average_score": (record or {}).get("average_score"),
        "ungraded_case_ids": (record or {}).get("ungraded_case_ids", []),
    }


def panel_view(record: dict[str, Any] | None, source: Path | None) -> dict[str, Any]:
    workers = (record or {}).get("workers") or []
    return {
        "status": (record or {}).get("status", "NOT_PROVIDED"),
        "source": str(source) if source else None,
        "panel_id": (record or {}).get("panel_id"),
        "workers": [
            {
                "family": worker.get("family"),
                "role": worker.get("role"),
                "provider": worker.get("provider"),
                "model": worker.get("canonical_model") or worker.get("selected_model"),
                "status": worker.get("status"),
                "verdict": worker.get("verdict"),
            }
            for worker in workers if isinstance(worker, dict)
        ],
    }


def lifecycle_view(record: dict[str, Any] | None, source: Path | None) -> dict[str, Any]:
    return {
        "status": "RECORDED" if record else "NOT_PROVIDED",
        "source": str(source) if source else None,
        "stage": (record or {}).get("stage"),
        "last_reviewed_version": (record or {}).get("last_reviewed_version"),
        "routing_cases": len((record or {}).get("routing_case_ids", [])),
        "behavior_cases": len((record or {}).get("behavior_case_ids", [])),
    }


def delta(before: Any, after: Any) -> float | None:
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        return round(float(after) - float(before), 4)
    return None


def build_report(
    *, subject: str, generated_at: str,
    routing_baseline: tuple[dict[str, Any] | None, Path | None],
    routing_candidate: tuple[dict[str, Any] | None, Path | None],
    behavior_baseline: tuple[dict[str, Any] | None, Path | None],
    behavior_candidate: tuple[dict[str, Any] | None, Path | None],
    panel: tuple[dict[str, Any] | None, Path | None],
    lifecycle: tuple[dict[str, Any] | None, Path | None],
    issues: list[str],
) -> dict[str, Any]:
    rb = routing_view(*routing_baseline)
    rc = routing_view(*routing_candidate)
    bb = behavior_view(*behavior_baseline)
    bc = behavior_view(*behavior_candidate)
    return {
        "schema_version": 1,
        "report_kind": "evidence_summary_only",
        "report_status": "INVALID_INPUT" if issues else "REPORT_RENDERED",
        "subject": subject,
        "generated_at_utc": generated_at,
        "routing": {"baseline": rb, "candidate": rc},
        "behavior": {"baseline": bb, "candidate": bc},
        "deltas": {
            "routing_overall_pass_rate": delta(rb["overall_pass_rate"], rc["overall_pass_rate"]),
            "behavior_average_score": delta(bb["average_score"], bc["average_score"]),
        },
        "panel": panel_view(*panel),
        "lifecycle": lifecycle_view(*lifecycle),
        "issues": issues,
        "limitations": [
            "The report does not execute models or deterministic checks.",
            "The report does not re-grade evidence or authorize approval, merge, tag, or release.",
            "NOT_PROVIDED and UNKNOWN remain visible instead of being treated as PASS.",
        ],
    }


def show(value: Any, *, percent: bool = False) -> str:
    if value is None:
        return "—"
    if percent and isinstance(value, (int, float)):
        return f"{float(value) * 100:.1f}%"
    return str(value)


def render_markdown(report: dict[str, Any]) -> str:
    routing = report["routing"]
    behavior = report["behavior"]
    lines = [
        f"# Benchmark Report: {report['subject']}", "",
        f"- Report status: **{report['report_status']}**",
        f"- Generated: `{report['generated_at_utc']}`",
        "- Scope: evidence display only; no grading or release authority.", "",
        "## Evidence summary", "",
        "| Evidence | Baseline | Candidate | Baseline value | Candidate value | Delta |",
        "|---|---|---|---:|---:|---:|",
        f"| Routing | {routing['baseline']['status']} | {routing['candidate']['status']} | {show(routing['baseline']['overall_pass_rate'], percent=True)} | {show(routing['candidate']['overall_pass_rate'], percent=True)} | {show(report['deltas']['routing_overall_pass_rate'], percent=True)} |",
        f"| Behavior | {behavior['baseline']['status']} | {behavior['candidate']['status']} | {show(behavior['baseline']['average_score'])} | {show(behavior['candidate']['average_score'])} | {show(report['deltas']['behavior_average_score'])} |",
        "", "## Model evidence", "",
        "| Input | Providers | Models | Source |",
        "|---|---|---|---|",
    ]
    for label, item in (
        ("Routing baseline", routing["baseline"]), ("Routing candidate", routing["candidate"]),
        ("Behavior baseline", behavior["baseline"]), ("Behavior candidate", behavior["candidate"]),
    ):
        lines.append(f"| {label} | {', '.join(item['providers']) or '—'} | {', '.join(item['models']) or '—'} | {item['source'] or '—'} |")
    panel = report["panel"]
    lines += ["", "## Review panel", "", f"- Status: **{panel['status']}**"]
    if panel["workers"]:
        lines += ["", "| Family | Role | Provider | Model | Execution | Verdict |", "|---|---|---|---|---|---|"]
        for worker in panel["workers"]:
            lines.append("| {family} | {role} | {provider} | {model} | {status} | {verdict} |".format(**worker))
    lifecycle = report["lifecycle"]
    lines += [
        "", "## Lifecycle record", "",
        f"- Status: **{lifecycle['status']}**",
        f"- Stage: `{lifecycle['stage'] or '—'}`",
        f"- Last reviewed version: `{lifecycle['last_reviewed_version'] or '—'}`",
        f"- Declared cases: routing {lifecycle['routing_cases']}, behavior {lifecycle['behavior_cases']}",
    ]
    if report["issues"]:
        lines += ["", "## Input issues", ""] + [f"- {issue}" for issue in report["issues"]]
    lines += ["", "## Limitations", ""] + [f"- {item}" for item in report["limitations"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    parser.add_argument("--routing-baseline", type=Path)
    parser.add_argument("--routing-candidate", type=Path)
    parser.add_argument("--behavior-baseline", type=Path)
    parser.add_argument("--behavior-candidate", type=Path)
    parser.add_argument("--panel", type=Path)
    parser.add_argument("--lifecycle", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    issues: list[str] = []
    read = lambda path, label: (load_json(path, label, issues), path)
    report = build_report(
        subject=args.subject,
        generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        routing_baseline=read(args.routing_baseline, "routing baseline"),
        routing_candidate=read(args.routing_candidate, "routing candidate"),
        behavior_baseline=read(args.behavior_baseline, "behavior baseline"),
        behavior_candidate=read(args.behavior_candidate, "behavior candidate"),
        panel=read(args.panel, "panel"), lifecycle=read(args.lifecycle, "lifecycle"), issues=issues,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(report), encoding="utf-8")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered Benchmark evidence report: {args.output}")
    return 2 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
