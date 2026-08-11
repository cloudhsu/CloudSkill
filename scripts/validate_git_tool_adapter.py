from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from import_eval_candidates import import_archives, resolve_private_terms  # noqa: E402
from eval_bundle_contract import build_bundle_manifest  # noqa: E402
from tool_action_store import save_action_atomic, transition_action  # noqa: E402
from tool_execution_broker import ExecutionContext, execute_prepared, prepare_invocation, reconcile_prepared  # noqa: E402

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
reconcile_help = subprocess.run([sys.executable, str(ROOT / "scripts/cloudskill_evolution.py"), "tool", "reconcile", "--help"], text=True, capture_output=True)
if reconcile_help.returncode or "--state-dir" not in reconcile_help.stdout:
    errors.append("controlled tool reconciliation CLI is unavailable")
with tempfile.TemporaryDirectory(prefix="cloudbox-git-adapter-") as temp_name:
    root = Path(temp_name)
    remote = root / "remote.git"
    seed = root / "seed"
    clone = root / "clone"
    inbox = root / "inbox"
    inbox.mkdir()
    terms_path = root / "sensitive-terms.local.txt"
    terms_path.write_text("PrivateFixtureTerm\n", encoding="utf-8")
    config_path = root / "config.local.json"
    config_path.write_text(json.dumps({
        "schema_version": "1.0",
        "cloudskill_version": "6.2.0",
        "cloudskill_repository": str(ROOT),
        "eval_inbox": str(inbox),
        "sensitive_terms_path": str(terms_path),
        "default_sanitization": True,
        "save_raw_transcript": False,
        "auto_modify_skills": False,
        "auto_commit": False,
        "auto_push": False
    }), encoding="utf-8")
    if resolve_private_terms(inbox, config_path) != ["PrivateFixtureTerm"]:
        errors.append("adapter/manual shared config did not resolve private terms")
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
        secret_values={"CLOUDSKILL_CONFIG_PATH": str(config_path)},
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

    reconcile_invocation = invocation("git.fetch", 4, {"repository": "clone", "remote": "origin"}, "grant-000001")
    reconcile_preparation = prepare_invocation(reconcile_invocation, registry, context)
    reconcile_path = root / "actions/reconcile-fetch.json"
    uncertain = save_action_atomic(reconcile_path, reconcile_preparation.action, 0, owner_id=context.owner_id, fencing_token=context.fencing_token, now=context.now_epoch)
    uncertain = transition_action(uncertain, "AUTHORIZED", {"authority_grant_id": "grant-000001"})
    uncertain = save_action_atomic(reconcile_path, uncertain, uncertain["revision"], owner_id=context.owner_id, fencing_token=context.fencing_token, now=context.now_epoch)
    uncertain = transition_action(uncertain, "RUNNING", {"adapter_version": "1.0.0"})
    uncertain = save_action_atomic(reconcile_path, uncertain, uncertain["revision"], owner_id=context.owner_id, fencing_token=context.fencing_token, now=context.now_epoch)
    uncertain = transition_action(uncertain, "UNCERTAIN", {"reason": "fixture transport loss"})
    save_action_atomic(reconcile_path, uncertain, uncertain["revision"], owner_id=context.owner_id, fencing_token=context.fencing_token, now=context.now_epoch)
    reconciled = reconcile_prepared(reconcile_preparation, reconcile_path, context)
    if reconciled["state"] != "SUCCEEDED" or reconciled["output"].get("status") != "OBSERVED_COMPLETE":
        errors.append(f"Git fetch reconciliation did not observe authoritative remote/local refs: {reconciled}")

    bad = invocation("git.fetch", 3, {"repository": "clone", "remote": "unregistered"}, "grant-000001")
    result = execute_prepared(prepare_invocation(bad, registry, context), root / "actions/bad-fetch.json", context)
    if result["state"] != "FAILED":
        errors.append("unregistered Git remote was not a confirmed failure")

    candidate = json.loads((ROOT / ".agents/skills/developing-skills/assets/INTERACTION_EVAL_CANDIDATE.template.json").read_text(encoding="utf-8"))
    candidate["cloudskill_version"] = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    candidate["task_summary"] = "Safe adapter import fixture"
    candidate["expected_skills"] = ["developing-skills"]
    payload = json.dumps(candidate, ensure_ascii=False, indent=2).encode("utf-8")
    payload_name = "INT-adapter-positive.json"
    manifest = build_bundle_manifest(
        cloudbox_version=candidate["cloudskill_version"], candidate_schema_version="1.0",
        host="codex", agent_name="codex", export_project_name="adapter-fixture",
        payload_hashes={payload_name: hashlib.sha256(payload).hexdigest()}, bundle_id="1" * 32,
    )
    imports = inbox / "imports"
    imports.mkdir()
    with zipfile.ZipFile(imports / "adapter-fixture.zip", "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr(payload_name, payload)
    import_request = invocation("git.import_bundle", 5, {"inbox": "inbox", "dry_run": False}, "grant-000001")
    imported = execute_prepared(prepare_invocation(import_request, registry, context), root / "actions/import.json", context)
    if imported["state"] != "SUCCEEDED" or imported["output"].get("candidates") != 1:
        errors.append("adapter import did not preserve configured safe-candidate routing")
    if len(list((inbox / "candidates").glob("*.json"))) != 1 or list((inbox / "manual-review").glob("*.json")):
        errors.append("adapter and manual importer private-term routing diverged")

    totals = import_archives(inbox, ["PrivateFixtureTerm"], True)
    if totals.get("archives") != 0:
        errors.append("manual import compatibility function changed empty-inbox behavior")

for error in errors:
    print(f"ERROR: {error}")
if errors:
    raise SystemExit(1)
print("Validated temporary-repository Git inspect/fetch boundaries and manual import compatibility.")
