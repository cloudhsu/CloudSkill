#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TARGET="/Users/cloudhsu/projects/cloudskill/CloudSkill"
TARGET="${1:-$DEFAULT_TARGET}"
OVERLAY="$SCRIPT_DIR/overlay"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$TARGET/.cloudskill-backup/conversation-opt-$STAMP"

if [[ ! -d "$TARGET/.git" ]]; then
  echo "ERROR: target is not a Git clone: $TARGET" >&2
  exit 1
fi

if [[ ! -f "$TARGET/VERSION" || ! -d "$TARGET/.agents/skills" ]]; then
  echo "ERROR: target does not look like CloudSkill: $TARGET" >&2
  exit 1
fi

if [[ ! -d "$OVERLAY" ]]; then
  echo "ERROR: overlay directory missing: $OVERLAY" >&2
  exit 1
fi

mkdir -p "$BACKUP"

while IFS= read -r -d '' source; do
  rel="${source#"$OVERLAY/"}"
  dest="$TARGET/$rel"
  if [[ -e "$dest" ]]; then
    mkdir -p "$BACKUP/$(dirname "$rel")"
    cp -p "$dest" "$BACKUP/$rel"
  fi
done < <(find "$OVERLAY" -type f -print0)

rsync -a "$OVERLAY/" "$TARGET/"

echo "Overlay applied to: $TARGET"
echo "Backup stored at:  $BACKUP"
echo

cd "$TARGET"
echo "Changed files:"
git status --short
echo

if [[ -f scripts/run_all_checks.py ]]; then
  echo "Running structural repository checks..."
  if python3 scripts/run_all_checks.py; then
    echo "Structural checks: PASS"
  else
    echo "Structural checks: FAIL"
    echo "Restore command:"
    echo "  rsync -a \"$BACKUP/\" \"$TARGET/\""
    exit 2
  fi
else
  echo "Structural checks: NOT RUN (scripts/run_all_checks.py missing)"
fi

cat <<EOF

This is an optimization candidate layered on repository version $(cat VERSION).
It does not change the official VERSION or CHANGELOG yet.

Recommended review:
  cd "$TARGET"
  git diff -- .agents/skills/using-cloudskill
  git diff -- .agents/skills/developing-skills
  git diff -- evals SKILL_MANIFEST.json

After review, package the full repository with:
  "$SCRIPT_DIR/build_full_package.sh" "$TARGET"

The installed ChatGPT plugin is not automatically refreshed by changing this clone.
Use the generated full ZIP to update/re-upload the plugin in the ChatGPT Skills UI.
EOF
