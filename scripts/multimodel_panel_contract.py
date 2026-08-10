from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import task_continuity_runner as schema_runtime

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "evals/runtime/contracts/multimodel-panel.schema.json"


def classify_panel(workers: list[dict[str, Any]]) -> str:
    if not workers:
        return "INCOMPLETE"
    if all(worker.get("status") == "BLOCKED" for worker in workers):
        return "BLOCKED"
    if any(worker.get("status") == "BLOCKED" for worker in workers):
        return "DEGRADED"
    cells = {(worker.get("family"), worker.get("role")) for worker in workers if worker.get("status") in {"PASS", "FAIL", "MANUAL_REQUIRED"}}
    required = {("gpt", "efficient"), ("gpt", "frontier"), ("claude", "efficient"), ("claude", "frontier")}
    if cells == required and len(workers) == 4:
        return "COMPLETE_2X2" if all(worker.get("status") == "PASS" for worker in workers) else "COMPLETE_UNRESOLVED"
    return "INCOMPLETE"


def validate_panel_record(record: Any, schema_path: Path = CONTRACT_PATH) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read panel schema: {exc}"]
    errors = schema_runtime.validate_schema_instance(record, schema)
    if not isinstance(record, dict):
        return errors
    workers = record.get("workers")
    if not isinstance(workers, list) or not workers:
        return errors
    output_paths: set[str] = set()
    identities: set[tuple[str, str]] = set()
    for index, worker in enumerate(workers):
        if not isinstance(worker, dict):
            errors.append(f"workers[{index}] must be an object")
            continue
        path = worker.get("output_path")
        if not isinstance(path, str) or not path.strip():
            errors.append(f"workers[{index}].output_path must be nonblank")
        elif path in output_paths:
            errors.append("worker output paths must be unique")
        else:
            output_paths.add(path)
        identity = (worker.get("family"), worker.get("role"))
        if identity in identities:
            errors.append("family/role cells must be unique")
        identities.add(identity)
        if worker.get("blind_label") == worker.get("worker_id"):
            errors.append("blind label must not expose worker identity")
        status = worker.get("status")
        canonical = worker.get("canonical_model")
        selected = worker.get("selected_model")
        returned = worker.get("provider_returned_model")
        identity_evidence = worker.get("model_identity_evidence")
        raw_hash = worker.get("raw_output_hash")
        cost = worker.get("cost")
        fallback = worker.get("fallback")
        fallback_hash = worker.get("fallback_prompt_hash")
        if fallback is None and fallback_hash is not None:
            errors.append(f"workers[{index}] no-fallback evidence cannot carry a fallback prompt hash")
        if fallback is not None and (
            not isinstance(fallback_hash, str) or len(fallback_hash) != 64
            or fallback_hash == worker.get("prompt_hash")
        ):
            errors.append(f"workers[{index}] fallback requires a distinct prompt hash")
        if cost is not None:
            if not isinstance(cost, dict) or set(cost) - {"kind", "amount", "currency", "estimate_source", "estimate_date"}:
                errors.append(f"workers[{index}].cost has invalid fields")
            elif (
                cost.get("kind") not in {"provider_reported", "estimated", "usage_only"}
                or not isinstance(cost.get("amount"), (int, float)) or isinstance(cost.get("amount"), bool) or cost.get("amount") < 0
                or not isinstance(cost.get("currency"), str) or not cost.get("currency").strip()
            ):
                errors.append(f"workers[{index}].cost is incomplete")
            elif cost.get("kind") == "estimated" and (
                not isinstance(cost.get("estimate_source"), str) or not cost.get("estimate_source", "").strip()
                or not isinstance(cost.get("estimate_date"), str) or not cost.get("estimate_date", "").strip()
            ):
                errors.append(f"workers[{index}].estimated cost lacks provenance")
        if status in {"PASS", "FAIL", "MANUAL_REQUIRED"}:
            if not isinstance(canonical, str) or not canonical.strip():
                errors.append(f"workers[{index}] completed evidence requires canonical model")
            if not isinstance(raw_hash, str) or len(raw_hash) != 64:
                errors.append(f"workers[{index}] completed evidence requires raw output hash")
            if identity_evidence == "provider_returned":
                if not isinstance(returned, str) or not returned.strip() or canonical != returned:
                    errors.append(f"workers[{index}] provider-returned identity must equal canonical model")
            elif identity_evidence == "explicit_selection":
                aliases = {"default", "codex-default", "claude-default", "sonnet", "opus"}
                if canonical != selected or worker.get("requested_model") != selected or selected in aliases or returned is not None:
                    errors.append(f"workers[{index}] explicit selection requires one fully pinned non-alias model")
            else:
                errors.append(f"workers[{index}] completed evidence requires model identity provenance")
        if status == "BLOCKED" and (canonical is not None or raw_hash is not None or cost is not None):
            errors.append(f"workers[{index}] blocked evidence cannot fabricate returned identity/output/cost")
    classified = classify_panel(workers)
    if record.get("status") != classified:
        errors.append(f"panel status {record.get('status')!r} conflicts with classified status {classified!r}")
    return errors


def aggregate_costs(workers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[tuple[str, str, str, str], float] = defaultdict(float)
    for worker in workers:
        cost = worker.get("cost")
        if not isinstance(cost, dict):
            continue
        key = (worker["provider"], worker["canonical_model"], cost["currency"], cost["kind"])
        totals[key] += cost["amount"]
    return [{"provider": key[0], "canonical_model": key[1], "currency": key[2], "kind": key[3], "amount": round(amount, 12)} for key, amount in sorted(totals.items())]
