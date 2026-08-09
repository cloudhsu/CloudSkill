from __future__ import annotations

import importlib.util
import json
import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
errors: list[str] = []

required = [
    ROOT / "cloudskill-eval-codex",
    ROOT / "cloudskill-resume",
    SCRIPTS / "codex_eval_adapter.py",
    SCRIPTS / "run_runtime_evals.py",
    SCRIPTS / "run_local_eval_review.py",
    SCRIPTS / "validate_behavior_contract.py",
    ROOT
    / ".agents"
    / "skills"
    / "local-runtime-eval-debugging"
    / "references"
    / "codex-runtime-eval.md",
]
for path in required:
    if not path.is_file():
        errors.append(f"missing Codex Eval path file: {path.relative_to(ROOT)}")

launcher = ROOT / "cloudskill-eval-codex"
if launcher.is_file():
    if not (launcher.stat().st_mode & stat.S_IXUSR):
        errors.append("cloudskill-eval-codex is not executable")
    text = launcher.read_text(encoding="utf-8")
    for marker in (
        "--provider codex",
        "--repeat 1",
        "--no-refine",
        "codex login",
    ):
        if marker not in text:
            errors.append(f"cloudskill-eval-codex missing marker: {marker}")


resume = ROOT / "cloudskill-resume"
if resume.is_file():
    text = resume.read_text(encoding="utf-8")
    for marker in (
        "--provider NAME",
        'EVAL_PROVIDER="ollama"',
        'EVAL_PROVIDER="codex"',
        'zip_matches_current_sources "$REVIEW_ZIP" "$EVAL_PROVIDER"',
        './cloudskill-eval-codex',
    ):
        if marker not in text:
            errors.append(f"cloudskill-resume missing provider marker: {marker}")

adapter = SCRIPTS / "codex_eval_adapter.py"
if adapter.is_file():
    text = adapter.read_text(encoding="utf-8")
    for marker in (
        "codex login",
        '"exec"',
        '"--ephemeral"',
        '"--sandbox"',
        '"read-only"',
        '"--ignore-user-config"',
        '"--ignore-rules"',
        '"--json"',
        '"--output-last-message"',
        '"--output-schema"',
        "TemporaryDirectory",
        'git", "init"',
    ):
        if marker not in text:
            errors.append(f"codex_eval_adapter.py missing marker: {marker}")
    if "auth.json" in text:
        errors.append("codex_eval_adapter.py must not read or package auth.json")
    if "--ask-for-approval" in text:
        errors.append(
            "codex_eval_adapter.py: --ask-for-approval was removed from codex-cli "
            "0.147.0 (confirmed against a live process: 'unexpected argument "
            "--ask-for-approval found'); do not reintroduce it"
        )

runner = SCRIPTS / "run_runtime_evals.py"
if runner.is_file():
    text = runner.read_text(encoding="utf-8")
    for marker in (
        '"codex"',
        "--codex-model",
        "call_codex_cli",
        "BEHAVIOR_OUTPUT_CONTRACT_ID",
        "BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT",
    ):
        if marker not in text:
            errors.append(f"run_runtime_evals.py missing Codex/final marker: {marker}")

local_runner = SCRIPTS / "run_local_eval_review.py"
if local_runner.is_file():
    text = local_runner.read_text(encoding="utf-8")
    for marker in (
        "from providers_contract import",
        "PROVIDER_IDS",
        "runtime_provider_args",
        "refinement_default(args.provider)",
        "codex_preflight",
    ):
        if marker not in text:
            errors.append(f"run_local_eval_review.py missing Codex marker: {marker}")
    if 'choices=("ollama", "codex")' in text:
        errors.append(
            "run_local_eval_review.py: --provider choices must come from the shared "
            "providers_contract registry, not a hand-copied tuple"
        )

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:
    from behavior_output_contract import (
        BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT,
        BEHAVIOR_OUTPUT_CONTRACT_ID,
    )
except Exception as exc:
    errors.append(f"cannot load shared Behavior output contract: {exc}")
else:
    if not BEHAVIOR_OUTPUT_CONTRACT_ID or len(BEHAVIOR_OUTPUT_CONTRACT_FINGERPRINT) != 64:
        errors.append("shared Behavior output contract identity is invalid")

print(
    "Validated Codex CLI Runtime Eval path; Behavior output-contract consistency is delegated to validate_behavior_contract.py"
)
print("NOTE: this validator does not call Codex, Ollama, OpenAI API, or another model.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
