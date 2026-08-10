#!/usr/bin/env python3
"""Build a deterministic, reviewable Task 4 evidence bundle from local raw runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sanitize_row(row: dict[str, Any]) -> dict[str, Any]:
    clean = json.loads(json.dumps(row))
    metadata = clean.get("provider_metadata")
    if isinstance(metadata, dict):
        metadata.pop("response_id", None)
        metadata.pop("request_id", None)
    return clean


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tc001", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite formal evidence bundle")

    tc001 = json.loads(args.tc001.read_text(encoding="utf-8"))
    remaining = [sanitize_row(row) for row in read_jsonl(args.results)]
    adjudication = json.loads(args.adjudication.read_text(encoding="utf-8"))
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    metadata.pop("output", None)
    bundle = {
        "schema_version": 1,
        "artifact_id": "cloudbox-6.0-task4-reviewable-evidence",
        "sanitization": {
            "removed": ["provider response_id", "provider request_id", "local output path"],
            "raw_provider_outputs_preserved": True,
        },
        "source_hashes": {
            "tc001": sha256(args.tc001),
            "remaining_results": sha256(args.results),
            "adjudication": sha256(args.adjudication),
            "metadata": sha256(args.metadata),
        },
        "tc001": tc001,
        "remaining_results": remaining,
        "semantic_adjudication": adjudication,
        "run_metadata": metadata,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
