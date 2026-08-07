from pathlib import Path
import csv
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'
errors = []
warnings = []
manifest = []
names = set()

for folder in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
    skill_file = folder / 'SKILL.md'
    if not skill_file.exists():
        errors.append(f'{folder}: missing SKILL.md')
        continue

    text = skill_file.read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
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
    if name != folder.name:
        errors.append(f'{skill_file}: name {name!r} must equal folder {folder.name!r}')
    if name in names:
        errors.append(f'duplicate skill name: {name}')
    names.add(name)

    if len(description) > 360:
        warnings.append(f'{name}: long description ({len(description)} chars)')
    if not (folder / 'agents' / 'openai.yaml').exists():
        warnings.append(f'{name}: missing optional agents/openai.yaml')

    manifest.append({
        'name': name,
        'description': description,
        'path': str(skill_file.relative_to(ROOT)),
        'file_count': sum(1 for path in folder.rglob('*') if path.is_file()),
    })

required = [
    'AGENTS.md', 'CLAUDE.md', 'INSTALL.md', 'PLANS.md', 'README.md', 'CHANGELOG.md', 'VERSION',
    'docs/README.md', 'docs/profile/ARCHITECT_PROFILE.md',
    'docs/evidence/BENTO_SYSTEM.md', 'docs/evidence/CLOUDBOX_ENGINE.md',
    'docs/standards/ENGINEERING_GOVERNANCE.md', 'docs/DOCUMENTATION_AUDIT.md',
    'scripts/install.ps1', 'scripts/install.sh', 'scripts/audit_docs.py',
    'evals/skill-routing-cases.csv',
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f'missing required file: {rel}')

claude_text = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8') if (ROOT / 'CLAUDE.md').exists() else ''
if '@AGENTS.md' not in claude_text:
    errors.append('CLAUDE.md must import @AGENTS.md')

history = ROOT / 'history'
if history.exists():
    snapshots = [path.name for path in history.iterdir() if path.is_dir()]
    if snapshots:
        errors.append(f'full history snapshots are not allowed: {snapshots}')

version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
if version != '5.0.0':
    errors.append(f'expected VERSION 5.0.0, got {version}')

with (ROOT / 'evals' / 'skill-routing-cases.csv').open('r', encoding='utf-8-sig', newline='') as handle:
    rows = list(csv.DictReader(handle))
if not rows:
    errors.append('skill routing eval set is empty')

(ROOT / 'SKILL_MANIFEST.json').write_text(json.dumps({
    'version': version,
    'skills': manifest,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f'Validated {len(manifest)} skills and {len(rows)} routing cases')
for warning in warnings:
    print(f'WARNING: {warning}')
for error in errors:
    print(f'ERROR: {error}')

sys.exit(1 if errors else 0)
