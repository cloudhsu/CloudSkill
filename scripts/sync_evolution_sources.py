from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from evolution_source_contract import load_source_registry, sync_source


def main() -> int:
    parser = argparse.ArgumentParser(description="Token-free Git evolution source synchronization.")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--source-id", required=True)
    args = parser.parse_args()
    try:
        result = sync_source(args.source_id, load_source_registry(Path(args.registry)), Path(args.exchange), dict(os.environ))
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "source_id": args.source_id, "error": str(exc), "model_calls": 0}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
