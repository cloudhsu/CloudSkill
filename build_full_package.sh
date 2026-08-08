#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TARGET="/Users/cloudhsu/projects/cloudskill/CloudSkill"
TARGET="${1:-$DEFAULT_TARGET}"
OUTPUT="${2:-$(dirname "$TARGET")/CloudSkill-conversation-optimized-full.zip}"

if [[ ! -d "$TARGET/.git" || ! -f "$TARGET/VERSION" ]]; then
  echo "ERROR: target is not a CloudSkill Git clone: $TARGET" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

NAME="CloudSkill-conversation-optimized"
mkdir -p "$TMP/$NAME"

rsync -a \
  --exclude '.git/' \
  --exclude '.local/' \
  --exclude '.cloudskill-backup/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  "$TARGET/" "$TMP/$NAME/"

rm -f "$OUTPUT"
(
  cd "$TMP"
  /usr/bin/zip -qr "$OUTPUT" "$NAME"
)

echo "Full plugin/source package created:"
echo "  $OUTPUT"
