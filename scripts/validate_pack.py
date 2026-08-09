from pathlib import Path
import argparse
import csv
import json
import re
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'
errors = []
warnings = []
manifest = []
names = set()

parser = argparse.ArgumentParser()
parser.add_argument('--check-manifest', action='store_true', help='Fail rather than rewrite when SKILL_MANIFEST.json differs.')
args = parser.parse_args()

if not SKILLS.exists():
    errors.append(f'missing skills directory: {SKILLS}')
else:
    for folder in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        skill_file = folder / 'SKILL.md'
        if not skill_file.exists():
            errors.append(f'{folder}: missing SKILL.md')
            continue

        text = skill_file.read_text(encoding='utf-8')
        match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n', text, re.S)
        if not match:
            errors.append(f'{skill_file}: invalid YAML frontmatter')
            continue

        front = match.group(1)
        name_match = re.search(r'^name:\s*(.+?)\s*$', front, re.M)
        desc_match = re.search(r'^description:\s*(.+?)\s*$', front, re.M)
        if not name_match or not desc_match:
            errors.append(f'{skill_file}: name and description required')
            continue

        name = name_match.group(1).strip()
        description = desc_match.group(1).strip()
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            errors.append(f'{skill_file}: invalid skill name {name!r}')
        if name != folder.name:
            errors.append(f'{skill_file}: name {name!r} must equal folder {folder.name!r}')
        if name in names:
            errors.append(f'duplicate skill name: {name}')
        names.add(name)

        if len(front) > 1024:
            errors.append(f'{name}: frontmatter exceeds 1024 characters')
        if len(description) > 500:
            warnings.append(f'{name}: long description ({len(description)} chars)')
        if not (folder / 'agents' / 'openai.yaml').exists():
            warnings.append(f'{name}: missing optional agents/openai.yaml')

        manifest.append({
            'name': name,
            'description': description,
            'path': str(skill_file.relative_to(ROOT)).replace('\\','/'),
            'file_count': sum(1 for path in folder.rglob('*') if path.is_file()),
        })

required = [
    'AGENTS.md', 'CLAUDE.md', 'INSTALL.md', 'PLANS.md', 'README.md', 'CHANGELOG.md', 'VERSION',
    'docs/README.md', 'docs/profile/ARCHITECT_PROFILE.md',
    'docs/evidence/BENTO_SYSTEM.md', 'docs/evidence/CLOUDBOX_ENGINE.md',
    'docs/evidence/QT_COMPONENT_SUITE.md', 'docs/evidence/SIS_TOUCH_UTILITY.md',
    'docs/evidence/EQUIPMENT_CONTROL_PLATFORM.md', 'docs/evidence/SEMICONDUCTOR_EQUIPMENT_TRAINING.md',
    'docs/standards/ENGINEERING_GOVERNANCE.md', 'docs/DOCUMENTATION_AUDIT.md',
    'scripts/install.ps1', 'scripts/install.sh', 'scripts/audit_docs.py',
    'scripts/validate_descriptions.py', 'scripts/validate_behavior_evals.py',
    'scripts/manage_skill.py', 'scripts/validate_skill_lifecycle.py',
    'scripts/smoke_install.py', 'scripts/run_all_checks.py', 'scripts/validate_plugins.py',
    'cloudskill-eval', 'cloudskill-eval-codex', 'scripts/codex_eval_adapter.py', 'scripts/run_local_eval_review.py', 'scripts/validate_local_eval_debugging.py', 'scripts/validate_codex_eval_path.py',
    '.codex-plugin/plugin.json', '.claude-plugin/plugin.json',
    '.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json',
    'assets/cloudbox.ico', 'assets/cloudbox-icon.png', 'assets/cloudbox-logo.png',
    'docs/CLOUDBOX_PLUGIN.md',
    'scripts/capture_eval_candidate.py', 'scripts/validate_interaction_capture.py',
    'config/cloudskill-config.template.json', '.gitignore',
    'evals/README.md', 'evals/skill-routing-cases.csv', 'evals/behavior/README.md',
    'evals/behavior/schema.json', 'evals/behavior/RESULT.template.json',
    '.agents/skills/using-cloudskill/SKILL.md',
    '.agents/skills/developing-skills/SKILL.md',
    '.agents/skills/developing-skills/references/interaction-eval-capture.md',
    '.agents/skills/developing-skills/assets/INTERACTION_EVAL_CANDIDATE.template.json',
    '.agents/skills/developing-skills/assets/EVAL_MINING_REPORT.template.md',
    '.agents/skills/developing-skills/references/skill-lifecycle-standard.md',
    '.agents/skills/developing-skills/assets/SKILL_PROPOSAL.template.md',
    '.agents/skills/developing-skills/assets/SKILL_LIFECYCLE.template.json',
    '.agents/skills/developing-skills/assets/SKILL_RELEASE_EVIDENCE.template.md',
    'config/skill-lifecycle-policy.json',
    '.agents/skills/local-runtime-eval-debugging/references/codex-runtime-eval.md',
    '.agents/skills/runtime-evaluation-engineering/SKILL.md',
    '.agents/skills/runtime-evaluation-engineering/agents/openai.yaml',
    '.agents/skills/runtime-evaluation-engineering/references/evaluation-failure-taxonomy.md',
    '.agents/skills/runtime-evaluation-engineering/references/case-and-grader-design.md',
    '.agents/skills/runtime-evaluation-engineering/assets/EVAL_SYSTEM_REVIEW.template.md',
    '.agents/skills/equipment-control-architecture/SKILL.md',
    '.agents/skills/equipment-domain-modeling/SKILL.md',
    '.agents/skills/semiconductor-equipment-domain-knowledge/SKILL.md',
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f'missing required file: {rel}')


