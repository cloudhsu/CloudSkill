#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from multimodel_panel_contract import aggregate_costs, classify_panel, validate_panel_record
    from run_multimodel_panel import bounded_claude_request, dry_run
except ModuleNotFoundError as exc:
    print(f"ERROR: cannot load multi-model panel contract: {exc}")
    raise SystemExit(1)


def worker(label: str, family: str, role: str, *, status: str = "PASS") -> dict:
    return {
        "worker_id": f"worker-{label}",
        "blind_label": label,
        "family": family,
        "role": role,
        "provider": family,
        "requested_model": role,
        "canonical_model": f"{family}-{role}" if status == "PASS" else None,
        "status": status,
        "output_path": f"workers/{label}.json",
        "packet_hash": "1" * 64,
        "prompt_hash": "2" * 64,
        "raw_output_hash": "3" * 64 if status == "PASS" else None,
        "adapter_version": "fixture-adapter-1", "transport_mode": "fixture",
        "tokens": {"input": 10, "cache": 2, "output": 3, "reasoning": 1},
        "latency_ms": 10, "attempts": 1, "retries": 0, "fallback": None,
        "failure_layer": None, "verdict": status, "findings_path": f"workers/{label}-findings.json",
        "cost": {"kind": "provider_reported", "amount": 0.01, "currency": "USD"} if status == "PASS" else None,
    }


workers = [
    worker("A", "gpt", "efficient"), worker("B", "gpt", "frontier"),
    worker("C", "claude", "efficient"), worker("D", "claude", "frontier"),
]
record = {"schema_version": 1, "panel_id": "panel-1", "status": "COMPLETE_2X2", "identity_map_hash": "4" * 64, "adjudication_path": "panel/adjudication.json", "workers": workers}
errors = validate_panel_record(record)
if errors:
    raise SystemExit("valid panel rejected: " + "; ".join(errors))
if classify_panel(workers) != "COMPLETE_2X2":
    raise SystemExit("complete 2x2 panel was not classified complete")

mutations = [
    ({**record, "workers": [workers[0], {**workers[1], "output_path": workers[0]["output_path"]}, *workers[2:]]}, "duplicate output path"),
    ({**record, "workers": [{**workers[0], "canonical_model": None}, *workers[1:]]}, "canonical model"),
    ({**record, "blind_label_map": {"A": "gpt"}}, "blind label map"),
    ({**record, "aggregate_score": 99.0}, "aggregate score"),
    ({**record, "workers": [{**workers[0], "blind_label": workers[0]["worker_id"]}, *workers[1:]]}, "unblinded worker identity"),
    ({**record, "workers": [{**workers[0], "cost": {"amount": 0.01}}, *workers[1:]]}, "unconstrained cost"),
    ({**record, "status": "DEGRADED", "workers": [*workers[:3], {**worker("D", "claude", "frontier", status="BLOCKED"), "cost": {"kind": "usage_only", "amount": 1, "currency": "tokens"}}]}, "blocked worker cost without canonical identity"),
    ({**record, "workers": [*workers[:3], worker("D", "claude", "frontier", status="BLOCKED")]}, "blocked worker"),
]
for mutated, label in mutations:
    if not validate_panel_record(mutated):
        raise SystemExit(f"{label} mutation was accepted")

blocked = [*workers[:3], worker("D", "claude", "frontier", status="BLOCKED")]
if classify_panel(blocked) != "DEGRADED":
    raise SystemExit("blocked worker was mislabeled as a complete 2x2")
if classify_panel([worker(label, family, role, status="BLOCKED") for label, family, role in (("A", "gpt", "efficient"), ("B", "gpt", "frontier"), ("C", "claude", "efficient"), ("D", "claude", "frontier"))]) != "BLOCKED":
    raise SystemExit("all-blocked panel did not use the declared BLOCKED state")

costs = aggregate_costs(workers)
if len(costs) != 4 or any("score" in item for item in costs):
    raise SystemExit("provider/model cost separation failed")

calls: list[str] = []
def preflight() -> dict:
    calls.append("preflight")
    return {"authenticated": True}
def strict(_packet: bytes, _schema: dict) -> dict:
    calls.append("strict")
    return {"status": "BLOCKED", "tokens": 0, "error": "Not logged in"}
def plain(_packet: bytes) -> dict:
    calls.append("plain")
    return {"status": "PASS", "raw_output": '{"verdict":"PASS"}', "tokens": 12, "canonical_model": "claude-sonnet"}

fallback_schema = {
    "type": "object", "additionalProperties": False, "required": ["verdict"],
    "properties": {"verdict": {"enum": ["PASS", "FAIL"]}},
}
fallback = bounded_claude_request(b"frozen", fallback_schema, {"max_attempts": 2}, preflight=preflight, strict_call=strict, plain_call=plain)
if (
    calls != ["preflight", "strict", "plain"] or fallback["status"] != "PASS"
    or fallback["fallback"] != "bounded_plain_output"
    or fallback.get("fallback_prompt_hash") in {None, fallback.get("packet_hash")}
):
    raise SystemExit("zero-token authenticated Claude fallback did not remain bounded")

def invalid_plain(_packet: bytes) -> dict:
    return {"status": "PASS", "raw_output": '{}', "tokens": 1, "canonical_model": "claude-sonnet"}
invalid_fallback = bounded_claude_request(
    b"frozen", fallback_schema, {"max_attempts": 2}, preflight=lambda: {"authenticated": True},
    strict_call=lambda _packet, _schema: {"status": "BLOCKED", "tokens": 0}, plain_call=invalid_plain,
)
if invalid_fallback.get("status") != "BLOCKED" or not invalid_fallback.get("validation_errors"):
    raise SystemExit("schema-invalid Claude plain fallback was accepted")

boolean_tokens_calls: list[str] = []
boolean_tokens = bounded_claude_request(
    b"frozen", fallback_schema, {"max_attempts": 2}, preflight=lambda: {"authenticated": True},
    strict_call=lambda _packet, _schema: {"status": "BLOCKED", "tokens": False},
    plain_call=lambda _packet: boolean_tokens_calls.append("plain") or {},
)
if boolean_tokens_calls or boolean_tokens.get("attempts") != 1:
    raise SystemExit("boolean token value was misclassified as a zero-token fallback")

unknown_tokens_calls: list[str] = []
unknown_tokens = bounded_claude_request(
    b"frozen", fallback_schema, {"max_attempts": 2}, preflight=lambda: {"authenticated": True},
    strict_call=lambda _packet, _schema: {"status": "BLOCKED", "tokens": None},
    plain_call=lambda _packet: unknown_tokens_calls.append("plain") or {},
)
if unknown_tokens_calls or unknown_tokens.get("attempts") != 1:
    raise SystemExit("unknown token evidence was misclassified as a verified zero-token fallback")

with tempfile.TemporaryDirectory(prefix="cloudbox-panel-test-") as temp:
    root = Path(temp)
    fixture = root / "workers.json"
    output = root / "panel.json"
    fixture.write_text(json.dumps(workers), encoding="utf-8")
    dry_run(fixture, output)
    if not output.is_file():
        raise SystemExit("four-worker dry run did not publish one panel record")
    try:
        dry_run(fixture, output)
    except ValueError:
        pass
    else:
        raise SystemExit("single-writer panel publication allowed overwrite")

print("Validated reproducible multi-model panel contract, degradation, cost separation, and bounded Claude fallback.")
