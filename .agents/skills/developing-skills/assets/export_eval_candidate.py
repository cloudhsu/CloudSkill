"""Portable, config-free CloudSkill interaction Eval candidate exporter.

Use this when a coding agent has the `developing-skills` Skill installed but
has NO reachable `.cloudskill/config.local.json` (project) or
`~/.cloudskill/config.json` (user) pointing at a CloudSkill repository clone
on this machine -- a disconnected/external session, such as a different
machine, a cloud sandbox, or a project where local config was never set up.

Normal same-machine capture uses `scripts/capture_eval_candidate.py` in the
CloudSkill repository, which writes directly into a configured Eval Inbox.
This script instead performs the same structural validation and
sanitization scan, but writes into a self-contained local "eval-outbox"
folder (default: `.cloudskill/eval-outbox/`) inside the CURRENT project, and
packages the result into one timestamped zip. The user copies that zip onto
the machine that hosts the CloudSkill repository and drops it into
`<CloudSkillRepo>/.local/eval-inbox/imports/`; `scripts/
import_eval_candidates.py` there merges it into the real Eval Inbox with a
second sensitive-term scan against the repository's own private terms file.

Keep ALLOWED_KINDS, ALLOWED_CONFIDENCE, ALLOWED_SANITIZATION,
PROHIBITED_KEYS, and SENSITIVE_PATTERNS behaviorally identical to
scripts/capture_eval_candidate.py in the CloudSkill repository --
scripts/validate_interaction_capture.py checks these two files stay in sync.
This file has no import dependency on the CloudSkill repository (stdlib
only) because only `.agents/skills/*` travels with an installed Skill;
`scripts/` does not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ALLOWED_KINDS = {'positive', 'negative'}
ALLOWED_CONFIDENCE = {'observed', 'inferred', 'unknown'}
ALLOWED_SANITIZATION = {'PASS', 'MANUAL_REQUIRED'}
PROHIBITED_KEYS = {
    'raw_transcript', 'full_transcript', 'conversation_transcript', 'messages',
    'customer_name', 'company_name', 'person_name', 'source_path', 'repository_url',
}
SENSITIVE_PATTERNS = {
    'email': re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I),
    'ipv4': re.compile(r'(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)'),
    'url': re.compile(r'\bhttps?://[^\s"\']+', re.I),
    'windows_path': re.compile(r'\b[A-Za-z]:\\[^\r\n"\']+'),
    'unc_path': re.compile(r'\\\\[^\\\s]+\\[^\s"\']+'),
    'home_path': re.compile(r'(?<![\w.-])/(?:home|Users)/[^\s"\']+'),
}

DEFAULT_OUTBOX = str(Path('.cloudskill') / 'eval-outbox')
BUNDLE_FORMAT_VERSION = '2.0'
EXPORTER_VERSION = '2.0'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Export one sanitized interaction Eval candidate to a local, config-free '
            'outbox and package it for manual transfer to a CloudSkill repository. Use '
            'when scripts/capture_eval_candidate.py is unreachable on this machine.'
        )
    )
    parser.add_argument('--kind', choices=sorted(ALLOWED_KINDS), required=True)
    parser.add_argument('--input', required=True, help='Draft JSON file, or - for stdin.')
    parser.add_argument('--outbox', default=DEFAULT_OUTBOX, help=f'Local export folder. Default: {DEFAULT_OUTBOX}')
    parser.add_argument(
        '--sensitive-terms',
        help='Optional local private-terms file (one term per line) if one happens to be reachable on this machine.',
    )
    parser.add_argument('--project-name', help='Private export project name; stored in project-local ignored config.')
    parser.add_argument('--host', choices=('codex', 'claude'), default='codex')
    parser.add_argument('--agent-name', help='Agent filename label. Defaults to host or claude-code.')
    parser.add_argument('--project-path', default='.', help='Project containing .cloudskill/config.local.json.')
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--no-zip', action='store_true', help='Write the candidate JSON only; skip packaging a zip.')
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def read_json(path_arg: str) -> dict[str, Any]:
    text = sys.stdin.read() if path_arg == '-' else Path(path_arg).read_text(encoding='utf-8')
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('candidate draft must be a JSON object')
    return value


def walk_items(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_items(child)


def string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from string_values(child)


def load_private_terms(path: Path) -> list[str]:
    if not path.is_file():
        return []
    terms = []
    for line in path.read_text(encoding='utf-8').splitlines():
        term = line.strip()
        if term and not term.startswith('#') and len(term) >= 3:
            terms.append(term)
    return terms


def validate_candidate(candidate: dict[str, Any], expected_kind: str) -> list[str]:
    errors: list[str] = []
    required = {
        'schema_version', 'case_kind', 'status', 'cloudskill_version', 'runtime',
        'task_summary', 'prompt_sanitized', 'expected_skills', 'observed_skills',
        'required_behaviors', 'forbidden_behaviors', 'outcome', 'verification', 'sanitization',
    }
    missing = sorted(required - candidate.keys())
    if missing:
        errors.append('missing fields: ' + ', '.join(missing))
    if candidate.get('case_kind') != expected_kind:
        errors.append(f'case_kind must equal --kind {expected_kind!r}')
    if candidate.get('status') != 'candidate':
        errors.append('status must be candidate')
    for key, child in walk_items(candidate):
        if key in PROHIBITED_KEYS:
            errors.append(f'prohibited raw/identifying field: {key}')
    observed = candidate.get('observed_skills')
    if not isinstance(observed, dict) or observed.get('confidence') not in ALLOWED_CONFIDENCE:
        errors.append('observed_skills.confidence must be observed, inferred, or unknown')
    elif not isinstance(observed.get('skills'), list):
        errors.append('observed_skills.skills must be an array')
    sanitization = candidate.get('sanitization')
    if not isinstance(sanitization, dict):
        errors.append('sanitization must be an object')
    else:
        if sanitization.get('status') not in ALLOWED_SANITIZATION:
            errors.append('sanitization.status must be PASS or MANUAL_REQUIRED')
        if sanitization.get('raw_transcript_saved') is not False:
            errors.append('sanitization.raw_transcript_saved must be false')
    for field in ('expected_skills', 'required_behaviors', 'forbidden_behaviors'):
        if not isinstance(candidate.get(field), list):
            errors.append(f'{field} must be an array')
    if expected_kind == 'negative':
        failures = candidate.get('failure_types', [])
        correction = candidate.get('user_correction_sanitized')
        if not failures and not correction:
            errors.append('negative candidates require failure_types or user_correction_sanitized')
        if not candidate.get('required_behaviors') or not candidate.get('forbidden_behaviors'):
            errors.append('negative candidates require both required and forbidden behaviors')
    return errors


def scan_sensitive(candidate: dict[str, Any], terms: list[str]) -> list[str]:
    findings: list[str] = []
    texts = list(string_values(candidate))
    combined = '\n'.join(texts)
    for label, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(combined):
            findings.append(label)
    folded = combined.casefold()
    for term in terms:
        if term.casefold() in folded:
            findings.append(f'private-term:{term}')
    return sorted(set(findings))


def safe_component(value: str) -> str:
    result = re.sub(r'[^A-Za-z0-9_-]+', '-', value.strip()).strip('-_')
    if not result:
        raise ValueError('export project/agent name is empty or unsafe')
    return result


def resolve_project_name(args: argparse.Namespace) -> str:
    config_path = Path(args.project_path).expanduser().resolve() / '.cloudskill' / 'config.local.json'
    config: dict[str, Any] = {}
    if config_path.is_file():
        value = json.loads(config_path.read_text(encoding='utf-8'))
        if isinstance(value, dict):
            config = value
    name = args.project_name or config.get('export_project_name')
    if not name:
        if args.non_interactive or not sys.stdin.isatty():
            raise ValueError('export_project_name is missing; run interactively with --project-name NAME once')
        name = input('Export project name: ').strip()
    name = safe_component(str(name))
    if config.get('export_project_name') != name:
        config['export_project_name'] = name
        config_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = config_path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(config_path)
    return name


def package_outbox(outbox: Path, payload: Path, project_name: str, host: str, agent_name: str, cloudbox_version: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    bundle_id = uuid.uuid4().hex
    payloads = [payload]
    payload_hashes = {str(path.relative_to(outbox)): hashlib.sha256(path.read_bytes()).hexdigest() for path in payloads}
    manifest = {
        'bundle_format_version': BUNDLE_FORMAT_VERSION,
        'cloudbox_version': cloudbox_version,
        'exporter_version': EXPORTER_VERSION,
        'candidate_schema_version': '1.0',
        'host': safe_component(host).lower(),
        'agent_name': safe_component(agent_name).lower(),
        'export_project_name': project_name,
        'created_at_utc': stamp,
        'bundle_id': bundle_id,
        'payload_hashes': payload_hashes,
    }
    zip_path = Path.cwd() / f'{project_name}-{host}-{agent_name}-{stamp}-{bundle_id[:8]}.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        for path in payloads:
            archive.write(path, arcname=path.relative_to(outbox))
    return zip_path


def main() -> int:
    args = parse_args()
    try:
        candidate = read_json(args.input)
        errors = validate_candidate(candidate, args.kind)
        if errors:
            raise ValueError('; '.join(errors))

        terms: list[str] = []
        if args.sensitive_terms:
            terms = load_private_terms(Path(args.sensitive_terms).expanduser())
        findings = scan_sensitive(candidate, terms)
        sanitization = candidate['sanitization']
        # A disconnected session has no reachable private sensitive-terms file by
        # default, so an automated PASS here is less trustworthy than the normal
        # same-machine path. Stay conservative: only allow PASS through when the
        # caller supplied a real terms file and it (plus the built-in patterns)
        # found nothing.
        if findings or not args.sensitive_terms:
            sanitization['status'] = 'MANUAL_REQUIRED'
            if findings:
                sanitization['automated_findings'] = findings
            sanitization.setdefault(
                'note',
                'exported from a disconnected session without a reachable private '
                'sensitive-terms file; re-scan on import',
            )

        now = datetime.now(timezone.utc).replace(microsecond=0)
        payload_seed = json.dumps(candidate, ensure_ascii=False, sort_keys=True).encode('utf-8')
        suffix = hashlib.sha256(payload_seed).hexdigest()[:8]
        candidate_id = f"INT-{now.strftime('%Y%m%d-%H%M%S')}-{suffix}"
        candidate['candidate_id'] = candidate_id
        candidate['captured_at'] = now.isoformat()
        candidate['capture_config'] = 'export_eval_candidate.py (disconnected session; no CloudSkill repository config)'

        queue = 'candidates' if sanitization['status'] == 'PASS' else 'manual-review'
        outbox = Path(args.outbox).expanduser()
        output = outbox / queue / f'{candidate_id}-{args.kind}.json'
        serialized = json.dumps(candidate, ensure_ascii=False, indent=2) + '\n'
        if args.dry_run:
            print(serialized, end='')
            print(f'DRY RUN queue={queue} outbox={outbox}', file=sys.stderr)
            return 0

        output.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = output.with_suffix(output.suffix + '.tmp')
        tmp_path.write_text(serialized, encoding='utf-8')
        tmp_path.replace(output)
        print(f'{sanitization["status"]}: {output}')

        if not args.no_zip:
            project_name = resolve_project_name(args)
            agent_name = safe_component(args.agent_name or ('claude-code' if args.host == 'claude' else 'codex')).replace('_', '-').lower()
            zip_path = package_outbox(outbox, output, project_name, args.host, agent_name, str(candidate['cloudskill_version']))
            print(f'Exported archive: {zip_path}')
            print(
                'Copy this file into <CloudSkillRepo>/.local/eval-inbox/imports/ on your '
                'CloudSkill machine, then run: python3 scripts/import_eval_candidates.py'
            )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
