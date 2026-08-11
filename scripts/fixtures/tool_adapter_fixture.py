from __future__ import annotations

import json
import sys
import time

request = json.loads(sys.stdin.read())
mode = request.get("arguments", {}).get("mode", "success")
if mode == "timeout":
    time.sleep(2)
if mode == "malformed":
    print("not-json")
    raise SystemExit(0)
if mode == "oversized":
    print("x" * 5000)
    raise SystemExit(0)

secret = request.get("secrets", {}).get("FIXTURE_SECRET", "")
diagnostics = [f"secret={secret}"] if mode == "leak" else []
result = {
    "contract_version": "1.0",
    "adapter_id": request["adapter_id"],
    "capability_id": request["capability_id"],
    "action_id": request["action_id"],
    "state": "SUCCEEDED",
    "summary": "fixture complete",
    "output": {"status": "NO_CHANGE" if mode == "no-change" else "OK"},
    "artifact_refs": [],
    "observed_side_effects": [],
    "diagnostics": diagnostics,
    "output_hash": "0" * 64,
    "latency_ms": 1,
    "model_calls": 0,
}
print(json.dumps(result))
