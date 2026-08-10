from datetime import datetime, timezone
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eval_bundle_contract import build_bundle_manifest, bundle_filename, normalize_filename_component, validate_bundle_manifest

errors = []
digest = hashlib.sha256(b"candidate").hexdigest()
fixed = datetime(2026, 8, 10, 1, 2, 3, tzinfo=timezone.utc)
m1 = build_bundle_manifest(cloudbox_version="6.1.0", candidate_schema_version="1.0", host="codex", agent_name="codex", export_project_name="engine core", payload_hashes={"candidates/a.json": digest}, now=fixed, bundle_id="a" * 32)
m2 = build_bundle_manifest(cloudbox_version="6.1.0", candidate_schema_version="1.0", host="codex", agent_name="codex", export_project_name="engine core", payload_hashes={"candidates/a.json": digest}, now=fixed, bundle_id="b" * 32)
if bundle_filename(m1) == bundle_filename(m2): errors.append("same-second bundles collide")
if bundle_filename(m1) != "engine-core-codex-codex-20260810T010203Z-aaaaaaaa.zip": errors.append("unexpected bundle filename")
for bad in (dict(m1, bundle_format_version="1.0"), dict(m1, payload_hashes={"x": "z" * 64}), dict(m1, export_project_name="https://private")):
    if not validate_bundle_manifest(bad): errors.append("invalid manifest passed")
try: normalize_filename_component("../")
except ValueError: pass
else: errors.append("unsafe empty component passed")
schema = (ROOT / "evals/interaction/contracts/eval-export-bundle.schema.json").read_text(encoding="utf-8")
for marker in ('"const": "2.0"', '"payload_hashes"', '^[0-9a-f]{64}$'):
    if marker not in schema: errors.append(f"schema missing {marker}")
print("Validated Eval export bundle 2.0 contract")
for error in errors: print(f"ERROR: {error}")
raise SystemExit(1 if errors else 0)
