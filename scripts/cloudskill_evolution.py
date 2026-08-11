from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from evolution_source_contract import load_source_registry, sync_source
from tool_adapter_contract import load_registry
from tool_execution_broker import ExecutionContext, execute_prepared, prepare_invocation


def _assignments(values: list[str], *, paths: bool = False) -> dict:
    result = {}
    for value in values:
        name, separator, item = value.partition("=")
        if not separator or not name or not item:
            raise ValueError("reference assignments must use NAME=value")
        result[name] = Path(item).expanduser().resolve() if paths else item
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="CloudBox evolution operation controller.")
    sub = parser.add_subparsers(dest="area", required=True)
    source = sub.add_parser("source"); source_sub = source.add_subparsers(dest="action", required=True)
    sync = source_sub.add_parser("sync"); sync.add_argument("--registry", required=True); sync.add_argument("--exchange", required=True); sync.add_argument("--source-id", required=True)
    tool = sub.add_parser("tool"); tool_sub = tool.add_subparsers(dest="action", required=True)
    invoke = tool_sub.add_parser("invoke")
    invoke.add_argument("--registry", required=True)
    invoke.add_argument("--invocation", required=True)
    invoke.add_argument("--state-dir", required=True)
    invoke.add_argument("--root-ref", action="append", default=[])
    invoke.add_argument("--secret-ref", action="append", default=[])
    invoke.add_argument("--authority", action="append", default=[])
    invoke.add_argument("--owner-id")
    invoke.add_argument("--fencing-token", type=int)
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
    if args.area == "tool":
        invocation = json.loads(Path(args.invocation).read_text(encoding="utf-8"))
        secret_names = _assignments(args.secret_ref)
        secrets = {name: os.environ.get(environment_name, "") for name, environment_name in secret_names.items()}
        context = ExecutionContext(
            root_refs=_assignments(args.root_ref, paths=True),
            secret_values=secrets,
            approved_authority=set(args.authority),
            repository_root=Path(__file__).resolve().parents[1],
            owner_id=args.owner_id,
            fencing_token=args.fencing_token,
        )
        prepared = prepare_invocation(invocation, load_registry(Path(args.registry)), context)
        state_path = Path(args.state_dir).expanduser().resolve() / f"{invocation['action_id']}.json"
        result = execute_prepared(prepared, state_path, context)
        print(json.dumps(result, sort_keys=True)); return 0
    if not args.approve:
        print(json.dumps({"status": "REFUSED", "reason": "explicit --approve is required", "operation_id": args.operation_id})); return 2
    print(json.dumps({"status": "AUTHORIZED", "operation": f"{args.area}.{args.action}", "operation_id": args.operation_id, "execution": "MANUAL_REQUIRED"}, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
