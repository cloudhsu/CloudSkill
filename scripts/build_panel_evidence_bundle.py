#!/usr/bin/env python3
"""Build a sanitized, reviewable bundle from one immutable local panel directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sanitize_worker(path: Path) -> dict[str, Any]:
    worker = json.loads(path.read_text(encoding="utf-8"))
    metadata = worker.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("response_id", None)
        metadata.pop("request_id", None)
    return worker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite formal panel evidence")

    directory = args.panel_directory
    panel_path = directory / "panel.json"
    adjudication_path = directory / "adjudication.json"
    attempt_path = directory / "attempt-ledger.json"
    packet_path = directory / "packet.json"
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    worker_paths = sorted(directory.glob("final-*.json"))
    adjudication = json.loads(adjudication_path.read_text(encoding="utf-8"))
    bundle = {
        "schema_version": 1,
        "artifact_id": args.output.stem,
        "sanitization": {
            "removed": ["provider response_id", "provider request_id", "absolute local paths"],
            "raw_judgments_preserved": True,
            "packet_content_reproducible_from_source_candidate": True,
        },
        "source_hashes": {
            "panel": sha256(panel_path),
            "adjudication": sha256(adjudication_path),
            "attempt_ledger": sha256(attempt_path),
            "packet": sha256(packet_path),
            "workers": {path.name: sha256(path) for path in worker_paths},
        },
        "source_candidate": adjudication.get("source_candidate"),
        "panel": panel,
        "adjudication": adjudication,
        "attempt_ledger": json.loads(attempt_path.read_text(encoding="utf-8")),
        "raw_workers": {path.name: sanitize_worker(path) for path in worker_paths},
    }
    for worker in bundle["panel"].get("panel", {}).get("workers", []):
        output_path = worker.get("output_path")
        if isinstance(output_path, str):
            worker["output_path"] = Path(output_path).name
        findings_path = worker.get("findings_path")
        if isinstance(findings_path, str):
            worker["findings_path"] = Path(findings_path).name
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
