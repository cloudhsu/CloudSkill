#!/bin/bash
# Claude Code / Codex CLI PreToolUse hook (Gemini CLI: BeforeTool) --
# ADVISORY ONLY reminder for this repository's own skill-authoring
# discipline: a commit that changes a skill's SKILL.md or references/
# without also touching that skill's lifecycle.json is easy to miss,
# because there is no single written rule mandating a 1:1 pairing (unlike
# the equipment engine/SelfTest pairing, which is an explicit skill
# requirement). This is exactly the real gap found in this repository's
# own PR #72: substantive skill content shipped with zero lifecycle.json
# change, discovered only during manual review, not by any automated
# check.
#
# Deliberately non-blocking: whether last_reviewed_version, a routing/
# behavior case id list, or the stage needs updating for a given change is
# a judgment call this script cannot make (a pure wording fix does not
# need it; a new reference file describing new required behavior
# probably does). It prints a reminder and always allows the commit.
#
# Assumes this repository's own `.agents/skills/<name>/` layout; not
# meant to be installed outside cloudbox-skills itself.
#
# Exit 0 always (advisory).
#
# LOG_FILE: every reminder this hook prints is also appended here (gitignored)
# so all of this project's hooks can be checked from one place --
# `tail -f .cloudskill-hooks-state/hooks.log` -- instead of only from
# session scrollback.
LOG_FILE=".cloudskill-hooks-state/hooks.log"
log_event() {
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    printf '%s\tlifecycle-evidence-reminder\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LOG_FILE" 2>/dev/null
}

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

if ! echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*git[[:space:]]+commit'; then
    exit 0
fi

[ -f "SKILL_MANIFEST.json" ] && [ -d ".agents/skills" ] || exit 0

STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
[ -n "$STAGED" ] || exit 0

# Skills whose SKILL.md or references/ changed in this commit.
CHANGED_SKILLS=$(echo "$STAGED" | grep -E '^\.agents/skills/[^/]+/(SKILL\.md|references/)' | sed -E 's#^\.agents/skills/([^/]+)/.*#\1#' | sort -u)
[ -n "$CHANGED_SKILLS" ] || exit 0

MISSING=""
while IFS= read -r skill; do
    [ -n "$skill" ] || continue
    if ! echo "$STAGED" | grep -qF ".agents/skills/$skill/lifecycle.json"; then
        MISSING="$MISSING\n  - $skill"
    fi
done <<< "$CHANGED_SKILLS"

if [ -n "$MISSING" ]; then
    log_event "ADVISORY" "SKILL.md/references changed without matching lifecycle.json: $(echo "$CHANGED_SKILLS" | tr '\n' ',' )"
    echo -e "=== Lifecycle Evidence Reminder (advisory, not blocking) ===
  These skills' SKILL.md or references/ changed in this commit but their
  lifecycle.json did not:$MISSING

  This is not always wrong (a pure wording/typo fix doesn't need it), but
  this exact pattern -- real skill content shipped with zero lifecycle.json
  change -- is what got missed on this repository's own PR #72. Consider
  whether last_reviewed_version, stage, or a case-id list should move.
==============================================================" >&2
fi

exit 0
