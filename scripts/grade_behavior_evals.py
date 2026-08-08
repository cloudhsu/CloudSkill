from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUBRICS = ROOT / "evals" / "runtime" / "cases" / "behavior-rubrics.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministically grade explicit engineering evidence in CloudBox Behavior Eval output."
    )
    parser.add_argument("--input", type=Path, required=True, help="JSONL output from run_runtime_evals.py")
    parser.add_argument("--rubrics", type=Path, default=DEFAULT_RUBRICS)
    parser.add_argument("--output", type=Path, help="Summary JSON path")
    parser.add_argument("--markdown-output", type=Path, help="Human-readable Markdown report path")
    parser.add_argument("--allow-failures", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise SystemExit(f"{path}:{line_number}: JSONL record must be an object")
        records.append(value)
    if not records:
        raise SystemExit("input contains no records")
    return records


def _matches(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I | re.S) is not None


def _snippet(pattern: str, text: str, radius: int = 90) -> str | None:
    match = re.search(pattern, text, re.I | re.S)
    if not match:
        return None
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    snippet = re.sub(r"\s+", " ", text[start:end]).strip()
    return snippet[:260]


def _group_evidence(
    groups: list[list[str]], text: str, max_span: int
) -> tuple[bool, list[dict[str, Any]], str | None]:
    candidates: list[list[tuple[int, int, str]]] = []
    group_results: list[dict[str, Any]] = []
    for group in groups:
        matches: list[tuple[int, int, str]] = []
        for pattern in group:
            for match in re.finditer(pattern, text, re.I | re.S):
                matches.append((match.start(), match.end(), pattern))
                if len(matches) >= 20:
                    break
        matches.sort(key=lambda item: item[0])
        candidates.append(matches)
        matched = matches[0] if matches else None
        group_results.append(
            {
                "passed": matched is not None,
                "matched_pattern": matched[2] if matched else None,
                "evidence": _snippet(matched[2], text) if matched else None,
            }
        )
    if any(not matches for matches in candidates):
        return False, group_results, None

    best: tuple[int, tuple[tuple[int, int, str], ...]] | None = None
    for combo in itertools.product(*candidates):
        span = max(item[1] for item in combo) - min(item[0] for item in combo)
        if best is None or span < best[0]:
            best = (span, combo)
    assert best is not None
    span, combo = best
    start = max(0, min(item[0] for item in combo) - 100)
    end = min(len(text), max(item[1] for item in combo) + 100)
    evidence = re.sub(r"\s+", " ", text[start:end]).strip()[:500]
    return span <= max_span, group_results, evidence


def grade_output(text: str, rubric: dict[str, Any]) -> dict[str, Any]:
    criteria_results: list[dict[str, Any]] = []
    earned = 0
    total = 0
    for criterion in rubric.get("criteria", []):
        weight = int(criterion["weight"])
        total += weight
        groups = criterion.get("all_groups", [])
        max_span = int(criterion.get("max_span", 800))
        passed, group_results, combined_evidence = _group_evidence(
            groups, text, max_span
        )

        forbidden_hits = []
        for pattern in criterion.get("must_not_match", []):
            if _matches(pattern, text):
                forbidden_hits.append(
                    {"pattern": pattern, "evidence": _snippet(pattern, text)}
                )
        matched_groups = sum(1 for item in group_results if item["passed"])
        group_count = len(group_results)
        group_coverage = matched_groups / group_count if group_count else 0.0
        if forbidden_hits:
            passed = False
            earned_points = 0.0
            status = "failed"
        elif passed:
            earned_points = float(weight)
            status = "passed"
        elif matched_groups:
            # Partial evidence is informative but capped at half of the criterion weight.
            earned_points = round(weight * group_coverage * 0.5, 2)
            status = "partial"
        else:
            earned_points = 0.0
            status = "failed"

        earned += earned_points
        criteria_results.append(
            {
                "id": criterion["id"],
                "label": criterion["label"],
                "weight": weight,
                "earned_points": earned_points,
                "status": status,
                "passed": passed,
                "matched_groups": matched_groups,
                "group_count": group_count,
                "groups": group_results,
                "combined_evidence": combined_evidence,
                "max_span": max_span,
                "forbidden_hits": forbidden_hits,
            }
        )

    raw_score = round((earned / total) * 100, 1) if total else 0.0
    penalties = []
    penalty_points = 0
    for penalty in rubric.get("penalties", []):
        trigger = next(
            (pattern for pattern in penalty.get("trigger_patterns", []) if _matches(pattern, text)),
            None,
        )
        mitigated = any(_matches(pattern, text) for pattern in penalty.get("unless_patterns", []))
        applied = bool(trigger and not mitigated)
        points = int(penalty.get("points", 0)) if applied else 0
        penalty_points += points
        penalties.append(
            {
                "id": penalty["id"],
                "label": penalty["label"],
                "applied": applied,
                "points": points,
                "trigger_pattern": trigger,
                "evidence": _snippet(trigger, text) if trigger else None,
                "mitigated": mitigated,
            }
        )

    final_score = max(0.0, round(raw_score - penalty_points, 1))
    passing_score = float(rubric.get("passing_score", 75))
    return {
        "passed": final_score >= passing_score,
        "score": final_score,
        "raw_score": raw_score,
        "penalty_points": penalty_points,
        "passing_score": passing_score,
        "criteria": criteria_results,
        "penalties": penalties,
        "output_characters": len(text),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# CloudBox Behavior Eval 人類可讀評分報告",
        "",
        f"- 輸入：`{report['input']}`",
        f"- 產生時間：{report['generated_at_utc']}",
        f"- 可評分紀錄：{report['graded_records']}",
        f"- 通過紀錄：{report['passed_records']}",
        f"- 平均分數：**{report['average_score']:.1f} / 100**",
        "",
        "> 此分數是 deterministic evidence-coverage score：檢查回答是否明確包含指定工程證據。它不是完整的語意正確性證明，也不取代人工架構審查。",
        "",
    ]
    for result in report["results"]:
        lines.extend(
            [
                f"## {result['case_id']} — Attempt {result['attempt']}",
                "",
                f"- 狀態：{'通過' if result['grade']['passed'] else '未通過'}",
                f"- 分數：**{result['grade']['score']:.1f} / 100**（門檻 {result['grade']['passing_score']:.1f}）",
                f"- 原始涵蓋分：{result['grade']['raw_score']:.1f}",
                f"- 扣分：{result['grade']['penalty_points']}",
                "",
                "| 準則 | 權重 | 得分 | 結果 |",
                "|---|---:|---:|---|",
            ]
        )
        for criterion in result["grade"]["criteria"]:
            status = criterion.get("status")
            if status == "passed":
                status_text = "通過"
            elif status == "partial":
                status_text = f"部分（{criterion['matched_groups']}/{criterion['group_count']}）"
            else:
                status_text = "缺少／不合格"
            lines.append(
                f"| {criterion['label']} | {criterion['weight']} | "
                f"{criterion.get('earned_points', 0):.1f} | {status_text} |"
            )
        applied = [p for p in result["grade"]["penalties"] if p["applied"]]
        if applied:
            lines.extend(["", "### 扣分"])
            for item in applied:
                lines.append(f"- -{item['points']}：{item['label']}")
        missing = [c for c in result["grade"]["criteria"] if not c["passed"]]
        if missing:
            lines.extend(["", "### 下一步補強"])
            for item in missing:
                lines.append(f"- {item['label']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rubrics = load_json(args.rubrics)
    records = load_jsonl(args.input)
    case_rubrics = rubrics.get("cases", {})
    results = []
    ungraded = []
    for record in records:
        case_id = record.get("case_id")
        rubric = case_rubrics.get(case_id)
        if rubric is None:
            ungraded.append(str(case_id))
            continue
        if record.get("eval_kind") != "behavior":
            ungraded.append(str(case_id))
            continue
        if record.get("behavior_status") != "completed":
            grade = {
                "passed": False,
                "score": 0.0,
                "raw_score": 0.0,
                "penalty_points": 0,
                "passing_score": float(rubric.get("passing_score", 75)),
                "criteria": [],
                "penalties": [],
                "output_characters": 0,
                "error": "behavior stage did not complete",
            }
        else:
            output = record.get("behavior_output")
            if not isinstance(output, str) or not output.strip():
                grade = {
                    "passed": False,
                    "score": 0.0,
                    "raw_score": 0.0,
                    "penalty_points": 0,
                    "passing_score": float(rubric.get("passing_score", 75)),
                    "criteria": [],
                    "penalties": [],
                    "output_characters": 0,
                    "error": "behavior_output is empty",
                }
            else:
                grade = grade_output(output, rubric)
        results.append(
            {
                "case_id": case_id,
                "attempt": record.get("attempt"),
                "model": record.get("model_returned") or record.get("model_requested"),
                "provider": record.get("provider"),
                "behavior_status": record.get("behavior_status"),
                "grade": grade,
            }
        )

    if not results:
        raise SystemExit("no behavior records matched a configured rubric")
    scores = [float(item["grade"]["score"]) for item in results]
    passed = sum(1 for item in results if item["grade"]["passed"])
    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input": str(args.input),
        "rubrics": str(args.rubrics),
        "graded_records": len(results),
        "passed_records": passed,
        "average_score": round(sum(scores) / len(scores), 1),
        "gate": {"passed": passed == len(results)},
        "ungraded_case_ids": sorted(set(ungraded)),
        "results": results,
    }
    output = args.output or args.input.with_name(args.input.stem + "-behavior-summary.json")
    markdown_output = args.markdown_output or output.with_suffix(".md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "graded_records": len(results),
                "passed_records": passed,
                "average_score": report["average_score"],
                "gate": report["gate"],
                "output": str(output),
                "markdown_output": str(markdown_output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not report["gate"]["passed"] and not args.allow_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
