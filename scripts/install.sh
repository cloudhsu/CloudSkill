#!/usr/bin/env bash
set -euo pipefail

TOOL="both"
SCOPE="user"
PROJECT_PATH="$PWD"
CLOUDSKILL_REPO_PATH=""
EVAL_INBOX_PATH=""
SKIP_GUIDANCE=0
SKIP_LOCAL_CONFIG=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    --project-path) PROJECT_PATH="$2"; shift 2 ;;
    --cloudskill-repo-path) CLOUDSKILL_REPO_PATH="$2"; shift 2 ;;
    --eval-inbox-path) EVAL_INBOX_PATH="$2"; shift 2 ;;
    --skip-guidance) SKIP_GUIDANCE=1; shift ;;
    --skip-local-config) SKIP_LOCAL_CONFIG=1; shift ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/install.sh [options]
  --tool codex|claude|both
  --scope user|project
  --project-path PATH
  --cloudskill-repo-path PATH
  --eval-inbox-path PATH
  --skip-guidance
  --skip-local-config
EOF
      exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ "$TOOL" =~ ^(codex|claude|both)$ ]] || { echo "Invalid --tool" >&2; exit 2; }
[[ "$SCOPE" =~ ^(user|project)$ ]] || { echo "Invalid --scope" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [[ -z "$CLOUDSKILL_REPO_PATH" ]]; then CLOUDSKILL_REPO_PATH="$SCRIPT_REPO_ROOT"; fi
REPO_ROOT="$(cd "$CLOUDSKILL_REPO_PATH" && pwd)"
SOURCE_SKILLS="$REPO_ROOT/.agents/skills"
BEGIN_MARKER='<!-- CLOUDSKILL:BEGIN -->'
END_MARKER='<!-- CLOUDSKILL:END -->'

for required in '.agents/skills' 'AGENTS.md' 'VERSION' 'scripts/capture_eval_candidate.py'; do
  [[ -e "$REPO_ROOT/$required" ]] || { echo "CloudSkill repository is missing $required: $REPO_ROOT" >&2; exit 1; }
done

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

initialize_eval_inbox() {
  local inbox="$1"
  mkdir -p "$inbox/candidates" "$inbox/manual-review" "$inbox/processed" "$inbox/rejected"
  local terms="$inbox/sensitive-terms.local.txt"
  if [[ ! -e "$terms" ]]; then
    cat > "$terms" <<'EOF'
# One private identifier per line. This file is never committed by CloudSkill.
# Add company, customer, project, product, machine, site, server, repository, and person names.
# Lines beginning with # are comments.
EOF
  fi
  printf '%s' "$terms"
}

write_local_config() {
  local path="$1" inbox="$2" terms="$3"
  mkdir -p "$(dirname "$path")"
  python3 - "$path" "$REPO_ROOT" "$inbox" "$terms" <<'PYCONFIG'
from pathlib import Path
import json, sys
path = Path(sys.argv[1])
repo = Path(sys.argv[2]).resolve()
inbox = Path(sys.argv[3]).resolve()
terms = Path(sys.argv[4]).resolve()
version = (repo / 'VERSION').read_text(encoding='utf-8').strip()
config = {
    'schema_version': '1.0',
    'cloudskill_version': version,
    'cloudskill_repository': str(repo),
    'eval_inbox': str(inbox),
    'sensitive_terms_path': str(terms),
    'default_sanitization': True,
    'save_raw_transcript': False,
    'auto_modify_skills': False,
    'auto_commit': False,
    'auto_push': False,
}
path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PYCONFIG
}

INSTALL_CODEX=0
INSTALL_CLAUDE=0
[[ "$TOOL" == "codex" || "$TOOL" == "both" ]] && INSTALL_CODEX=1
[[ "$TOOL" == "claude" || "$TOOL" == "both" ]] && INSTALL_CLAUDE=1

if [[ "$SCOPE" == "user" ]]; then
  if [[ $INSTALL_CODEX -eq 1 ]]; then
    copy_skills "$HOME/.agents/skills"
    [[ $SKIP_GUIDANCE -eq 1 ]] || set_managed_block "$HOME/.codex/AGENTS.md" "$REPO_ROOT/AGENTS.md"
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

if [[ $SKIP_LOCAL_CONFIG -eq 0 ]]; then
  if [[ -z "$EVAL_INBOX_PATH" ]]; then EVAL_INBOX_PATH="$REPO_ROOT/.local/eval-inbox"; fi
  EVAL_INBOX_PATH="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())' "$EVAL_INBOX_PATH")"
  terms="$(initialize_eval_inbox "$EVAL_INBOX_PATH")"
  if [[ "$SCOPE" == "user" ]]; then
    config_path="$HOME/.cloudskill/config.json"
  else
    config_dir="$PROJECT_PATH/.cloudskill"
    mkdir -p "$config_dir"
    config_path="$config_dir/config.local.json"
    tmp_ignore="$(mktemp)"
    printf '%s\n' 'config.local.json' 'eval-outbox/' > "$tmp_ignore"
    set_managed_block "$config_dir/.gitignore" "$tmp_ignore"
    rm -f "$tmp_ignore"
  fi
  write_local_config "$config_path" "$EVAL_INBOX_PATH" "$terms"
  echo "CloudSkill local config: $config_path"
  echo "CloudSkill Eval Inbox: $EVAL_INBOX_PATH"
fi

echo "CloudSkill installation complete: tool=$TOOL scope=$SCOPE skipGuidance=$SKIP_GUIDANCE skipLocalConfig=$SKIP_LOCAL_CONFIG"
