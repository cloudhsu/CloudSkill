#!/usr/bin/env bash
set -euo pipefail

TOOL="both"
SCOPE="user"
PROJECT_PATH="$PWD"
SKIP_GUIDANCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    --project-path) PROJECT_PATH="$2"; shift 2 ;;
    --skip-guidance) SKIP_GUIDANCE=1; shift ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/install.sh [options]
  --tool codex|claude|both
  --scope user|project
  --project-path PATH
  --skip-guidance
EOF
      exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ "$TOOL" =~ ^(codex|claude|both)$ ]] || { echo "Invalid --tool" >&2; exit 2; }
[[ "$SCOPE" =~ ^(user|project)$ ]] || { echo "Invalid --scope" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_SKILLS="$REPO_ROOT/.agents/skills"
BEGIN_MARKER='<!-- CLOUDSKILL:BEGIN -->'
END_MARKER='<!-- CLOUDSKILL:END -->'

copy_skills() {
  local destination="$1"
  mkdir -p "$destination"
  local source target
  for source in "$SOURCE_SKILLS"/*; do
    [[ -d "$source" ]] || continue
    target="$destination/$(basename "$source")"
    rm -rf "$target"
    cp -R "$source" "$target"
  done
}

set_managed_block() {
  local path="$1"
  local content_file="$2"
  mkdir -p "$(dirname "$path")"
  python3 - "$path" "$content_file" "$BEGIN_MARKER" "$END_MARKER" <<'PYBLOCK'
from pathlib import Path
import re, sys
path = Path(sys.argv[1])
content = Path(sys.argv[2]).read_text(encoding='utf-8').strip()
begin, end = sys.argv[3], sys.argv[4]
existing = path.read_text(encoding='utf-8') if path.exists() else ''
block = f"{begin}\n{content}\n{end}"
pattern = re.compile(re.escape(begin) + r'.*?' + re.escape(end), re.S)
if pattern.search(existing):
    updated = pattern.sub(block, existing)
elif existing.strip():
    updated = existing.rstrip() + "\n\n" + block + "\n"
else:
    updated = block + "\n"
path.write_text(updated, encoding='utf-8')
PYBLOCK
}

INSTALL_CODEX=0
INSTALL_CLAUDE=0
[[ "$TOOL" == "codex" || "$TOOL" == "both" ]] && INSTALL_CODEX=1
[[ "$TOOL" == "claude" || "$TOOL" == "both" ]] && INSTALL_CLAUDE=1

if [[ "$SCOPE" == "user" ]]; then
  if [[ $INSTALL_CODEX -eq 1 ]]; then
    copy_skills "$HOME/.agents/skills"
    if [[ $SKIP_GUIDANCE -eq 0 ]]; then
      set_managed_block "$HOME/.codex/AGENTS.md" "$REPO_ROOT/AGENTS.md"
    fi
  fi

  if [[ $INSTALL_CLAUDE -eq 1 ]]; then
    copy_skills "$HOME/.claude/skills"
    if [[ $SKIP_GUIDANCE -eq 0 ]]; then
      mkdir -p "$HOME/.claude/cloudskill"
      cp "$REPO_ROOT/AGENTS.md" "$HOME/.claude/cloudskill/AGENTS.md"
      tmp_import="$(mktemp)"
      printf '%s\n' '@~/.claude/cloudskill/AGENTS.md' > "$tmp_import"
      set_managed_block "$HOME/.claude/CLAUDE.md" "$tmp_import"
      rm -f "$tmp_import"
    fi
  fi
else
  PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"

  [[ $INSTALL_CODEX -eq 1 ]] && copy_skills "$PROJECT_PATH/.agents/skills"
  [[ $INSTALL_CLAUDE -eq 1 ]] && copy_skills "$PROJECT_PATH/.claude/skills"

  if [[ $SKIP_GUIDANCE -eq 0 ]]; then
    set_managed_block "$PROJECT_PATH/AGENTS.md" "$REPO_ROOT/AGENTS.md"
    if [[ $INSTALL_CLAUDE -eq 1 ]]; then
      tmp_import="$(mktemp)"
      printf '%s\n' '@AGENTS.md' > "$tmp_import"
      set_managed_block "$PROJECT_PATH/CLAUDE.md" "$tmp_import"
      rm -f "$tmp_import"
    fi
  fi
fi

echo "CloudSkill installation complete: tool=$TOOL scope=$SCOPE skipGuidance=$SKIP_GUIDANCE"
