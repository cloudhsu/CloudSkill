from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from evolution_source_contract import load_source_registry, sync_source


def main() -> int:
    parser = argparse.ArgumentParser(description="CloudBox evolution operation controller.")
    sub = parser.add_subparsers(dest="area", required=True)
    source = sub.add_parser("source"); source_sub = source.add_subparsers(dest="action", required=True)
    sync = source_sub.add_parser("sync"); sync.add_argument("--registry", required=True); sync.add_argument("--exchange", required=True); sync.add_argument("--source-id", required=True)
    for area, action in (("candidate", "review"), ("candidate", "evaluate"), ("evolution", "apply"), ("evolution", "release")):
        command = sub.choices.get(area) or sub.add_parser(area)
        children = getattr(command, "_cloudskill_children", None)
        if children is None:
            children = command.add_subparsers(dest="action", required=True); command._cloudskill_children = children
        child = children.add_parser(action); child.add_argument("--approve", action="store_true"); child.add_argument("--operation-id", required=True)
    args = parser.parse_args()
    if args.area == "source":
        result = sync_source(args.source_id, load_source_registry(Path(args.registry)), Path(args.exchange), dict(os.environ))
        print(json.dumps(result, sort_keys=True)); return 0
    if not args.approve:
        print(json.dumps({"status": "REFUSED", "reason": "explicit --approve is required", "operation_id": args.operation_id})); return 2
    print(json.dumps({"status": "AUTHORIZED", "operation": f"{args.area}.{args.action}", "operation_id": args.operation_id, "execution": "MANUAL_REQUIRED"}, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
