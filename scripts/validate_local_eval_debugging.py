from __future__ import annotations

import csv
import json
import re
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

required = [
    ROOT / "cloudskill-eval",
    ROOT / "cloudskill-eval-codex",
    ROOT / "scripts" / "codex_eval_adapter.py",
    ROOT / "scripts" / "validate_codex_eval_path.py",
    ROOT / "scripts" / "run_local_eval_review.py",
    ROOT / ".agents" / "skills" / "local-runtime-eval-debugging" / "SKILL.md",
    ROOT / ".agents" / "skills" / "local-runtime-eval-debugging" / "agents" / "openai.yaml",
    ROOT / ".agents" / "skills" / "local-runtime-eval-debugging" / "references" / "local-eval-troubleshooting.md",
    ROOT / ".agents" / "skills" / "local-runtime-eval-debugging" / "references" / "codex-runtime-eval.md",
    ROOT / ".agents" / "skills" / "local-runtime-eval-debugging" / "assets" / "LOCAL_EVAL_BUNDLE_CONTRACT.md",
    ROOT / "evals" / "behavior" / "cases" / "local-runtime-eval-debugging.json",
]
for path in required:
    if not path.is_file():
        errors.append(f"missing local Eval debugging file: {path.relative_to(ROOT)}")

launcher = ROOT / "cloudskill-eval"
if launcher.is_file():
    mode = launcher.stat().st_mode
    if not (mode & stat.S_IXUSR):
        errors.append("cloudskill-eval is not executable")
    text = launcher.read_text(encoding="utf-8")
    for marker in ("Python 3.10", "run_local_eval_review.py", "CLOUDSKILL_PYTHON"):
        if marker not in text:
            errors.append(f"cloudskill-eval missing marker: {marker}")

codex_launcher = ROOT / "cloudskill-eval-codex"
if codex_launcher.is_file():
    mode = codex_launcher.stat().st_mode
    if not (mode & stat.S_IXUSR):
        errors.append("cloudskill-eval-codex is not executable")
    text = codex_launcher.read_text(encoding="utf-8")
    for marker in ("--provider codex", "--repeat 1", "--no-refine", "codex login"):
        if marker not in text:
            errors.append(f"cloudskill-eval-codex missing marker: {marker}")

runner = ROOT / "scripts" / "run_local_eval_review.py"
if runner.is_file():
    text = runner.read_text(encoding="utf-8")
    for marker in (
        "LATEST_REVIEW_ZIP.txt",
        "CloudSkill-local-eval-review-latest.zip",
        "CONTEXT_CANDIDATES",
        "behavior_output_initial",
        "behavior-refined",
        "source-snapshot",
        "pipeline_status",
        "evaluation_gate",
        'choices=("ollama", "codex")',
        "codex_preflight",
    ):
        if marker not in text:
            errors.append(f"run_local_eval_review.py missing marker: {marker}")
    result = subprocess.run([sys.executable, "-m", "py_compile", str(runner)], capture_output=True, text=True)
    if result.returncode:
        errors.append(f"run_local_eval_review.py failed py_compile: {result.stderr.strip()}")

skill = ROOT / ".agents" / "skills" / "local-runtime-eval-debugging" / "SKILL.md"
if skill.is_file():
    text = skill.read_text(encoding="utf-8")
    if not re.match(r"^---\nname: local-runtime-eval-debugging\ndescription: Use when", text):
        errors.append("local-runtime-eval-debugging frontmatter is invalid")
    for marker in (
        "one user command and produce one review bundle",
        "Infrastructure failure",
        "Context failure",
        "Evaluation gate failure",
        "Preserve raw behavior before refinement",
    ):
        if marker not in text:
            errors.append(f"local-runtime-eval-debugging missing behavior marker: {marker}")

manifest = ROOT / "SKILL_MANIFEST.json"
if manifest.is_file():
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        names = {item.get("name") for item in payload.get("skills", []) if isinstance(item, dict)}
        if "local-runtime-eval-debugging" not in names:
            errors.append("SKILL_MANIFEST.json does not include local-runtime-eval-debugging")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid SKILL_MANIFEST.json: {exc}")

routing_cases = ROOT / "evals" / "skill-routing-cases.csv"
if routing_cases.is_file():
    with routing_cases.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = {row.get("id") for row in rows}
    for case_id in ("LRED-01", "LRED-02", "LRED-NEG-01"):
        if case_id not in ids:
            errors.append(f"routing case missing: {case_id}")

behavior_case = ROOT / "evals" / "behavior" / "cases" / "local-runtime-eval-debugging.json"
if behavior_case.is_file():
    try:
        payload = json.loads(behavior_case.read_text(encoding="utf-8"))
        types = {item.get("type") for item in payload.get("cases", []) if isinstance(item, dict)}
        missing = {"recognition", "application", "counterexample"} - types
        if missing:
            errors.append(f"local Eval behavior coverage missing: {sorted(missing)}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid local Eval behavior case JSON: {exc}")

validate_pack = ROOT / "scripts" / "validate_pack.py"
if validate_pack.is_file():
    text = validate_pack.read_text(encoding="utf-8")
    if "git ls-files" not in text and '"ls-files"' not in text:
        errors.append("validate_pack.py still scans all local files instead of Git-tracked files")

runtime_validator = ROOT / "scripts" / "validate_runtime_evals.py"
if runtime_validator.is_file():
    text = runtime_validator.read_text(encoding="utf-8")
    if "found {len(valid_skills)}" in text and "!= 17" in text:
        errors.append("validate_runtime_evals.py still hard-codes 17 skill IDs")
    if "VALIDATION_NUM_CTX = 8192" not in text and "ROUTING_VALIDATION_NUM_CTX = 8192" not in text:
        errors.append("validate_runtime_evals.py is missing the updated validation context")

print("Validated one-command local Runtime Eval tooling, review bundle contract, routing cases, and skill coverage")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
