from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import zipfile

# Loading capture_eval_candidate.py/export_eval_candidate.py below via
# importlib would otherwise write __pycache__ bytecode cache under
# .agents/skills/developing-skills/assets/, which validate_pack.py's naive
# per-skill file_count then picks up on the *next* run (a real drift this
# validator caught: SKILL_MANIFEST.json oscillated between file_count 16/17
# depending on run order). Disable bytecode writes for this process only.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
for phrase in (
    '整理成正向案例', '整理成負向案例', '從專案提煉優化案例',
    'manual-review', 'raw or complete transcript',
):
    if phrase not in skill_text:
        fail(f'developing-skills is missing interaction capture rule: {phrase}')

mining_reference_path = ROOT / '.agents/skills/developing-skills/references/conversation-derived-optimization.md'
mining_reference_text = mining_reference_path.read_text(encoding='utf-8') if mining_reference_path.is_file() else ''
if not mining_reference_text:
    fail(f'missing conversation-derived-optimization reference: {mining_reference_path.relative_to(ROOT)}')
for phrase in (
    'Project-history mining', 'inferred', 'Auto-bounded scope',
    'skill-authoring-sources.md',
):
    if phrase not in mining_reference_text:
        fail(f'conversation-derived-optimization.md is missing project-history mining rule: {phrase}')

agents_text = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
for phrase in ('從專案提煉優化案例', 'Project-history-derived Eval capture'):
    if phrase not in agents_text:
        fail(f'AGENTS.md is missing project-history capture rule: {phrase}')

install_text = (ROOT / 'INSTALL.md').read_text(encoding='utf-8')
if '從專案提煉優化案例' not in install_text:
    fail('INSTALL.md is missing the project-history mining trigger phrase')

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

export_script_path = ROOT / '.agents/skills/developing-skills/assets/export_eval_candidate.py'
import_script_path = ROOT / 'scripts/import_eval_candidates.py'
if not export_script_path.is_file():
    fail('missing portable export asset: .agents/skills/developing-skills/assets/export_eval_candidate.py')
if not import_script_path.is_file():
    fail('missing Eval Inbox import tool: scripts/import_eval_candidates.py')

if import_script_path.is_file():
    import_module = load_module('cloudskill_import_eval_candidates', import_script_path)
    with tempfile.TemporaryDirectory(prefix='cloudskill-explicit-inbox-policy-') as tmp_name:
        tmp = Path(tmp_name)
        owned_inbox = (tmp / 'owned-inbox').resolve()
        terms_path = tmp / 'private-terms.txt'
        terms_path.write_text('private-marker\n', encoding='utf-8')
        config_path = tmp / 'config.json'
        config_path.write_text(json.dumps({
            'schema_version': '1.0', 'cloudskill_version': '6.3.0',
            'cloudskill_repository': str(ROOT), 'eval_inbox': str(owned_inbox),
            'sensitive_terms_path': str(terms_path), 'default_sanitization': True,
            'save_raw_transcript': False, 'auto_modify_skills': False,
            'auto_commit': False, 'auto_push': False,
        }), encoding='utf-8')
        resolved_inbox, resolved_terms = import_module.resolve_inbox(SimpleNamespace(
            eval_inbox=str(owned_inbox), config=str(config_path), dry_run=False,
        ))
        if resolved_inbox != owned_inbox or resolved_terms != ['private-marker']:
            fail('explicit Eval Inbox did not preserve its owning config private-term policy')

