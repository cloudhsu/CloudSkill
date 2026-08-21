from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True
    ).stdout


def changed_paths(base_ref: str = "HEAD") -> list[str]:
    tracked = git_bytes(
        "diff", "--name-only", "--no-renames", "-z", base_ref, "--"
    )
    untracked = git_bytes("ls-files", "--others", "--exclude-standard", "-z")
    values = {
        os.fsdecode(raw)
        for raw in (tracked + untracked).split(b"\0")
        if raw
    }
    return sorted(values)


def file_record(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists() and not path.is_symlink():
        return {"path": relative, "state": "deleted"}
    if path.is_symlink():
        payload = os.readlink(path).encode("utf-8")
        kind = "symlink"
    elif path.is_file():
        payload = path.read_bytes()
        kind = "file"
    else:
        raise ValueError(f"packet path is not a file or symlink: {relative}")
    return {
        "path": relative,
        "state": kind,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def build_manifest(
    excludes: set[str], base_ref: str = "HEAD"
) -> dict[str, Any]:
    resolved_base = git_bytes("rev-parse", base_ref).decode("ascii").strip()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "base_head": resolved_base,
        "exclusions": sorted(excludes),
        "files": [
            file_record(path)
            for path in changed_paths(base_ref)
            if path not in excludes
        ],
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    payload["packet_id"] = "sha256:" + hashlib.sha256(canonical).hexdigest()
    return payload


def verify_manifest(payload: dict[str, Any]) -> bool:
    claimed = payload.get("packet_id")
    unsigned = {key: value for key, value in payload.items() if key != "packet_id"}
    canonical = json.dumps(
        unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return claimed == "sha256:" + hashlib.sha256(canonical).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze a Git working-tree Skill review packet manifest."
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Git baseline to compare against (default: HEAD)",
    )
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    relative_output = output.relative_to(ROOT).as_posix()
    excludes = {relative_output, *args.exclude}
    payload = build_manifest(excludes, args.base_ref)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not verify_manifest(payload):
        raise SystemExit("packet manifest failed self-verification")
    print(payload["packet_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
