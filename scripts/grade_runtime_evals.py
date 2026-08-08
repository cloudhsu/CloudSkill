from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_eval_common import (
    DEFAULT_CASES,
    MANIFEST,
    ROOT,
    VERSION_FILE,
    grade_decision,
    load_cases,
    load_manifest,
    skill_ids,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministically grade CloudBox runtime routing results.")
    parser.add_argument("--input", type=Path, required=True, help="JSONL output from run_runtime_evals.py")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, help="Summary JSON path")
    parser.add_argument("--allow-failures", action="store_true", help="Always exit zero after writing the report")
    return parser.parse_args()


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 1.0


def main() -> int:
    args = parse_args()
    suite = load_cases(args.cases)
    manifest = load_manifest(MANIFEST)
    valid_skills = skill_ids(manifest)
    case_map = {case["id"]: case for case in suite["cases"]}
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{args.input}:{line_number}: invalid JSON: {exc}") from exc
    if not records:
        raise SystemExit("input contains no records")

    per_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    counters = defaultdict(int)
    required_total = 0
    required_found = 0
    failures: list[str] = []
    models = set()
    providers = set()

    for index, record in enumerate(records, start=1):
        case_id = record.get("case_id")
        if case_id not in case_map:
            grade = {"passed": False, "checks": {}, "errors": [f"unknown case_id: {case_id}"]}
        elif record.get("error"):
            grade = {"passed": False, "checks": {"valid_output": False}, "errors": ["model request error"]}
        else:
            grade = grade_decision(case_map[case_id], record.get("actual"), valid_skills)

        expected = case_map.get(case_id, {}).get("expected", {})
        required = set(expected.get("required_supporting_skills", []))
        actual_support = set((record.get("actual") or {}).get("supporting_skills") or [])
        required_total += len(required)
        required_found += len(required & actual_support)

        checks = grade.get("checks", {})
        counters["total"] += 1
        counters["passed"] += int(grade["passed"])
        counters["valid_output"] += int(checks.get("valid_output", False))
        counters["primary_skill"] += int(checks.get("primary_skill", False))
        counters["forbidden_absent"] += int(checks.get("forbidden_selected_skills", False))
        counters["execution_order"] += int(checks.get("execution_order", False))
        counters["router_not_downstream"] += int(checks.get("router_not_downstream", False))

        if expected.get("primary_skill") is None:
            counters["no_skill_total"] += 1
            counters["no_skill_passed"] += int(checks.get("primary_skill", False) and checks.get("valid_output", False))

        enriched = dict(record)
        enriched["grade"] = grade
        per_case[str(case_id)].append(enriched)
        if not grade["passed"]:
            failures.append(f"record {index} {case_id}: {', '.join(grade['errors'])}")
        models.add(record.get("model_returned") or record.get("model_requested") or "unknown")
        providers.add(record.get("provider") or "unknown")

    total = counters["total"]
    metrics = {
        "overall_pass_rate": ratio(counters["passed"], total),
        "primary_skill_accuracy": ratio(counters["primary_skill"], total),
        "required_supporting_skill_recall": ratio(required_found, required_total),
        "forbidden_selected_skill_violation_rate": round(1 - ratio(counters["forbidden_absent"], total), 6),
        "execution_order_accuracy": ratio(counters["execution_order"], total),
        "no_skill_accuracy": ratio(counters["no_skill_passed"], counters["no_skill_total"]),
        "router_self_inclusion_rate": round(1 - ratio(counters["router_not_downstream"], total), 6),
        "invalid_output_rate": round(1 - ratio(counters["valid_output"], total), 6),
    }
    gate_failures = []
    expected_exact = {
        "overall_pass_rate": 1.0,
        "primary_skill_accuracy": 1.0,
        "required_supporting_skill_recall": 1.0,
        "forbidden_selected_skill_violation_rate": 0.0,
        "execution_order_accuracy": 1.0,
        "no_skill_accuracy": 1.0,
        "router_self_inclusion_rate": 0.0,
        "invalid_output_rate": 0.0,
    }
    for metric, target in expected_exact.items():
        if metrics[metric] != target:
            gate_failures.append(f"{metric}={metrics[metric]} expected={target}")

    attempts = defaultdict(int)
    for record in records:
        attempts[record.get("case_id")] += 1
    report = {
        "schema_version": 1,
        "cloudbox_version": VERSION_FILE.read_text(encoding="utf-8").strip(),
        "suite": suite["suite"],
        "provider": sorted(providers),
        "model": sorted(models),
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "record_count": total,
        "runs_per_case": dict(sorted(attempts.items())),
        "metrics": metrics,
        "gate": {"passed": not gate_failures, "failures": gate_failures},
        "record_failures": failures,
        "case_results": dict(sorted(per_case.items())),
    }

    output = args.output or args.input.with_name(args.input.stem + "-summary.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": metrics, "gate": report["gate"], "output": str(output)}, ensure_ascii=False, indent=2))
    if gate_failures and not args.allow_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
