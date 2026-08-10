"""Git-based transport for interaction/project-history Eval candidates
between machines and agents, without putting private pre-review candidates
into CloudSkill's own Git history.

`.local/eval-inbox/` is gitignored on every machine (by design -- candidates
are unreviewed evidence, not formal Evals), so having CloudSkill repository
access on a second machine does not by itself get candidates from there to
here. This script pushes/pulls through a separate, private "exchange"
repository the user owns and configures via `eval_exchange_repo` in
`.cloudskill/config.local.json` / `~/.cloudskill/config.json`.

--push (run where candidates were captured): zips new files from
  eval_inbox/{candidates,manual-review}/ in the same format
  export_eval_candidate.py produces, commits+pushes it to the exchange
  repository's incoming/ folder, then moves the source files locally into
  eval_inbox/synced/ (never deletes, mirrors the existing
  candidates/manual-review/processed/rejected bookkeeping pattern).

--pull (run on the machine that hosts the CloudSkill repository): pulls the
  exchange repository and copies any zip in incoming/ that is not already in
  eval_inbox/imports/processed/ into eval_inbox/imports/, ready for
  scripts/import_eval_candidates.py -- this script does not itself validate,
  sanitize, or merge candidates; that remains import_eval_candidates.py's job.

Never commits raw transcripts, credentials, or anything import_eval_candidates.py
would reject; the exchange repository carries only what
capture_eval_candidate.py already sanitized before writing to eval_inbox.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_eval_candidate import find_project_config, load_config  # noqa: E402
from eval_bundle_contract import build_bundle_manifest, bundle_filename  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLONE_DIR = ROOT / ".local" / "eval-exchange-clone"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Git-based transport for Eval candidates between machines.")
    parser.add_argument("--push", action="store_true", help="Send locally captured candidates to the exchange repository.")
    parser.add_argument("--pull", action="store_true", help="Fetch candidate zips from the exchange repository into eval_inbox/imports/.")
    parser.add_argument("--config", help="Explicit config JSON path. Defaults to project/user config discovery.")
    parser.add_argument("--label", help="Machine/session label for the zip filename. Default: hostname.")
    parser.add_argument("--clone-dir", type=Path, default=DEFAULT_CLONE_DIR)
    return parser.parse_args()


def resolve_config(explicit: str | None) -> dict[str, Any]:
    config_path = Path(explicit).expanduser().resolve() if explicit else find_project_config(ROOT)
    if config_path is None:
        config_path = Path.home() / ".cloudskill" / "config.json"
    if not config_path.is_file():
        raise SystemExit(f"no CloudSkill local config found (looked for {config_path})")
    return load_config(config_path)


def run_git(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip()}")
    return result


def ensure_clone(exchange_repo: str, clone_dir: Path) -> Path:
    if (clone_dir / ".git").is_dir():
        run_git(["pull", "--ff-only"], cwd=clone_dir)
    else:
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
        run_git(["clone", exchange_repo, str(clone_dir)], cwd=clone_dir.parent)
    (clone_dir / "incoming").mkdir(exist_ok=True)
    return clone_dir


def safe_label(label: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in label) or "machine"


def do_push(config: dict[str, Any], args: argparse.Namespace) -> int:
    exchange_repo = config.get("eval_exchange_repo")
    if not exchange_repo:
        raise SystemExit("config has no 'eval_exchange_repo'; add it to .cloudskill/config.local.json or ~/.cloudskill/config.json")

    inbox: Path = config["_inbox_path"]
    pending = [
        path
        for folder in ("candidates", "manual-review")
        for path in sorted((inbox / folder).glob("*.json"))
    ]
    if not pending:
        print("Nothing to push: no candidates in candidates/ or manual-review/.")
        return 0

    clone_dir = ensure_clone(exchange_repo, args.clone_dir)
    label = safe_label(args.label or socket.gethostname())
    payload_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in pending}
    manifest = build_bundle_manifest(
        cloudbox_version=str(config.get("cloudskill_version", (ROOT / "VERSION").read_text().strip())),
        candidate_schema_version="1.0", host=str(config.get("export_host", "codex")),
        agent_name=str(config.get("export_agent_name", "codex")),
        export_project_name=str(config.get("export_project_name", label)),
        payload_hashes=payload_hashes, bundle_id=uuid.uuid4().hex,
    )
    zip_name = bundle_filename(manifest)
    zip_path = clone_dir / "incoming" / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for path in pending:
            archive.write(path, arcname=path.name)

    run_git(["add", f"incoming/{zip_name}"], cwd=clone_dir)
    run_git(["commit", "-m", f"candidates from {label} ({len(pending)} file(s))"], cwd=clone_dir)
    run_git(["push"], cwd=clone_dir)

    synced_dir = inbox / "synced"
    synced_dir.mkdir(exist_ok=True)
    for path in pending:
        path.replace(synced_dir / path.name)

    print(f"Pushed {len(pending)} candidate(s) as {zip_name} to {exchange_repo}")
    print(f"Moved source files to {synced_dir} (not deleted).")
    return 0


def do_pull(config: dict[str, Any], args: argparse.Namespace) -> int:
    exchange_repo = config.get("eval_exchange_repo")
    if not exchange_repo:
        raise SystemExit("config has no 'eval_exchange_repo'; add it to .cloudskill/config.local.json or ~/.cloudskill/config.json")

    inbox: Path = config["_inbox_path"]
    clone_dir = ensure_clone(exchange_repo, args.clone_dir)
    imports_dir = inbox / "imports"
    processed_dir = imports_dir / "processed"
    unsupported_dir = imports_dir / "unsupported"
    imports_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    unsupported_dir.mkdir(parents=True, exist_ok=True)

    already_seen = {path.name for path in processed_dir.glob("*.zip")} | {path.name for path in imports_dir.glob("*.zip")} | {path.name for path in unsupported_dir.glob("*.zip")}
    copied = 0
    for zip_path in sorted((clone_dir / "incoming").glob("*.zip")):
        if zip_path.name in already_seen:
            continue
        target = imports_dir / zip_path.name
        target.write_bytes(zip_path.read_bytes())
        copied += 1
        print(f"Pulled {zip_path.name} -> {target}")

    if copied:
        print(f"Copied {copied} new archive(s) into {imports_dir}.")
        print("Run: python3 scripts/import_eval_candidates.py")
    else:
        print("Nothing new to pull.")
    return 0


def main() -> int:
    args = parse_args()
    if args.push == args.pull:
        raise SystemExit("specify exactly one of --push or --pull")
    config = resolve_config(args.config)
    if args.push:
        return do_push(config, args)
    return do_pull(config, args)


if __name__ == "__main__":
    raise SystemExit(main())
