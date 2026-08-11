"""Narrow Git and CloudBox bundle operations for the controlled CLI broker."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from import_eval_candidates import import_archives


def _git(arguments: list[str], cwd: Path, timeout: int = 90) -> str:
    result = subprocess.run(["git", *arguments], cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError("registered Git operation failed")
    return result.stdout.strip()


def _ref_fingerprint(repository: Path, remote: str) -> str:
    refs = _git(["for-each-ref", "--format=%(refname):%(objectname)", f"refs/remotes/{remote}/"], repository)
    return hashlib.sha256(refs.encode("utf-8")).hexdigest()


def _inspect(repository: Path) -> tuple[dict[str, Any], list[str]]:
    head = _git(["rev-parse", "HEAD"], repository)
    branch = _git(["branch", "--show-current"], repository)
    dirty = bool(_git(["status", "--porcelain", "--untracked-files=normal"], repository))
    remotes = sorted(item for item in _git(["remote"], repository).splitlines() if item)
    remote_names_hash = hashlib.sha256("\n".join(remotes).encode("utf-8")).hexdigest()
    return {"head": head, "branch": branch, "dirty": dirty, "remote_names_hash": remote_names_hash}, []


def _execute(capability: str, arguments: dict[str, Any]) -> tuple[str, str, dict[str, Any], list[str]]:
    if capability == "git.inspect":
        output, effects = _inspect(Path(arguments["repository"]))
        return "SUCCEEDED", "repository inspected", output, effects
    if capability == "git.fetch":
        repository = Path(arguments["repository"])
        remote = arguments["remote"]
        registered = set(_git(["remote"], repository).splitlines())
        if remote not in registered:
            raise ValueError("requested remote is not registered in repository")
        before = _ref_fingerprint(repository, remote)
        _git(["fetch", "--no-tags", "--prune", remote], repository)
        after = _ref_fingerprint(repository, remote)
        status = "NO_CHANGE" if before == after else "UPDATED"
        return "SUCCEEDED", "registered remote fetched", {"status": status, "refs_hash": after}, [f"remote-tracking refs: {status.lower()}"]
    if capability == "git.import_bundle":
        inbox = Path(arguments["inbox"])
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            totals = import_archives(inbox, [], bool(arguments.get("dry_run", False)))
        return "SUCCEEDED", "versioned bundle import inspected", totals, ["local Eval Inbox import queues evaluated"]
    raise ValueError("unknown registered Git capability")


def make_result(request: dict[str, Any], state: str, summary: str, output: dict[str, Any], effects: list[str], diagnostics: list[str], latency_ms: int) -> dict[str, Any]:
    digest = hashlib.sha256(json.dumps(output, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "contract_version": "1.0",
        "adapter_id": request["adapter_id"],
        "capability_id": request["capability_id"],
        "action_id": request["action_id"],
        "state": state,
        "summary": summary,
        "output": output,
        "artifact_refs": [],
        "observed_side_effects": effects,
        "diagnostics": diagnostics,
        "output_hash": digest,
        "latency_ms": latency_ms,
        "model_calls": 0,
    }


def main() -> int:
    started = time.monotonic()
    request = json.loads(sys.stdin.read())
    try:
        if request.get("operation") not in {"execute", "reconcile"}:
            raise ValueError("unsupported adapter operation")
        state, summary, output, effects = _execute(request["capability_id"], request["arguments"])
        result = make_result(request, state, summary, output, effects, [], int((time.monotonic() - started) * 1000))
    except (KeyError, OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        result = make_result(request, "FAILED", "registered Git operation did not complete", {}, [], [str(exc)], int((time.monotonic() - started) * 1000))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
