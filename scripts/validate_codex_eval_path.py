from __future__ import annotations

import importlib.util
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
        '"--ask-for-approval"',
        '"never"',
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

runner = SCRIPTS / "run_runtime_evals.py"
if runner.is_file():
    text = runner.read_text(encoding="utf-8")
    for marker in (
        '"codex"',
        "--codex-model",
        "call_codex_cli",
        "MIN_FINAL_DELIVERABLE_CHARACTERS",
        "trailing.strip()",
    ):
        if marker not in text:
            errors.append(f"run_runtime_evals.py missing Codex/final marker: {marker}")

local_runner = SCRIPTS / "run_local_eval_review.py"
if local_runner.is_file():
    text = local_runner.read_text(encoding="utf-8")
    for marker in (
        'choices=("ollama", "codex")',
        "runtime_provider_args",
        'args.provider == "ollama" and not args.no_refine',
        "codex_preflight",
    ):
        if marker not in text:
            errors.append(f"run_local_eval_review.py missing Codex marker: {marker}")

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

try:
    from run_runtime_evals import extract_final_deliverable

    internal_mention = (
        "Planning text says begin with <final> and ending with </final>, "
        "then continues with internal analysis."
    )
    value, extracted = extract_final_deliverable(internal_mention)
    if extracted or value != internal_mention:
        errors.append("internal final-tag mention was incorrectly extracted")

    short = "<final>too short</final>"
    value, extracted = extract_final_deliverable(short)
    if extracted or value != short:
        errors.append("short final block was incorrectly accepted")

    candidate = "A" * 650
    raw = "Internal planning before the deliverable.\n<final>" + candidate + "</final>\n"
    value, extracted = extract_final_deliverable(raw)
    if not extracted or value != candidate:
        errors.append("substantive trailing final block was not extracted")

    trailing = "<final>" + candidate + "</final>\nadditional analysis"
    value, extracted = extract_final_deliverable(trailing)
    if extracted or value != trailing:
        errors.append("non-terminal final block was incorrectly accepted")
except Exception as exc:
    errors.append(f"failed synthetic final-extraction checks: {exc}")

try:
    from run_local_eval_review import extract_final, MIN_REFINED_CHARACTERS

    mention = "Editor says use <final> and then </final>, but keeps planning."
    if extract_final(mention) != mention:
        errors.append("refiner extracted a tag mention as the final answer")

    candidate = "B" * (MIN_REFINED_CHARACTERS + 50)
    raw = "planning\n<final>" + candidate + "</final>"
    if extract_final(raw) != candidate:
        errors.append("refiner did not extract a substantive terminal final block")
except Exception as exc:
    errors.append(f"failed synthetic refiner extraction checks: {exc}")

print(
    "Validated Codex CLI Runtime Eval path and strict terminal final-deliverable extraction"
)
print("NOTE: this validator does not call Codex, Ollama, OpenAI API, or another model.")
for error in errors:
    print(f"ERROR: {error}")
sys.exit(1 if errors else 0)