tracked_files = []
try:
    tracked_result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    tracked_files = [ROOT / item.decode("utf-8") for item in tracked_result.stdout.split(b"\0") if item]
except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
    errors.append(f"failed to inspect Git-tracked files: {exc}")

private_tracked = [
    path for path in tracked_files
    if '.local' in path.relative_to(ROOT).parts
    or path.name == 'config.local.json'
    or path.suffix == '.jsonl'
    or path.name.endswith('.transcript.md')
]
if private_tracked:
    errors.append('private local interaction data must not be tracked: ' + ', '.join(str(path.relative_to(ROOT)) for path in private_tracked))

claude_text = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8') if (ROOT / 'CLAUDE.md').exists() else ''
if '@AGENTS.md' not in claude_text:
    errors.append('CLAUDE.md must import @AGENTS.md')

history = ROOT / 'history'
if history.exists():
    snapshots = [path.name for path in history.iterdir() if path.is_dir()]
    if snapshots:
        errors.append(f'full history snapshots are not allowed: {snapshots}')

version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip() if (ROOT / 'VERSION').exists() else ''
if not re.fullmatch(r'\d+\.\d+\.\d+', version):
    errors.append(f'invalid semantic VERSION: {version!r}')

readme = (ROOT / 'README.md').read_text(encoding='utf-8') if (ROOT / 'README.md').exists() else ''
if version and f'**Current version: {version}**' not in readme:
    errors.append('README current version does not match VERSION')

changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8') if (ROOT / 'CHANGELOG.md').exists() else ''
first_release = re.search(r'^##\s+(\d+\.\d+\.\d+)\s*$', changelog, re.M)
if version and (not first_release or first_release.group(1) != version):
    errors.append('first CHANGELOG release does not match VERSION')

routing_path = ROOT / 'evals' / 'skill-routing-cases.csv'
if routing_path.exists():
    with routing_path.open('r', encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        errors.append('skill routing eval set is empty')
    routing_ids = [row.get('id','') for row in rows]
    if len(routing_ids) != len(set(routing_ids)):
        errors.append('duplicate routing eval IDs')
else:
    rows = []

expected = {'version': version, 'skills': manifest}
manifest_path = ROOT / 'SKILL_MANIFEST.json'
current = None
if manifest_path.exists():
    try:
        current = json.loads(manifest_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        errors.append(f'invalid SKILL_MANIFEST.json: {exc}')

if current != expected:
    if args.check_manifest:
        errors.append('SKILL_MANIFEST.json is stale; run python scripts/validate_pack.py')
    else:
        manifest_path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Updated SKILL_MANIFEST.json')

print(f'Validated {len(manifest)} skills and {len(rows)} routing cases for version {version or "UNKNOWN"}')
for warning in warnings:
    print(f'WARNING: {warning}')
for error in errors:
    print(f'ERROR: {error}')

sys.exit(1 if errors else 0)
