#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from multimodel_panel_contract import aggregate_costs, classify_panel, validate_panel_record


def bounded_claude_request(packet: bytes, schema: dict[str, Any], limits: dict[str, Any], *, preflight: Callable[[], dict[str, Any]] | None = None, strict_call: Callable[[bytes, dict[str, Any]], dict[str, Any]] | None = None, plain_call: Callable[[bytes], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Perform one strict request and at most one zero-token plain-output fallback."""
    if limits.get("max_attempts") not in {1, 2}:
        raise ValueError("max_attempts must be 1 or 2")
    if preflight is None or strict_call is None or plain_call is None:
        raise ValueError("bounded Claude transport requires explicit preflight and call adapters")
    packet_hash = hashlib.sha256(packet).hexdigest()
    if preflight().get("authenticated") is not True:
        return {"status": "BLOCKED", "attempts": 0, "fallback": None, "packet_hash": packet_hash}
    first = strict_call(packet, schema)
    first["packet_hash"] = packet_hash
    if first.get("status") != "BLOCKED" or first.get("tokens") not in {0, None} or limits["max_attempts"] == 1:
        first.update(attempts=1, fallback=None)
        return first
    second = plain_call(packet)
    second.update(packet_hash=packet_hash, attempts=2, fallback="bounded_plain_output")
    return second


def write_panel(path: Path, record: dict[str, Any]) -> None:
    errors = validate_panel_record(record)
    if errors:
        raise ValueError("invalid panel record: " + "; ".join(errors))
    if path.exists():
        raise ValueError("panel output already exists; stable panel publication is single-writer")
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {"panel": record, "cost_totals": aggregate_costs(record["workers"])}
    path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dry_run(workers_path: Path, output_path: Path) -> dict[str, Any]:
    workers = json.loads(workers_path.read_text(encoding="utf-8"))
    record = {"schema_version": 1, "panel_id": "fixture-panel", "status": classify_panel(workers), "workers": workers}
    write_panel(output_path, record)
    return record
