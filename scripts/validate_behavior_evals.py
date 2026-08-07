from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'
CASES = ROOT / 'evals' / 'behavior' / 'cases'
errors = []
warnings = []
ids = set()
valid_types = {'recognition','application','counterexample','discipline','reference'}
skill_names = {p.parent.name for p in SKILLS.glob('*/SKILL.md')}
coverage = {name: set() for name in skill_names}
case_count = 0

required_fields = {
    'id','skill','type','prompt','expected_routing','required_behaviors',
    'forbidden_behaviors','required_artifacts','baseline_expected_failure','review_notes'
}

if not CASES.exists():
    errors.append(f'missing behavior cases directory: {CASES}')
else:
    for path in sorted(CASES.glob('*.json')):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            errors.append(f'{path}: invalid JSON: {exc}')
            continue
        file_skill = payload.get('skill')
        if file_skill not in skill_names:
            errors.append(f'{path}: unknown skill {file_skill!r}')
        for item in payload.get('cases', []):
            case_count += 1
            missing = required_fields - set(item)
            if missing:
                errors.append(f'{path}: case missing fields {sorted(missing)}')
                continue
            cid = item['id']
            if cid in ids:
                errors.append(f'duplicate behavior case ID: {cid}')
            ids.add(cid)
            skill = item['skill']
            typ = item['type']
            if skill != file_skill:
                errors.append(f'{cid}: case skill differs from file skill')
            if skill not in skill_names:
                errors.append(f'{cid}: unknown skill {skill!r}')
            if typ not in valid_types:
                errors.append(f'{cid}: invalid type {typ!r}')
            else:
                coverage.setdefault(skill, set()).add(typ)
            if not isinstance(item['expected_routing'], bool):
                errors.append(f'{cid}: expected_routing must be boolean')
            if typ == 'counterexample' and item['expected_routing']:
                errors.append(f'{cid}: counterexample must set expected_routing=false')
            if typ != 'counterexample' and not item['expected_routing']:
                errors.append(f'{cid}: positive case must set expected_routing=true')
            for field in ['required_behaviors','forbidden_behaviors','required_artifacts','baseline_expected_failure']:
                if not isinstance(item[field], list):
                    errors.append(f'{cid}: {field} must be an array')
            if not item['prompt'].strip():
                errors.append(f'{cid}: prompt is empty')
            if not item['baseline_expected_failure']:
                warnings.append(f'{cid}: no baseline failure recorded')

for skill in sorted(skill_names):
    missing = {'recognition','application','counterexample'} - coverage.get(skill, set())
    if missing:
        errors.append(f'{skill}: missing behavior case types {sorted(missing)}')

print(f'Validated {case_count} behavior case contracts for {len(skill_names)} skills')
print('NOTE: case validation is not a model behavior execution.')
for warning in warnings:
    print(f'WARNING: {warning}')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
