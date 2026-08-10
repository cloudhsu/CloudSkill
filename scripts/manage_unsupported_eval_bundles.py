from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or explicitly delete unsupported Eval bundles.")
    parser.add_argument("action", choices=("inspect", "delete"))
    parser.add_argument("--directory", required=True)
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--confirm")
    args = parser.parse_args()
    directory = Path(args.directory).expanduser().resolve()
    matches = []
    for sidecar in directory.glob("*.status.json"):
        value = json.loads(sidecar.read_text(encoding="utf-8"))
        if value.get("bundle_id") == args.bundle_id:
            matches.append((sidecar, value))
    if len(matches) != 1:
        raise SystemExit("bundle ID did not resolve to exactly one unsupported bundle")
    sidecar, value = matches[0]
    archive = directory / value["archive"]
    if archive.parent != directory or not archive.is_file():
        raise SystemExit("unsupported archive is missing or unsafe")
    if args.action == "inspect":
        print(json.dumps({"bundle_id": value["bundle_id"], "status": value["status"], "archive": archive.name}, indent=2))
        return 0
    if args.confirm != args.bundle_id:
        raise SystemExit("delete requires --confirm with the exact bundle ID")
    archive.unlink()
    sidecar.unlink()
    print(f"Deleted unsupported bundle {args.bundle_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
