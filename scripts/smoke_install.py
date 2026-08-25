from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.agents' / 'skills'
DIST = ROOT / 'config' / 'skill-distribution.json'
errors = []

def hashes(root: Path):
    result = {}
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        result[str(path.relative_to(root)).replace('\\','/')] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

with tempfile.TemporaryDirectory(prefix='cloudskill-install-') as tmp:
    tmp = Path(tmp)
    codex = tmp / 'codex' / '.agents' / 'skills'
    claude = tmp / 'claude' / '.claude' / 'skills'
    shutil.copytree(SOURCE, codex)
    shutil.copytree(SOURCE, claude)
    expected = hashes(SOURCE)
    if hashes(codex) != expected:
        errors.append('Codex smoke-install copy differs from canonical skills')
    if hashes(claude) != expected:
        errors.append('Claude smoke-install copy differs from canonical skills')
    for package_name in ('gemini-plugin', 'private-gemini-plugin', 'public-plugin'):
        source = ROOT / package_name / 'skills'
        if source.is_dir():
            installed = tmp / package_name / 'skills'
            shutil.copytree(source, installed)
            if hashes(installed) != hashes(source):
                errors.append(f'{package_name} smoke-install copy differs from its projection')

    if (ROOT / 'public-plugin').is_dir():
        distribution = json.loads(DIST.read_text(encoding='utf-8'))
        expected_public = sorted(name for name, tier in distribution['skills'].items() if tier == 'core')
        actual_public = sorted(path.name for path in (ROOT / 'public-plugin' / 'skills').iterdir() if path.is_dir())
        if actual_public != expected_public:
            errors.append('public-plugin contains a non-core Skill or is missing a core Skill')

claude_adapter = ROOT / 'CLAUDE.md'
if not claude_adapter.exists() or '@AGENTS.md' not in claude_adapter.read_text(encoding='utf-8'):
    errors.append('CLAUDE.md does not import @AGENTS.md')

print(f'Smoke-installed {len(list(SOURCE.iterdir()))} canonical Skill directories and Gemini projections')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
