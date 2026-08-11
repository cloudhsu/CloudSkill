from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from import_eval_candidates import import_archives  # noqa: E402
from tool_execution_broker import ExecutionContext, execute_prepared, prepare_invocation  # noqa: E402

ADAPTER = ROOT / "scripts/git_tool_adapter.py"


def git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def invocation(capability: str, action: int, arguments: dict, authority: str | None) -> dict:
    return {
        "contract_version": "1.0",
        "adapter_id": "git-local",
        "capability_id": capability,
        "action_id": f"act-000000{action:02d}",
        "idempotency_key": f"idem-000000{action:02d}",
        "plan_id": "plan-00000001",
        "plan_revision": 1,
        "arguments": arguments,
        "authority_grant_id": authority,
        "deadline": "2099-08-11T12:00:00Z",
    }


errors: list[str] = []
tool_help = subprocess.run([sys.executable, str(ROOT / "scripts/cloudskill_evolution.py"), "tool", "invoke", "--help"], text=True, capture_output=True)
if tool_help.returncode or any(flag not in tool_help.stdout for flag in ("--root-ref", "--authority", "--owner-id", "--fencing-token")):
    errors.append("controlled tool operator CLI is unavailable")
with tempfile.TemporaryDirectory(prefix="cloudbox-git-adapter-") as temp_name:
    root = Path(temp_name)
    remote = root / "remote.git"
    seed = root / "seed"
    clone = root / "clone"
    inbox = root / "inbox"
    inbox.mkdir()
    git(["init", "--bare", str(remote)])
    git(["init", str(seed)])
    git(["config", "user.email", "fixture@example.invalid"], seed)
    git(["config", "user.name", "Fixture"], seed)
    (seed / "README.md").write_text("one\n", encoding="utf-8")
    git(["add", "README.md"], seed)
    git(["commit", "-m", "one"], seed)
    git(["remote", "add", "origin", str(remote)], seed)
    git(["push", "origin", "HEAD:main"], seed)
    git(["clone", "-b", "main", str(remote), str(clone)])

    registry = json.loads((ROOT / "config/tool-adapters.json").read_text(encoding="utf-8"))
    registry["adapters"][0]["provenance"]["sha256"] = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
    context = ExecutionContext(
        root_refs={"REPOSITORY_ROOT": root, "EVAL_INBOX_ROOT": root},
        secret_values={},
        approved_authority={"git.fetch", "git.import_bundle"},
        repository_root=ROOT,
        owner_id="git-fixture-owner",
        fencing_token=1,
        now_epoch=1760000000,
    )
    inspect = invocation("git.inspect", 1, {"repository": "clone"}, None)
    result = execute_prepared(prepare_invocation(inspect, registry, context), root / "actions/inspect.json", context)
    if result["state"] != "SUCCEEDED" or len(result["output"].get("head", "")) != 40:
        errors.append("git.inspect did not return a bounded HEAD fingerprint")
    if str(remote) in json.dumps(result):
        errors.append("git.inspect exposed the remote URL")

    (seed / "README.md").write_text("two\n", encoding="utf-8")
    git(["commit", "-am", "two"], seed)
    git(["push", "origin", "HEAD:main"], seed)
    before = git(["rev-parse", "refs/remotes/origin/main"], clone)
    fetch = invocation("git.fetch", 2, {"repository": "clone", "remote": "origin"}, "grant-000001")
    result = execute_prepared(prepare_invocation(fetch, registry, context), root / "actions/fetch.json", context)
    after = git(["rev-parse", "refs/remotes/origin/main"], clone)
    if result["state"] != "SUCCEEDED" or before == after:
        errors.append("git.fetch did not update the registered remote-tracking ref")
    if git(["rev-parse", "HEAD"], clone) != before:
        errors.append("git.fetch changed the checked-out branch")

    bad = invocation("git.fetch", 3, {"repository": "clone", "remote": "unregistered"}, "grant-000001")
    result = execute_prepared(prepare_invocation(bad, registry, context), root / "actions/bad-fetch.json", context)
    if result["state"] != "FAILED":
        errors.append("unregistered Git remote was not a confirmed failure")

    totals = import_archives(inbox, [], True)
    if totals.get("archives") != 0:
        errors.append("manual import compatibility function changed empty-inbox behavior")

for error in errors:
    print(f"ERROR: {error}")
if errors:
    raise SystemExit(1)
print("Validated temporary-repository Git inspect/fetch boundaries and manual import compatibility.")
