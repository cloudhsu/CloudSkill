from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        fail(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}\n{result.stderr}")
    return result


candidate_template_path = ROOT / '.agents/skills/developing-skills/assets/INTERACTION_EVAL_CANDIDATE.template.json'
config_template_path = ROOT / 'config/cloudskill-config.template.json'
try:
    candidate_template = json.loads(candidate_template_path.read_text(encoding='utf-8'))
    config_template = json.loads(config_template_path.read_text(encoding='utf-8'))
except (OSError, json.JSONDecodeError) as exc:
    fail(f'invalid interaction capture template: {exc}')
    candidate_template = {}
    config_template = {}

for key, expected in {
    'default_sanitization': True,
    'save_raw_transcript': False,
    'auto_modify_skills': False,
    'auto_commit': False,
    'auto_push': False,
}.items():
    if config_template.get(key) is not expected:
        fail(f'config template safety mismatch: {key}')

skill_text = (ROOT / '.agents/skills/developing-skills/SKILL.md').read_text(encoding='utf-8')
for phrase in ('整理成正向案例', '整理成負向案例', 'manual-review', 'raw or complete transcript'):
    if phrase not in skill_text:
        fail(f'developing-skills is missing interaction capture rule: {phrase}')

ignore_text = (ROOT / '.gitignore').read_text(encoding='utf-8')
for pattern in ('.local/', '.cloudskill/config.local.json', '*.session.jsonl', '*.transcript.md'):
    if pattern not in ignore_text:
        fail(f'.gitignore missing private pattern: {pattern}')

ps_text = (ROOT / 'scripts/install.ps1').read_text(encoding='utf-8')
for marker in ('CloudSkillRepoPath', 'EvalInboxPath', 'SkipLocalConfig', 'ConfigOnly', 'config.local.json', 'sensitive-terms.local.txt'):
    if marker not in ps_text:
        fail(f'PowerShell installer missing local-config marker: {marker}')

with tempfile.TemporaryDirectory(prefix='cloudskill-interaction-') as tmp_name:
    tmp = Path(tmp_name)
    home = tmp / 'home'
    project = tmp / 'project'
    inbox = tmp / 'private-inbox'
    home.mkdir()
    project.mkdir()
    env = os.environ.copy()
    env['HOME'] = str(home)

    result = run([
        'bash', 'scripts/install.sh', '--tool', 'codex', '--scope', 'project',
        '--project-path', str(project), '--cloudskill-repo-path', str(ROOT),
        '--eval-inbox-path', str(inbox),
    ], cwd=ROOT, env=env)

    config_path = project / '.cloudskill/config.local.json'
    if not config_path.is_file():
        fail('project installer did not create config.local.json')
    if not (project / '.agents/skills/developing-skills/SKILL.md').is_file():
        fail('project installer did not copy developing-skills')
    for folder in ('candidates', 'manual-review', 'processed', 'rejected'):
        if not (inbox / folder).is_dir():
            fail(f'installer did not create Eval Inbox queue: {folder}')


    config_only_project = tmp / 'config-only-project'
    config_only_inbox = tmp / 'config-only-inbox'
    config_only_project.mkdir()
    run([
        'bash', 'scripts/install.sh', '--scope', 'project', '--project-path', str(config_only_project),
        '--cloudskill-repo-path', str(ROOT), '--eval-inbox-path', str(config_only_inbox), '--config-only',
    ], cwd=ROOT, env=env)
    if not (config_only_project / '.cloudskill/config.local.json').is_file():
        fail('config-only setup did not create project config')
    if (config_only_project / '.agents/skills').exists() or (config_only_project / '.claude/skills').exists():
        fail('config-only setup copied standalone skills')
    if (config_only_project / 'AGENTS.md').exists() or (config_only_project / 'CLAUDE.md').exists():
        fail('config-only setup wrote guidance files')

    if config_path.is_file():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        for key, expected in {
            'default_sanitization': True,
            'save_raw_transcript': False,
            'auto_modify_skills': False,
            'auto_commit': False,
            'auto_push': False,
        }.items():
            if config.get(key) is not expected:
                fail(f'installed config safety mismatch: {key}')

        draft = dict(candidate_template)
        draft['cloudskill_version'] = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        draft['task_summary'] = 'Readback state modeling'
        draft['prompt_sanitized'] = 'A device accepts a command but the hardware readback has not reached the requested value.'
        draft_path = tmp / 'positive.json'
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding='utf-8')
        run([
            sys.executable, 'scripts/capture_eval_candidate.py', '--kind', 'positive',
            '--input', str(draft_path), '--project-path', str(project),
        ], cwd=ROOT, env=env)
        if len(list((inbox / 'candidates').glob('*.json'))) != 1:
            fail('positive candidate was not saved to candidates queue')

        terms_path = Path(config['sensitive_terms_path'])
        terms_path.write_text('ExampleInternalName\n', encoding='utf-8')
        negative = dict(draft)
        negative['case_kind'] = 'negative'
        negative['task_summary'] = 'Failure with ExampleInternalName'
        negative['prompt_sanitized'] = 'ExampleInternalName command handling failed.'
        negative['failure_types'] = ['behavioral-omission']
        negative['user_correction_sanitized'] = 'Command acceptance is not physical completion.'
        negative['outcome'] = 'accepted-after-correction'
        negative_path = tmp / 'negative.json'
        negative_path.write_text(json.dumps(negative, ensure_ascii=False, indent=2), encoding='utf-8')
        run([
            sys.executable, 'scripts/capture_eval_candidate.py', '--kind', 'negative',
            '--input', str(negative_path), '--project-path', str(project),
        ], cwd=ROOT, env=env)
        if len(list((inbox / 'manual-review').glob('*.json'))) != 1:
            fail('sensitive-term candidate was not routed to manual-review')

        unsafe = dict(draft)
        unsafe['raw_transcript'] = 'must not be stored'
        unsafe_path = tmp / 'unsafe.json'
        unsafe_path.write_text(json.dumps(unsafe, ensure_ascii=False, indent=2), encoding='utf-8')
        result = subprocess.run([
            sys.executable, 'scripts/capture_eval_candidate.py', '--kind', 'positive',
            '--input', str(unsafe_path), '--project-path', str(project),
        ], cwd=ROOT, env=env, text=True, capture_output=True)
        if result.returncode == 0:
            fail('capture helper accepted a raw transcript field')

print('Validated full and config-only setup, private Inbox setup, positive capture, manual-review routing, and raw-transcript rejection')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
