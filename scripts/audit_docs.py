from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {'.git', 'history', 'assets'}
GENERATED_PREFIXES = ('gemini-plugin/skills/', 'private-gemini-plugin/skills/', 'private-plugin/codex-skills/')
MIN_CHARS = 120


def normalize(text: str) -> str:
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text


paragraphs = {}
for path in ROOT.rglob('*.md'):
    if any(part in EXCLUDED_PARTS for part in path.parts):
        continue
    relative = str(path.relative_to(ROOT)).replace('\\', '/')
    if relative.startswith(GENERATED_PREFIXES):
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    for index, paragraph in enumerate(re.split(r'\n\s*\n', text), start=1):
        norm = normalize(paragraph)
        if len(norm) < MIN_CHARS:
            continue
        digest = hashlib.sha256(norm.encode('utf-8')).hexdigest()
        paragraphs.setdefault(digest, []).append((path.relative_to(ROOT), index, norm[:100]))

duplicates = [items for items in paragraphs.values() if len({str(item[0]) for item in items}) > 1]
root_markdown = sorted(path.name for path in ROOT.glob('*.md'))
history_snapshots = sorted(path.name for path in (ROOT / 'history').iterdir() if path.is_dir()) if (ROOT / 'history').exists() else []

print(f'Root Markdown files: {len(root_markdown)}')
print(f'Full history snapshot directories: {len(history_snapshots)}')
print(f'Exact long-paragraph duplicate groups: {len(duplicates)}')

for group in duplicates:
    print('DUPLICATE:')
    for path, index, preview in group:
        print(f'  {path} paragraph {index}: {preview}')

if history_snapshots:
    print('ERROR: full version snapshots duplicate Git history:', ', '.join(history_snapshots))
    sys.exit(1)
