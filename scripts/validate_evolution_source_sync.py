from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evolution_source_contract import load_source_registry, sync_source
from sync_eval_exchange import candidate_contract

errors = []
with tempfile.TemporaryDirectory(prefix="cloudskill-source-validator-") as tmp_name:
    tmp = Path(tmp_name); source = tmp / "source"; exchange = tmp / "exchange"; source.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.name", "Validator"], cwd=source, check=True)
    subprocess.run(["git", "config", "user.email", "validator@example.invalid"], cwd=source, check=True)
    (source / "README.md").write_text("fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=source, check=True); subprocess.run(["git", "commit", "-qm", "fixture"], cwd=source, check=True)
    registry_path = tmp / "registry.json"
    registry_path.write_text(json.dumps({"schema_version": "1.0", "sources": [{"source_id": "fixture", "url_secret": "FIXTURE_URL", "ref": "HEAD", "paths": ["README.md"]}]}), encoding="utf-8")
    registry = load_source_registry(registry_path); env = {"FIXTURE_URL": str(source)}
    first = sync_source("fixture", registry, exchange, env); second = sync_source("fixture", registry, exchange, env)
    if first["status"] != "STORED" or second["status"] != "NO_CHANGE": errors.append("sync is not idempotent")
    if first["model_calls"] or second["model_calls"]: errors.append("sync invoked a model")
    if str(source) in json.dumps(first): errors.append("source URL/path leaked")
    if len(list((exchange / "sources/fixture/candidates").glob("*.json"))) != 1: errors.append("duplicate candidate stored")
    checkpoint = exchange / "sources/fixture/state/checkpoint.json"
    checkpoint.unlink()
    recovered = sync_source("fixture", registry, exchange, env)
    if recovered["candidate_id"] != first["candidate_id"]: errors.append("partial-write retry changed candidate identity")
    if len(list((exchange / "sources/fixture/candidates").glob("*.json"))) != 1: errors.append("partial-write retry duplicated candidate")
    if not checkpoint.is_file(): errors.append("partial-write retry did not restore checkpoint")
    first_fingerprint = first["commit_fingerprint"]
    (source / "README.md").write_text("fixture changed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=source, check=True); subprocess.run(["git", "commit", "-qm", "content change"], cwd=source, check=True)
    changed = sync_source("fixture", registry, exchange, env)
    if changed["commit_fingerprint"] == first_fingerprint: errors.append("new source commit was not detected")
    try: sync_source("fixture", registry, exchange, {})
    except ValueError as exc:
        if str(source) in str(exc): errors.append("secret value leaked in error")
    else: errors.append("missing secret did not fail")
    contract_dir = tmp / "candidate-contracts"; contract_dir.mkdir()
    first_candidate = contract_dir / "first.json"
    second_candidate = contract_dir / "second.json"
    base_contract = {"cloudskill_version":"6.4.0","schema_version":"1.0","runtime":"codex"}
    first_candidate.write_text(json.dumps(base_contract), encoding="utf-8")
    second_candidate.write_text(json.dumps(base_contract), encoding="utf-8")
    if candidate_contract([first_candidate, second_candidate]) != {
        "cloudbox_version":"6.4.0","candidate_schema_version":"1.0","host":"codex"
    }: errors.append("Eval Exchange did not derive one payload-owned contract")
    for label, changed in (
        ("CloudBox version", {**base_contract,"cloudskill_version":"6.3.0"}),
        ("candidate schema", {**base_contract,"schema_version":"9.9"}),
        ("runtime", {**base_contract,"runtime":"claude"}),
    ):
        second_candidate.write_text(json.dumps(changed), encoding="utf-8")
        try: candidate_contract([first_candidate, second_candidate])
        except ValueError: pass
        else: errors.append(f"Eval Exchange accepted mixed {label} contracts")
    duplicate_left = contract_dir / "left" / "same.json"
    duplicate_right = contract_dir / "right" / "same.json"
    duplicate_left.parent.mkdir(); duplicate_right.parent.mkdir()
    duplicate_left.write_text(json.dumps(base_contract), encoding="utf-8")
    duplicate_right.write_text(json.dumps(base_contract), encoding="utf-8")
    try: candidate_contract([duplicate_left, duplicate_right])
    except ValueError: pass
    else: errors.append("Eval Exchange accepted duplicate archive member names")
print("Validated token-free Git evolution source synchronization")
controller = (ROOT / "scripts/cloudskill_evolution.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/evolution-source-sync.yml").read_text(encoding="utf-8")
for marker in ('explicit --approve is required', '"execution": "MANUAL_REQUIRED"'):
    if marker not in controller: errors.append(f"controller missing authority marker: {marker}")
if "permissions:\n  contents: read" not in workflow: errors.append("source workflow is not read-only")
if "OPENAI_API_KEY" in workflow: errors.append("source workflow must not receive a model API key")
for marker in ('git clone --quiet "$EVOLUTION_EXCHANGE_URL"', 'git -C .local/private-evolution-exchange push 2>/dev/null', 'secrets.EVOLUTION_SOURCE_ID', 'remote details redacted'):
    if marker not in workflow: errors.append(f"source workflow does not persist private Exchange state: {marker}")
exchange_transport = (ROOT / "scripts/sync_eval_exchange.py").read_text(encoding="utf-8")
if 'to {exchange_repo}' in exchange_transport: errors.append("Eval Exchange success output exposes configured remote")
if "result.stderr.strip()" in exchange_transport: errors.append("Eval Exchange failure output exposes Git details")
for error in errors: print(f"ERROR: {error}")
raise SystemExit(1 if errors else 0)
