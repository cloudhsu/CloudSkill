from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'
errors = []
warnings = []

workflow_markers = re.compile(r'\b(first|then|finally|step-by-step|workflow|by (?:creating|running|writing|dispatching))\b', re.I)

for skill_file in sorted(SKILLS.glob('*/SKILL.md')):
    text = skill_file.read_text(encoding='utf-8')
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n', text, re.S)
    if not match:
        continue
    front = match.group(1)
    name = re.search(r'^name:\s*(.+?)\s*$', front, re.M).group(1).strip()
    desc_match = re.search(r'^description:\s*(.+?)\s*$', front, re.M)
    if not desc_match:
        continue
    description = desc_match.group(1).strip()
    if not description.startswith('Use when '):
        errors.append(f'{name}: description must begin with "Use when "')
    if len(description) > 500:
        errors.append(f'{name}: description exceeds 500 characters')
    if workflow_markers.search(description):
        warnings.append(f'{name}: description may summarize workflow rather than triggers')
    if description.count('.') > 2:
        warnings.append(f'{name}: description may be too broad; prefer one trigger-focused sentence')

print(f'Validated descriptions for {len(list(SKILLS.glob("*/SKILL.md")))} skills')
for warning in warnings:
    print(f'WARNING: {warning}')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
