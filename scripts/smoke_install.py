from pathlib import Path
import hashlib
import shutil
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.agents' / 'skills'
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

claude_adapter = ROOT / 'CLAUDE.md'
if not claude_adapter.exists() or '@AGENTS.md' not in claude_adapter.read_text(encoding='utf-8'):
    errors.append('CLAUDE.md does not import @AGENTS.md')

print(f'Smoke-installed {len(list(SOURCE.iterdir()))} canonical skill directories for Codex and Claude')
for error in errors:
    print(f'ERROR: {error}')
sys.exit(1 if errors else 0)
