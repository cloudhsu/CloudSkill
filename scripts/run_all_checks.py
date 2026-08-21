from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
commands = [
    [sys.executable, 'scripts/validate_pack.py'],
    [sys.executable, 'scripts/audit_docs.py'],
    [sys.executable, 'scripts/validate_descriptions.py'],
    [sys.executable, 'scripts/validate_behavior_evals.py'],
    [sys.executable, 'scripts/validate_skill_lifecycle.py'],
    [sys.executable, 'scripts/validate_skill_context_budget.py'],
    [sys.executable, 'scripts/validate_planning_priority.py'],
    [sys.executable, 'scripts/validate_interaction_capture.py'],
    [sys.executable, 'scripts/validate_eval_bundle_contract.py'],
    [sys.executable, 'scripts/sync_gemini_plugins.py', '--check'],
    [sys.executable, 'scripts/validate_plugins.py'],
    [sys.executable, 'scripts/smoke_install.py'],
    [sys.executable, 'scripts/validate_runtime_evals.py'],
    [sys.executable, 'scripts/validate_local_eval_debugging.py'],
    [sys.executable, 'scripts/validate_codex_eval_path.py'],
    [sys.executable, 'scripts/validate_providers_contract.py'],
    [sys.executable, 'scripts/validate_skill_portability.py'],
    [sys.executable, 'scripts/validate_behavior_contract.py'],
    [sys.executable, 'scripts/validate_evolution_handoff.py'],
    [sys.executable, 'scripts/validate_behavior_runtime_evals.py'],
    [sys.executable, 'scripts/validate_task_continuity_evals.py'],
    [sys.executable, 'scripts/validate_task_continuity_runner.py'],
    [sys.executable, 'scripts/validate_multimodel_panel.py'],
    [sys.executable, 'scripts/validate_benchmark_report.py'],
    [sys.executable, 'scripts/validate_review_assurance.py'],
    [sys.executable, 'scripts/validate_lifecycle_orchestration.py'],
    [sys.executable, 'scripts/validate_lifecycle_templates.py'],
]

for command in commands:
    script_path = ROOT / command[1]
    if not script_path.exists():
        # A filtered public checkout (scripts/export_public_bundle.py) can
        # legitimately omit a private-only validator. Skip rather than fail
        # so this same command list works unmodified in both checkouts.
        print(f"NOTE: skipping {command[1]} (not present in this checkout)", flush=True)
        continue
    print('+', ' '.join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        raise SystemExit(result.returncode)

print('All CloudSkill checks passed.')
