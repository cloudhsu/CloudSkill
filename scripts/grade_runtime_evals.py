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
    ROUTER_SKILL_PATH,
    ROOT,
    VERSION_FILE,
    grade_decision,
    load_cases,
    load_manifest,
    skill_ids,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministically grade CloudBox runtime routing results."
    )
    parser.add_argument("--input", type=Path, required=True, help="JSONL output from run_runtime_evals.py")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, help="Summary JSON path")
    parser.add_argument("--markdown-output", type=Path, help="Human-readable Markdown report path")
    parser.add_argument("--no-markdown", action="store_true", help="Do not write the default Markdown report")
    parser.add_argument("--allow-failures", action="store_true", help="Always exit zero after writing the report")
    return parser.parse_args()


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 1.0


def routing_context(record: dict[str, Any]) -> dict[str, Any]:
    context = record.get("context")
    if not isinstance(context, dict):
        return {}
    nested = context.get("routing")
    return nested if isinstance(nested, dict) else context


def context_integrity(record: dict[str, Any]) -> dict[str, Any]:
    evidence = routing_context(record)
    mode = evidence.get("mode") or record.get("context_mode")
    loaded = evidence.get("loaded_files") if isinstance(evidence.get("loaded_files"), list) else []
    router_rel = ROUTER_SKILL_PATH.relative_to(ROOT).as_posix()
    router_entries = [
        item for item in loaded if isinstance(item, dict) and item.get("path") == router_rel
    ]
    router_loaded = any(item.get("included") and not item.get("truncated") for item in router_entries)
    overflow = int(evidence.get("overflow_tokens") or 0)
    evidence_present = bool(evidence)
    requires_router = mode == "router" or record.get("context_mode") == "selected-skills"
    return {
        "evidence_present": evidence_present,
        "mode": mode,
        "router_required": requires_router,
        "router_loaded": router_loaded,
        "within_budget": overflow == 0,
        "truncated": bool(evidence.get("truncated", False)),
        "passed": evidence_present and overflow == 0 and (router_loaded if requires_router else True),
    }


def _safe_actual(record: dict[str, Any], field: str) -> Any:
    value = record.get(field)
    return value if value is not None else record.get("actual")


def _grade_record(
    case: dict[str, Any], record: dict[str, Any], valid_skills: set[str], field: str
) -> dict[str, Any]:
    actual = _safe_actual(record, field)
    if actual is None:
        return {
            "passed": False,
            "checks": {
                "valid_output": False,
                "primary_skill": False,
                "required_supporting_skills": False,
                "additional_supporting_skills": False,
                "forbidden_selected_skills": False,
                "execution_order": False,
                "router_not_downstream": False,
                "selected_set_consistent": False,
            },
            "errors": ["no routing decision available"],
            "contract_errors": ["no routing decision available"],
        }
    return grade_decision(case, actual, valid_skills)


