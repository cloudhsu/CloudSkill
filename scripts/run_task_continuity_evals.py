"""Run task-continuity fixtures through a supplied local provider-output file.

This command deliberately has no model, network, process, Git, or release
adapter.  A future paid provider integration must remain outside this baseline
and inject the callback accepted by ``task_continuity_runner.run_cases``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import task_continuity_runner as runner
import task_continuity_contract as task2


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "agent" / "task-continuity-cases.json"


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"provider fixture contains duplicate JSON object key: {key!r}")
        value[key] = item
    return value


def _read_fixture(path: Path) -> dict[str, Any]:
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except FileNotFoundError as exc:
        raise ValueError(f"missing provider fixture: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid provider fixture JSON: {exc}") from exc
    if not isinstance(fixture, dict):
        raise ValueError("provider fixture must be an object")
    if not isinstance(fixture.get("context"), str) or not fixture["context"].strip():
        raise ValueError("provider fixture.context must be nonblank text")
    if not isinstance(fixture.get("stage"), str) or not fixture["stage"].strip():
        raise ValueError("provider fixture.stage must be nonblank text")
    for field in ("experiment_id", "run_id"):
        if not isinstance(fixture.get(field), str) or not fixture[field].strip():
            raise ValueError(f"provider fixture.{field} must be nonblank text")
    responses = fixture.get("responses")
    if not isinstance(responses, dict):
        raise ValueError("provider fixture.responses must be an object keyed by case_id")
    for case_id, response in responses.items():
        if not isinstance(case_id, str) or not isinstance(response, dict) or set(response) != {"case_id", "text", "metadata"}:
            raise ValueError(f"provider fixture.responses[{case_id!r}] must contain only case_id, text, and metadata")
        if response["case_id"] != case_id:
            raise ValueError(f"provider fixture response key {case_id!r} does not match its case_id")
        if not isinstance(response["text"], str):
            raise ValueError(f"provider fixture.responses[{case_id!r}].text must be text")
    return fixture


def run_fixture(
    cases_path: Path,
    fixture_path: Path,
    output_path: Path,
    *,
    cost_ledger_path: Path | None = None,
) -> list[dict]:
    """Run one pre-supplied local response per case; never invoke a provider."""
    fixture = _read_fixture(fixture_path)
    cases = task2.load_cases(cases_path)
    responses = fixture["responses"]
    case_ids = {case["id"] for case in cases}
    if set(responses) != case_ids:
        raise ValueError("provider fixture response case_ids must exactly match authoritative Task 2 cases")
    provider_identities = {
        (response["metadata"].get("provider"), response["metadata"].get("canonical_model"))
        for response in responses.values() if isinstance(response.get("metadata"), dict)
    }
    if len(provider_identities) != 1 or any(not all(isinstance(value, str) and value.strip() for value in identity) for identity in provider_identities):
        raise ValueError("fixture responses must declare one planned provider/model identity")

    response_sequence = iter([responses[case["id"]] for case in cases])

    def call(_prompt: str, _schema: dict) -> tuple[str, dict]:
        response = next(response_sequence)
        return response["text"], response["metadata"]

    planned_provider, planned_model = next(iter(provider_identities))

    return runner.run_cases(
        cases_path,
        call,
        output_path,
        context=fixture["context"],
        stage=fixture["stage"],
        experiment_id=fixture["experiment_id"],
        run_id=fixture["run_id"],
        cost_ledger_path=cost_ledger_path,
        planned_provider=planned_provider,
        planned_canonical_model=planned_model,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run non-mutating task-continuity fixture evaluations.")
    parser.add_argument("--provider-fixture", required=True, type=Path, help="local JSON fixture; no provider is invoked")
    parser.add_argument("--output", required=True, type=Path, help="result JSONL path")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="Task 2 case suite")
    parser.add_argument("--cost-ledger", type=Path, help="optional append-only local cost ledger JSONL")
    arguments = parser.parse_args()
    rows = run_fixture(
        arguments.cases,
        arguments.provider_fixture,
        arguments.output,
        cost_ledger_path=arguments.cost_ledger,
    )
    print(f"Wrote {len(rows)} non-mutating task-continuity result record(s) to {arguments.output}.")
    print("Provider calls: 0 (local fixture only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
