from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evolution_source_contract import load_source_registry, sync_source

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
    try: sync_source("fixture", registry, exchange, {})
    except ValueError as exc:
        if str(source) in str(exc): errors.append("secret value leaked in error")
    else: errors.append("missing secret did not fail")
print("Validated token-free Git evolution source synchronization")
controller = (ROOT / "scripts/cloudskill_evolution.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/evolution-source-sync.yml").read_text(encoding="utf-8")
for marker in ('explicit --approve is required', '"execution": "MANUAL_REQUIRED"'):
    if marker not in controller: errors.append(f"controller missing authority marker: {marker}")
if "permissions:\n  contents: read" not in workflow: errors.append("source workflow is not read-only")
if "OPENAI_API_KEY" in workflow: errors.append("source workflow must not receive a model API key")
for error in errors: print(f"ERROR: {error}")
raise SystemExit(1 if errors else 0)
