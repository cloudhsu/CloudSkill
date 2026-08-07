from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable

SAFE_CONFIG = {
    'default_sanitization': True,
    'save_raw_transcript': False,
    'auto_modify_skills': False,
    'auto_commit': False,
    'auto_push': False,
}
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Save one sanitized interaction Eval candidate.')
    parser.add_argument('--kind', choices=sorted(ALLOWED_KINDS), required=True)
    parser.add_argument('--input', required=True, help='Draft JSON file, or - for stdin.')
    parser.add_argument('--project-path', default='.', help='Start directory for project config discovery.')
    parser.add_argument('--config', help='Explicit config JSON path.')
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def read_json(path_arg: str) -> dict[str, Any]:
    text = sys.stdin.read() if path_arg == '-' else Path(path_arg).read_text(encoding='utf-8')
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('candidate draft must be a JSON object')
    return value


def find_project_config(start: Path) -> Path | None:
    start = start.resolve()
    for folder in (start, *start.parents):
        candidate = folder / '.cloudskill' / 'config.local.json'
        if candidate.is_file():
            return candidate
    return None


def resolve_config(explicit: str | None, project_path: str) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f'config not found: {path}')
        return path
    project = find_project_config(Path(project_path))
    if project:
        return project
    user = Path.home() / '.cloudskill' / 'config.json'
    if user.is_file():
        return user
    raise FileNotFoundError('no CloudSkill local config found; run the 5.5.1 installer with local config enabled')


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(config, dict):
        raise ValueError('config must be a JSON object')
    for key, expected in SAFE_CONFIG.items():
        if config.get(key) is not expected:
            raise ValueError(f'unsafe config: {key} must be {expected!r}')
    for key in ('cloudskill_repository', 'eval_inbox', 'sensitive_terms_path'):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'config requires {key}')
    repository = Path(config['cloudskill_repository']).expanduser().resolve()
    inbox = Path(config['eval_inbox']).expanduser().resolve()
    formal_evals = repository / 'evals'
    try:
        inbox.relative_to(formal_evals)
    except ValueError:
        pass
    else:
        raise ValueError('Eval Inbox must not be inside the formal repository evals/ tree')
    config['_repository_path'] = repository
    config['_inbox_path'] = inbox
    config['_sensitive_terms_file'] = Path(config['sensitive_terms_path']).expanduser().resolve()
    return config


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


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(path)


def main() -> int:
    args = parse_args()
    try:
        candidate = read_json(args.input)
        config_path = resolve_config(args.config, args.project_path)
        config = load_config(config_path)
        errors = validate_candidate(candidate, args.kind)
        if errors:
            raise ValueError('; '.join(errors))

        private_terms = load_private_terms(config['_sensitive_terms_file'])
        findings = scan_sensitive(candidate, private_terms)
        sanitization = candidate['sanitization']
        if findings:
            sanitization['status'] = 'MANUAL_REQUIRED'
            sanitization['automated_findings'] = findings

        now = datetime.now(timezone.utc).replace(microsecond=0)
        payload_seed = json.dumps(candidate, ensure_ascii=False, sort_keys=True).encode('utf-8')
        suffix = hashlib.sha256(payload_seed).hexdigest()[:8]
        candidate_id = f"INT-{now.strftime('%Y%m%d-%H%M%S')}-{suffix}"
        candidate['candidate_id'] = candidate_id
        candidate['captured_at'] = now.isoformat()
        candidate['capture_config'] = str(config_path)

        queue = 'candidates' if sanitization['status'] == 'PASS' else 'manual-review'
        output = config['_inbox_path'] / queue / f'{candidate_id}-{args.kind}.json'
        serialized = json.dumps(candidate, ensure_ascii=False, indent=2) + '\n'
        if args.dry_run:
            print(serialized, end='')
            print(f'DRY RUN queue={queue}', file=sys.stderr)
            return 0
        atomic_write(output, serialized)
        print(f'{sanitization["status"]}: {output}')
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
