"""Structurally validate every evals/behavior/cases/*.json file: required
fields present, IDs globally unique, valid `type`, expected_routing
consistent with type, and every Skill covering recognition/application/
counterexample at minimum.

2026-08-24 note, added after a real mix-up in this repository's own
session -- these ~320 cases across 41 Skills are a *documented behavior
contract* layer only. Passing this validator proves the case is
well-formed and non-duplicate-ID, NOT that any model has ever been run
against it. This is a structurally separate, much larger corpus from
evals/runtime/cases/behavior-rubrics.json's small set of live-model-
gradable rubric cases (7, as of this note) that scripts/run_runtime_evals.py
and scripts/run_local_eval_review.py actually execute -- adding a case
here does NOT make it runnable via `--case-id` on those scripts; see
their own module docstrings. Confirmed by direct count: `python3
scripts/prioritize_eval_inbox.py`-adjacent tooling and a manual count on
2026-08-24 found only 7/320 cases have ever had a live execution path.
Do not assume "this validator passed" means "this behavior was verified
against a model" when reporting status to a user -- state NOT RUN
explicitly for any case without a corresponding behavior-rubrics.json
entry and executed=true evidence.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'
CASES = ROOT / 'evals' / 'behavior' / 'cases'
errors = []
warnings = []
ids = set()
suites = set()
items_by_id = {}
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
        suite = payload.get('suite')
        if not isinstance(suite, str) or not suite.strip():
            errors.append(f'{path}: missing nonblank suite')
        elif suite in suites:
            errors.append(f'{path}: duplicate behavior suite {suite!r}')
        else:
            suites.add(suite)
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
            items_by_id[cid] = item
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

# ENG-BEH-004 belongs to a non-core Skill;
# a filtered public checkout correctly omits it along with the rest of that
# skill's case file -- do not require it there.
_elicitation_contract_ids = {'AR-BEH-004', 'AR-BEH-005', 'AR-BEH-006'}
if 'cross-platform-engine-architecture' in skill_names:
    _elicitation_contract_ids.add('ENG-BEH-004')
for cid in _elicitation_contract_ids:
    item = items_by_id.get(cid)
    if not item:
        errors.append(f'missing architecture elicitation behavior contract: {cid}')
        continue
    joined = ' '.join(item['required_behaviors'] + item['forbidden_behaviors']).lower()
    if cid in {'AR-BEH-004', 'ENG-BEH-004'}:
        for phrase in ('exactly one', 'mutually exclusive', 'recommended'):
            if phrase not in joined:
                errors.append(f'{cid}: elicitation contract missing {phrase!r}')
    elif 'without' not in joined and 'directly' not in joined:
        errors.append(f'{cid}: no-question control is not explicit')

elicitation_reference = SKILLS / 'architecture-review' / 'references' / 'architecture-decision-elicitation.md'
if not elicitation_reference.is_file():
    errors.append('missing authoritative architecture decision elicitation reference')
else:
    elicitation_text = elicitation_reference.read_text(encoding='utf-8').lower()
    for phrase in ('exactly one', 'mutually exclusive', 'recommended option first', 'do not ask'):
        if phrase not in elicitation_text:
            errors.append(f'architecture elicitation reference missing rule: {phrase}')
    for consumer in (
        'architecture-review', 'application-client-server-architecture',
        'cross-platform-engine-architecture', 'cross-platform-native-architecture',
        'equipment-control-architecture', 'framework-design',
    ):
        consumer_path = SKILLS / consumer / 'SKILL.md'
        if not consumer_path.is_file():
            # A filtered public checkout (scripts/export_public_bundle.py)
            # can legitimately omit a private-tier consumer (e.g.
            # cross-platform-engine-architecture, non-core) -- skip
            # rather than fail. A genuinely missing skill folder in the
            # canonical private repo is caught elsewhere (validate_pack.py).
            continue
        consumer_text = consumer_path.read_text(encoding='utf-8')
        if 'architecture-decision-elicitation.md' not in consumer_text:
            errors.append(f'{consumer}: missing architecture elicitation reference link')

print(f'Validated {case_count} behavior case contracts for {len(skill_names)} skills')
print('NOTE: case validation is not a model behavior execution.')
for warning in warnings:
    print(f'WARNING: {warning}')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