if export_script_path.is_file():
    capture_module = load_module('cloudskill_capture_eval_candidate', ROOT / 'scripts/capture_eval_candidate.py')
    export_module = load_module('cloudskill_export_eval_candidate', export_script_path)
    if capture_module.ALLOWED_KINDS != export_module.ALLOWED_KINDS:
        fail('export_eval_candidate.py ALLOWED_KINDS has drifted from capture_eval_candidate.py')
    if capture_module.PROHIBITED_KEYS != export_module.PROHIBITED_KEYS:
        fail('export_eval_candidate.py PROHIBITED_KEYS has drifted from capture_eval_candidate.py')
    capture_patterns = {key: pattern.pattern for key, pattern in capture_module.SENSITIVE_PATTERNS.items()}
    export_patterns = {key: pattern.pattern for key, pattern in export_module.SENSITIVE_PATTERNS.items()}
    if capture_patterns != export_patterns:
        fail('export_eval_candidate.py SENSITIVE_PATTERNS has drifted from capture_eval_candidate.py')

    # Export-then-import round trip, simulating a fully disconnected session: no
    # .cloudskill config anywhere, an external "eval-outbox" project, a manual zip
    # transfer, and an import into a private repository-side Eval Inbox.
    with tempfile.TemporaryDirectory(prefix='cloudskill-export-import-') as tmp_name:
        tmp = Path(tmp_name)
        external_project = tmp / 'external-project'
        repo_inbox = tmp / 'imported-inbox'
        external_project.mkdir()

        draft = dict(candidate_template)
        draft['cloudskill_version'] = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        draft['task_summary'] = 'Disconnected-session export smoke test'
        draft['prompt_sanitized'] = 'A device accepts a command but the hardware readback has not reached the requested value.'
        draft_path = tmp / 'export-positive.json'
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding='utf-8')
        stale = external_project / '.cloudskill/eval-outbox/manual-review/INT-stale-negative.json'
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text('{}\n', encoding='utf-8')

        export_result = run([
            sys.executable, str(export_script_path), '--kind', 'positive',
            '--input', str(draft_path), '--outbox', str(external_project / '.cloudskill/eval-outbox'),
            '--project-name', 'validator-smoke', '--non-interactive',
        ], cwd=external_project)
        export_config = json.loads((external_project / '.cloudskill/config.local.json').read_text(encoding='utf-8'))
        if export_config.get('export_project_name') != 'validator-smoke' or export_config.get('export_agent_name') != 'codex':
            fail('portable exporter did not persist project and agent aliases')
        exported_zips = list(external_project.glob('validator-smoke-codex-codex-*.zip'))
        if len(exported_zips) != 1:
            fail('export_eval_candidate.py did not produce exactly one zip archive')
        elif not zipfile.is_zipfile(exported_zips[0]):
            fail('export_eval_candidate.py produced an invalid zip archive')
        if 'MANUAL_REQUIRED' not in export_result.stdout:
            fail('export without a reachable sensitive-terms file did not conservatively route to manual-review')
        if exported_zips:
            with zipfile.ZipFile(exported_zips[0]) as archive:
                manifest = json.loads(archive.read('manifest.json'))
            if manifest.get('bundle_format_version') != '2.0':
                fail('export bundle is missing format version 2.0')
            if manifest.get('export_project_name') != 'validator-smoke':
                fail('export bundle did not preserve configured project name')
            if len(manifest.get('payload_hashes', {})) != 1 or 'INT-stale-negative.json' in manifest.get('payload_hashes', {}):
                fail('single-candidate export included stale outbox candidates')

        if exported_zips:
            (repo_inbox / 'imports').mkdir(parents=True, exist_ok=True)
            shutil.copy2(exported_zips[0], repo_inbox / 'imports' / exported_zips[0].name)

            run([
                sys.executable, str(import_script_path), '--eval-inbox', str(repo_inbox),
            ], cwd=ROOT)
            if len(list((repo_inbox / 'manual-review').glob('*.json'))) != 1:
                fail('import_eval_candidates.py did not file the exported candidate into manual-review/')
            if list((repo_inbox / 'imports').glob('*.zip')):
                fail('import_eval_candidates.py left the processed zip in imports/ instead of imports/processed/')
            if len(list((repo_inbox / 'imports/processed').glob('*.zip'))) != 1:
                fail('import_eval_candidates.py did not move the processed zip into imports/processed/')

            renamed = repo_inbox / 'imports' / 'renamed.zip'
            shutil.copy2(exported_zips[0], renamed)
            renamed_result = run([
                sys.executable, str(import_script_path), '--eval-inbox', str(repo_inbox),
            ], cwd=ROOT)
            if 'unsupported=1' not in renamed_result.stdout or not (repo_inbox / 'imports/unsupported/renamed.zip').is_file():
                fail('manifest-valid archive with a mismatched filename was not routed to unsupported/')

            # Re-running import on an inbox with no new zips must be a no-op, not an error.
            rerun = run([
                sys.executable, str(import_script_path), '--eval-inbox', str(repo_inbox),
            ], cwd=ROOT)
            if 'No import archives found' not in rerun.stdout:
                fail('re-running import_eval_candidates.py with nothing new to import did not report a no-op')

            # One real mixed batch proves that shared seen_keys, totals, and
            # archive disposition work together rather than only in isolated runs.
            batch_inbox = tmp / 'batch-inbox'
            batch_imports = batch_inbox / 'imports'
            batch_imports.mkdir(parents=True)
            shutil.copy2(exported_zips[0], batch_imports / exported_zips[0].name)
            with zipfile.ZipFile(exported_zips[0]) as source:
                members = {name: source.read(name) for name in source.namelist()}
            duplicate_manifest = json.loads(members['manifest.json'])
            duplicate_manifest['bundle_id'] = 'd' * 32
            duplicate_name = (
                f"{duplicate_manifest['export_project_name']}-{duplicate_manifest['host']}-"
                f"{duplicate_manifest['agent_name']}-{duplicate_manifest['created_at_utc']}-dddddddd.zip"
            )
            with zipfile.ZipFile(batch_imports / duplicate_name, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json', json.dumps(duplicate_manifest, ensure_ascii=False, indent=2) + '\n')
                for name, payload in members.items():
                    if name != 'manifest.json':
                        archive.writestr(name, payload)
            shutil.copy2(exported_zips[0], batch_imports / 'wrong-name.zip')
            (batch_imports / 'malformed.zip').write_bytes(b'not a zip')

            batch = run([
                sys.executable, str(import_script_path), '--eval-inbox', str(batch_inbox),
            ], cwd=ROOT)
            expected_totals = ('TOTAL: 4 archive(s)', 'manual_review=1', 'duplicate=1', 'skipped=1', 'unsupported=1')
            if any(value not in batch.stdout for value in expected_totals):
                fail('mixed multi-zip batch totals did not preserve valid, duplicate, malformed, and unsupported outcomes')
            if len(list((batch_inbox / 'imports/processed').glob('*.zip'))) != 2:
                fail('mixed batch did not process both supported archives')
            if not (batch_inbox / 'imports/unsupported/wrong-name.zip').is_file():
                fail('mixed batch did not retain the filename-mismatched archive as unsupported')
            if not (batch_imports / 'malformed.zip').is_file():
                fail('mixed batch did not retain the malformed archive for manual review')
            if len(list((batch_inbox / 'manual-review').glob('*.json'))) != 1:
                fail('mixed batch partially imported unsupported/malformed content or failed to deduplicate')
            # Reusing archive names must preserve both old and new audit inputs.
            shutil.copy2(exported_zips[0], batch_imports / exported_zips[0].name)
            shutil.copy2(exported_zips[0], batch_imports / 'wrong-name.zip')
            run([sys.executable, str(import_script_path), '--eval-inbox', str(batch_inbox)], cwd=ROOT)
            if len(list((batch_inbox / 'imports/processed').glob('validator-smoke-*.zip'))) != 3:
                fail('same-name processed archive overwrote retained evidence')
            if len(list((batch_inbox / 'imports/unsupported').glob('wrong-name*.zip'))) != 2:
                fail('same-name unsupported archive overwrote retained evidence')

            bomb_inbox = tmp / 'bomb-inbox'
            bomb_imports = bomb_inbox / 'imports'
            bomb_imports.mkdir(parents=True)
            bomb_path = bomb_imports / 'oversized.zip'
            with zipfile.ZipFile(bomb_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json', '{}')
                archive.writestr('payload.bin', b'0' * (4 * 1024 * 1024 + 1))
            bomb = run([sys.executable, str(import_script_path), '--eval-inbox', str(bomb_inbox)], cwd=ROOT)
            if 'skipped=1' not in bomb.stdout or not bomb_path.is_file():
                fail('resource-limit archive was not retained for manual review')
            if list((bomb_inbox / 'manual-review').glob('*.json')):
                fail('resource-limit archive produced partial candidate output')

            partial_inbox = tmp / 'partial-inbox'
            partial_imports = partial_inbox / 'imports'
            partial_imports.mkdir(parents=True)
            valid_payload_name = next(name for name in members if name != 'manifest.json')
            valid_payload = members[valid_payload_name]
            malformed_payload = b'{not-json'
            partial_manifest = dict(duplicate_manifest)
            partial_manifest['bundle_id'] = 'e' * 32
            partial_manifest['payload_hashes'] = {
                valid_payload_name: hashlib.sha256(valid_payload).hexdigest(),
                'manual-review/zz-malformed.json': hashlib.sha256(malformed_payload).hexdigest(),
            }
            partial_name = (
                f"{partial_manifest['export_project_name']}-{partial_manifest['host']}-"
                f"{partial_manifest['agent_name']}-{partial_manifest['created_at_utc']}-eeeeeeee.zip"
            )
            with zipfile.ZipFile(partial_imports / partial_name, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json', json.dumps(partial_manifest))
                archive.writestr(valid_payload_name, valid_payload)
                archive.writestr('manual-review/zz-malformed.json', malformed_payload)
            partial = run([sys.executable, str(import_script_path), '--eval-inbox', str(partial_inbox)], cwd=ROOT)
            if 'skipped=1' not in partial.stdout or list((partial_inbox / 'manual-review').glob('*.json')):
                fail('manifest-valid archive published a partial candidate before later payload failure')

            unsafe_id_inbox = tmp / 'unsafe-id-inbox'
            unsafe_id_imports = unsafe_id_inbox / 'imports'
            unsafe_id_imports.mkdir(parents=True)
            base_candidate = json.loads(valid_payload)
            absolute_target = tmp / 'absolute-owned'
            unsafe_candidates = []
            for candidate_id in (str(absolute_target), '../../traversal-owned'):
                value = dict(base_candidate)
                value['candidate_id'] = candidate_id
                unsafe_candidates.append(value)
            rejected_value = dict(base_candidate)
            rejected_value['candidate_id'] = '../../rejected-owned'
            rejected_value['case_kind'] = '../../unsafe-kind'
            unsafe_candidates.append(rejected_value)
            unsafe_candidates.append(dict(rejected_value))
            unsafe_payloads = {
                f'manual-review/unsafe-{index}.json': json.dumps(value).encode('utf-8')
                for index, value in enumerate(unsafe_candidates)
            }
            unsafe_manifest = dict(duplicate_manifest)
            unsafe_manifest['bundle_id'] = 'f' * 32
            unsafe_manifest['payload_hashes'] = {
                name: hashlib.sha256(payload).hexdigest() for name, payload in unsafe_payloads.items()
            }
            unsafe_name = (
                f"{unsafe_manifest['export_project_name']}-{unsafe_manifest['host']}-"
                f"{unsafe_manifest['agent_name']}-{unsafe_manifest['created_at_utc']}-ffffffff.zip"
            )
            with zipfile.ZipFile(unsafe_id_imports / unsafe_name, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('manifest.json', json.dumps(unsafe_manifest))
                for name, payload in unsafe_payloads.items():
                    archive.writestr(name, payload)
            run([sys.executable, str(import_script_path), '--eval-inbox', str(unsafe_id_inbox)], cwd=ROOT)
            if Path(str(absolute_target) + '-positive.json').exists() or (tmp / 'traversal-owned-positive.json').exists() or (tmp / 'rejected-owned-candidate.json').exists():
                fail('imported candidate fields escaped the selected Inbox queue')
            published = list((unsafe_id_inbox / 'manual-review').glob('*.json')) + list((unsafe_id_inbox / 'rejected').glob('*.json'))
            if not published or any(path.resolve().parent not in {(unsafe_id_inbox / 'manual-review').resolve(), (unsafe_id_inbox / 'rejected').resolve()} for path in published):
                fail('unsafe candidate identifiers were not published under safe local queue names')
            if len(list((unsafe_id_inbox / 'rejected').glob('*.json'))) != 2:
                fail('identical rejected candidates did not retain collision-safe outputs')

            symlink_inbox = tmp / 'symlink-inbox'
            symlink_imports = symlink_inbox / 'imports'
            external_queue = tmp / 'external-queue'
            symlink_imports.mkdir(parents=True)
            external_queue.mkdir()
            try:
                (symlink_inbox / 'manual-review').symlink_to(external_queue, target_is_directory=True)
            except (OSError, NotImplementedError):
                pass
            else:
                shutil.copy2(exported_zips[0], symlink_imports / exported_zips[0].name)
                symlink_result = subprocess.run(
                    [sys.executable, str(import_script_path), '--eval-inbox', str(symlink_inbox)],
                    cwd=ROOT, text=True, capture_output=True,
                )
                if symlink_result.returncode == 0 or list(external_queue.glob('*.json')):
                    fail('symlinked candidate queue was followed outside the Inbox')

            continuation_inbox = tmp / 'continuation-inbox'
            continuation_imports = continuation_inbox / 'imports'
            continuation_imports.mkdir(parents=True)
            with zipfile.ZipFile(continuation_imports / 'a-long-path.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('x' * 256 + '.json', '{}')
            shutil.copy2(exported_zips[0], continuation_imports / exported_zips[0].name)
            continuation = run([sys.executable, str(import_script_path), '--eval-inbox', str(continuation_inbox)], cwd=ROOT)
            if 'skipped=1' not in continuation.stdout or len(list((continuation_inbox / 'imports/processed').glob('*.zip'))) != 1:
                fail('bad archive path aborted processing of a later valid archive')
            if not (continuation_imports / 'a-long-path.zip').is_file():
                fail('bad archive path was not retained for manual review')
            importer_source = import_script_path.read_text(encoding='utf-8')
            if any(marker in importer_source for marker in ('openai', 'anthropic', 'ollama', 'subprocess')):
                fail('manual importer acquired a model/provider execution dependency')

sync_script_path = ROOT / 'scripts/sync_eval_exchange.py'
if not sync_script_path.is_file():
    fail('missing git-based Eval Inbox transport: scripts/sync_eval_exchange.py')
else:
    # Full push -> pull -> import round trip through a local bare Git
    # repository standing in for a private "exchange" repository, so
    # .local/eval-inbox/ being gitignored on every machine does not strand
    # candidates captured on a second machine that never reaches this one's
    # filesystem directly.
    with tempfile.TemporaryDirectory(prefix='cloudskill-eval-exchange-') as tmp_name:
        tmp = Path(tmp_name)
        bare_exchange = tmp / 'bare-exchange.git'
        source_inbox = tmp / 'source-inbox'
        dest_inbox = tmp / 'dest-inbox'
        (source_inbox / 'candidates').mkdir(parents=True)
        (source_inbox / 'manual-review').mkdir(parents=True)
        run(['git', 'init', '-q', '--bare', str(bare_exchange)], cwd=tmp)

        draft = dict(candidate_template)
        draft['cloudskill_version'] = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        draft['task_summary'] = 'Exchange-transport smoke test'
        draft['prompt_sanitized'] = 'A device accepts a command but the hardware readback has not reached the requested value.'
        (source_inbox / 'candidates' / 'INT-exchange-smoke-positive.json').write_text(
            json.dumps(draft, ensure_ascii=False, indent=2), encoding='utf-8'
        )

        source_config_path = tmp / 'source-config.json'
        source_config_path.write_text(json.dumps({
            'schema_version': '1.0', 'cloudskill_version': draft['cloudskill_version'],
            'cloudskill_repository': str(ROOT), 'eval_inbox': str(source_inbox),
            'sensitive_terms_path': str(source_inbox / 'sensitive-terms.local.txt'),
            'default_sanitization': True, 'save_raw_transcript': False,
            'auto_modify_skills': False, 'auto_commit': False, 'auto_push': False,
            'eval_exchange_repo': str(bare_exchange),
        }), encoding='utf-8')

        git_env = os.environ.copy()
        git_env.setdefault('GIT_AUTHOR_NAME', 'CloudSkill Validator')
        git_env.setdefault('GIT_AUTHOR_EMAIL', 'validator@example.invalid')
        git_env.setdefault('GIT_COMMITTER_NAME', 'CloudSkill Validator')
        git_env.setdefault('GIT_COMMITTER_EMAIL', 'validator@example.invalid')

        run([
            sys.executable, str(sync_script_path), '--push',
            '--config', str(source_config_path), '--clone-dir', str(tmp / 'source-clone'),
            '--label', 'validator-source',
        ], cwd=ROOT, env=git_env)
        if list((source_inbox / 'candidates').glob('*.json')):
            fail('sync_eval_exchange.py --push did not clear the source candidates/ queue')
        if not list((source_inbox / 'synced').glob('*.json')):
            fail('sync_eval_exchange.py --push did not move source files into eval_inbox/synced/')

        dest_config_path = tmp / 'dest-config.json'
        dest_config_path.write_text(json.dumps({
            'schema_version': '1.0', 'cloudskill_version': draft['cloudskill_version'],
            'cloudskill_repository': str(ROOT), 'eval_inbox': str(dest_inbox),
            'sensitive_terms_path': str(dest_inbox / 'sensitive-terms.local.txt'),
            'default_sanitization': True, 'save_raw_transcript': False,
            'auto_modify_skills': False, 'auto_commit': False, 'auto_push': False,
            'eval_exchange_repo': str(bare_exchange),
        }), encoding='utf-8')

        run([
            sys.executable, str(sync_script_path), '--pull',
            '--config', str(dest_config_path), '--clone-dir', str(tmp / 'dest-clone'),
        ], cwd=ROOT, env=git_env)
        if len(list((dest_inbox / 'imports').glob('*.zip'))) != 1:
            fail('sync_eval_exchange.py --pull did not copy the exchanged zip into eval_inbox/imports/')

        run([
            sys.executable, str(import_script_path), '--eval-inbox', str(dest_inbox),
        ], cwd=ROOT)
        if not list((dest_inbox / 'candidates').glob('*.json')) and not list((dest_inbox / 'manual-review').glob('*.json')):
            fail('exchanged candidate did not reach candidates/ or manual-review/ after import')

        # Idempotent re-pull: nothing new once the exchange repo is unchanged.
        rerun = run([
            sys.executable, str(sync_script_path), '--pull',
            '--config', str(dest_config_path), '--clone-dir', str(tmp / 'dest-clone'),
        ], cwd=ROOT, env=git_env)
        if 'Nothing new to pull' not in rerun.stdout:
            fail('re-running sync_eval_exchange.py --pull with nothing new did not report a no-op')

print('Validated full and config-only setup, private Inbox setup, positive capture, manual-review routing, raw-transcript rejection, the disconnected-session export/import round trip, and the git-based eval-exchange push/pull round trip')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