def aggregate(entries: list[dict[str, Any]], grade_key: str, actual_key: str) -> dict[str, Any]:
    counters = defaultdict(int)
    required_total = 0
    required_found = 0
    for entry in entries:
        record = entry["record"]
        grade = entry[grade_key]
        expected = entry["expected"]
        checks = grade.get("checks", {})
        actual = _safe_actual(record, actual_key)
        actual = actual if isinstance(actual, dict) else {}
        required = set(expected.get("required_supporting_skills", []))
        actual_support = set(actual.get("supporting_skills") or [])
        required_total += len(required)
        required_found += len(required & actual_support)

        counters["total"] += 1
        counters["passed"] += int(grade.get("passed", False))
        counters["valid_output"] += int(checks.get("valid_output", False))
        counters["primary_skill"] += int(checks.get("primary_skill", False))
        counters["required_supporting"] += int(checks.get("required_supporting_skills", False))
        counters["supporting_exact"] += int(
            checks.get("required_supporting_skills", False)
            and checks.get("additional_supporting_skills", False)
        )
        counters["forbidden_absent"] += int(checks.get("forbidden_selected_skills", False))
        counters["execution_order"] += int(checks.get("execution_order", False))
        counters["router_not_downstream"] += int(checks.get("router_not_downstream", False))
        counters["selected_set_consistent"] += int(checks.get("selected_set_consistent", False))
        counters["context_integrity"] += int(entry["context_integrity"]["passed"])

        if expected.get("primary_skill") is None:
            counters["no_skill_total"] += 1
            counters["no_skill_passed"] += int(
                checks.get("primary_skill", False)
                and checks.get("required_supporting_skills", False)
                and checks.get("additional_supporting_skills", False)
                and checks.get("execution_order", False)
            )
        if record.get("eval_kind") == "behavior":
            counters["behavior_total"] += 1
            counters["behavior_completed"] += int(record.get("behavior_status") == "completed")
            counters["behavior_no_skill"] += int(record.get("behavior_status") == "no-skill")
            counters["behavior_failed"] += int(bool(record.get("error")))

    total = counters["total"]
    return {
        "record_count": total,
        "overall_pass_rate": ratio(counters["passed"], total),
        "contract_valid_rate": ratio(counters["valid_output"], total),
        "primary_skill_accuracy": ratio(counters["primary_skill"], total),
        "supporting_skill_exact_accuracy": ratio(counters["supporting_exact"], total),
        "required_supporting_skill_recall": ratio(required_found, required_total),
        "forbidden_selected_skill_violation_rate": round(
            1 - ratio(counters["forbidden_absent"], total), 6
        ),
        "execution_order_accuracy": ratio(counters["execution_order"], total),
        "selected_set_consistency_rate": ratio(counters["selected_set_consistent"], total),
        "no_skill_accuracy": ratio(counters["no_skill_passed"], counters["no_skill_total"]),
        "router_self_inclusion_rate": round(
            1 - ratio(counters["router_not_downstream"], total), 6
        ),
        "invalid_output_rate": round(1 - ratio(counters["valid_output"], total), 6),
        "context_integrity_rate": ratio(counters["context_integrity"], total),
        "behavior_execution": {
            "total": counters["behavior_total"],
            "completed": counters["behavior_completed"],
            "no_skill": counters["behavior_no_skill"],
            "failed": counters["behavior_failed"],
            "quality_graded": False,
        },
    }


def _pct(value: Any) -> str:
    return f"{float(value) * 100:.1f}%" if isinstance(value, (int, float)) else "—"


def _skill_list(primary: Any, supporting: Any, order: Any) -> str:
    p = primary if isinstance(primary, str) else ("無" if primary is None else "格式錯誤")
    s = ", ".join(supporting) if isinstance(supporting, list) and supporting else "無"
    o = " → ".join(order) if isinstance(order, list) and order else "無"
    return f"P={p}; S={s}; O={o}"


def _problem_classification(entry: dict[str, Any]) -> str:
    record = entry["record"]
    grade = entry["effective_grade"]
    checks = grade.get("checks", {})
    integrity = entry["context_integrity"]
    if not integrity["passed"] or (record.get("error") and record.get("actual") is None):
        return "Runner／Context"
    if not checks.get("valid_output", False):
        return "輸出契約／模型結構遵循"
    if not checks.get("primary_skill", False):
        return "主要路由辨識"
    if not checks.get("required_supporting_skills", False) or not checks.get(
        "additional_supporting_skills", False
    ):
        return "Supporting Skill 辨識"
    if not checks.get("execution_order", False):
        return "執行順序"
    return "通過"


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    initial = report["initial_metrics"]
    repair = report["contract_repair"]
    lines = [
        "# CloudBox Runtime Eval 人類可讀評分報告",
        "",
        f"- CloudBox 版本：`{report['cloudbox_version']}`",
        f"- Provider：{', '.join(report['provider'])}",
        f"- Model：{', '.join(report['model'])}",
        f"- 紀錄數：{report['record_count']}",
        "",
        "## 結論摘要",
        "",
        f"- 最終嚴格通過率：**{_pct(metrics['overall_pass_rate'])}**。",
        f"- 主要 Skill 正確率：**{_pct(metrics['primary_skill_accuracy'])}**。",
        f"- Supporting Skill 完全正確率：**{_pct(metrics['supporting_skill_exact_accuracy'])}**。",
        f"- 執行順序正確率：**{_pct(metrics['execution_order_accuracy'])}**。",
        f"- 最終輸出契約有效率：**{_pct(metrics['contract_valid_rate'])}**。",
        f"- Contract repair 套用 {repair['applied_records']} 筆，其中 {repair['repaired_to_valid_records']} 筆由無效轉為有效。",
        "",
        "## 原始模型輸出與修復後結果",
        "",
        "| 指標 | 原始模型輸出 | 修復後／最終 |",
        "|---|---:|---:|",
        f"| 嚴格通過率 | {_pct(initial['overall_pass_rate'])} | {_pct(metrics['overall_pass_rate'])} |",
        f"| Contract valid | {_pct(initial['contract_valid_rate'])} | {_pct(metrics['contract_valid_rate'])} |",
        f"| Primary accuracy | {_pct(initial['primary_skill_accuracy'])} | {_pct(metrics['primary_skill_accuracy'])} |",
        f"| Supporting exact | {_pct(initial['supporting_skill_exact_accuracy'])} | {_pct(metrics['supporting_skill_exact_accuracy'])} |",
        f"| Execution order | {_pct(initial['execution_order_accuracy'])} | {_pct(metrics['execution_order_accuracy'])} |",
        f"| Router self-inclusion | {_pct(initial['router_self_inclusion_rate'])} | {_pct(metrics['router_self_inclusion_rate'])} |",
        "",
        "> Contract repair 只處理機械性欄位關係，例如補齊 execution_order；不會新增漏選的 supporting skill，也不會更換 primary skill。",
        "",
        "## Context Mode 比較",
        "",
        "| Mode | 嚴格通過 | Primary | Supporting exact | Order | Contract valid |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode, values in report["metrics_by_context_mode"].items():
        lines.append(
            f"| {mode} | {_pct(values['overall_pass_rate'])} | "
            f"{_pct(values['primary_skill_accuracy'])} | "
            f"{_pct(values['supporting_skill_exact_accuracy'])} | "
            f"{_pct(values['execution_order_accuracy'])} | "
            f"{_pct(values['contract_valid_rate'])} |"
        )

    lines.extend(
        [
            "",
            "## 逐題結果",
            "",
            "| Case | 預期 | 最終實際 | 嚴格結果 | 問題分類 | Repair |",
            "|---|---|---|---|---|---|",
        ]
    )
    for case_id, results in report["case_results"].items():
        for result in results:
            expected = result.get("expected") or {}
            actual = result.get("actual") if isinstance(result.get("actual"), dict) else {}
            expected_text = _skill_list(
                expected.get("primary_skill"),
                expected.get("required_supporting_skills"),
                expected.get("execution_order"),
            )
            actual_text = _skill_list(
                actual.get("primary_skill"),
                actual.get("supporting_skills"),
                actual.get("execution_order"),
            )
            passed = "通過" if result["grade"]["passed"] else "未通過"
            repair_data = result.get("contract_repair") or {}
            repair_text = "；".join(repair_data.get("changes") or []) or "無"
            classification = result.get("problem_classification") or "—"
            lines.append(
                f"| {case_id} | {expected_text} | {actual_text} | {passed} | {classification} | {repair_text} |"
            )

    lines.extend(
        [
            "",
            "## 如何判斷下一步",
            "",
            "- Primary 錯：先檢查 Router Prompt、reference retrieval 與模型能力。",
            "- Primary 對、Supporting 錯：優化多 decision-boundary 掃描，不要先改 downstream Skill。",
            "- Skill 都對、Order 錯：優化 owner 與 execution order 契約。",
            "- Contract invalid 但 repair 後有效：屬於模型結構遵循問題，不是 Skill 規則錯。",
            "- Routing 全對但 Behavior 回答差：再檢查 selected SKILL.md／references 與 Behavior rubric。",
            "",
            "## 證據限制",
            "",
            "本報告的嚴格評分針對 Routing Decision。Behavior 階段只記錄是否完成，尚未自動判斷工程回答品質。",
            "",
        ]
    )
    return "\n".join(lines)


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
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    failures: list[str] = []
    models: set[str] = set()
    providers: set[str] = set()
    diagnostic_counts = defaultdict(int)
    graded_entries: list[dict[str, Any]] = []
    repair_counts = defaultdict(int)

    for index, record in enumerate(records, start=1):
        case_id = record.get("case_id")
        if case_id not in case_map:
            expected: dict[str, Any] = {}
            initial_grade = effective_grade = {
                "passed": False,
                "checks": {"valid_output": False},
                "errors": [f"unknown case_id: {case_id}"],
                "contract_errors": [f"unknown case_id: {case_id}"],
            }
        else:
            case = case_map[case_id]
            expected = case["expected"]
            initial_grade = _grade_record(case, record, valid_skills, "initial_actual")
            effective_grade = _grade_record(case, record, valid_skills, "actual")

        integrity = context_integrity(record)
        entry = {
            "record": record,
            "initial_grade": initial_grade,
            "effective_grade": effective_grade,
            "expected": expected,
            "context_integrity": integrity,
        }
        graded_entries.append(entry)
        mode = str(record.get("context_mode") or integrity.get("mode") or "unknown")
        grouped[mode].append(entry)

        repair = record.get("contract_repair") if isinstance(record.get("contract_repair"), dict) else {}
        repair_counts["records"] += 1
        repair_counts["applied"] += int(bool(repair.get("applied")))
        repair_counts["repaired_to_valid"] += int(
            not initial_grade.get("checks", {}).get("valid_output", False)
            and effective_grade.get("checks", {}).get("valid_output", False)
        )

        enriched = dict(record)
        enriched["expected"] = expected
        enriched["context_integrity"] = integrity
        enriched["initial_grade"] = initial_grade
        enriched["grade"] = effective_grade
        enriched["problem_classification"] = _problem_classification(entry)
        per_case[str(case_id)].append(enriched)
        if not effective_grade["passed"]:
            failures.append(f"record {index} {case_id}: {', '.join(effective_grade['errors'])}")
        models.add(str(record.get("model_returned") or record.get("model_requested") or "unknown"))
        providers.add(str(record.get("provider") or "unknown"))

        if not integrity["passed"] or (record.get("error") and record.get("actual") is None):
            diagnostic_counts["runner_or_context_assembly"] += 1
        elif not effective_grade.get("checks", {}).get("valid_output", False):
            diagnostic_counts["prompt_or_model_contract_adherence"] += 1
        elif not effective_grade["passed"]:
            diagnostic_counts["model_routing_or_prompt_discrimination"] += 1
        elif repair.get("applied"):
            diagnostic_counts["routing_pass_after_contract_repair"] += 1
        else:
            diagnostic_counts["routing_pass"] += 1

    metrics = aggregate(graded_entries, "effective_grade", "actual")
    initial_metrics = aggregate(graded_entries, "initial_grade", "initial_actual")
    metrics_by_context_mode = {
        mode: aggregate(entries, "effective_grade", "actual")
        for mode, entries in sorted(grouped.items())
    }
    initial_metrics_by_context_mode = {
        mode: aggregate(entries, "initial_grade", "initial_actual")
        for mode, entries in sorted(grouped.items())
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
        "context_integrity_rate": 1.0,
    }
    for metric, target in expected_exact.items():
        if metrics[metric] != target:
            gate_failures.append(f"{metric}={metrics[metric]} expected={target}")

    attempts = defaultdict(int)
    for record in records:
        attempts[record.get("case_id")] += 1

    report = {
        "schema_version": 3,
        "cloudbox_version": VERSION_FILE.read_text(encoding="utf-8").strip(),
        "suite": suite["suite"],
        "provider": sorted(providers),
        "model": sorted(models),
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "record_count": len(records),
        "runs_per_case": dict(sorted(attempts.items())),
        "initial_metrics": initial_metrics,
        "metrics": metrics,
        "initial_metrics_by_context_mode": initial_metrics_by_context_mode,
        "metrics_by_context_mode": metrics_by_context_mode,
        "contract_repair": {
            "record_count": repair_counts["records"],
            "applied_records": repair_counts["applied"],
            "repaired_to_valid_records": repair_counts["repaired_to_valid"],
            "note": "Mechanical repair does not change primary_skill or add missing supporting skills.",
        },
        "gate": {"passed": not gate_failures, "failures": gate_failures},
        "diagnostic_classification": {
            "counts": dict(sorted(diagnostic_counts.items())),
            "interpretation": {
                "runner_or_context_assembly": "Missing/overflow context or no routing decision. Fix Runner before judging Skills.",
                "prompt_or_model_contract_adherence": "Routing object remains contract-invalid. This is schema/structure adherence, not automatically a Skill defect.",
                "model_routing_or_prompt_discrimination": "Contract-valid output differs from expected routing. Compare repetitions and models before changing a Skill.",
                "routing_pass_after_contract_repair": "Routing classification was usable; a mechanical selected-set/order relation was normalized.",
                "cloudbox_skill_rule_problem": "Never inferred from one small-model run. Requires repeated failure with verified context and human review.",
            },
        },
        "record_failures": failures,
        "case_results": dict(sorted(per_case.items())),
    }

    output = args.output or args.input.with_name(args.input.stem + "-summary.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_output: Path | None = None
    if not args.no_markdown:
        markdown_output = args.markdown_output or output.with_suffix(".md")
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(render_markdown(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "initial_metrics": initial_metrics,
                "metrics": metrics,
                "contract_repair": report["contract_repair"],
                "gate": report["gate"],
                "json_output": str(output),
                "markdown_output": str(markdown_output) if markdown_output else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if gate_failures and not args.allow_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
