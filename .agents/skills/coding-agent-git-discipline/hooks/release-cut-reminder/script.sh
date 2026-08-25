#!/bin/bash
# Claude Code / Codex CLI PreToolUse hook (Gemini CLI: BeforeTool) --
# ADVISORY ONLY reminder: once commits-since-last-tag crosses a small
# threshold, remind before push that a version bump / release cut is worth
# considering. Direct response to a real gap this repository hit: version
# tags fell 90 commits behind before anyone noticed, because nothing
# checked in between.
#
# Deliberately a small threshold (default 6, in the user-requested 5-8
# range) and deliberately non-blocking -- whether *this specific* push is
# actually a good moment to cut a release (mid-batch work, an incomplete
# PR sequence, a deliberate multi-step change) is a judgment call this
# script cannot make. It asks, every push past the threshold, rather than
# escalating or blocking; "not yet, still mid-batch" is a completely valid
# answer to give it.
#
# Override the threshold per project without editing this installed copy:
# RELEASE_CUT_REMINDER_THRESHOLD=10 (env var).
#
# Exit 0 always (advisory).

THRESHOLD="${RELEASE_CUT_REMINDER_THRESHOLD:-6}"

# LOG_FILE: every reminder this hook prints is also appended here (gitignored)
# so all of this project's hooks can be checked from one place --
# `tail -f .cloudskill-hooks-state/hooks.log` -- instead of only from
# session scrollback.
LOG_FILE=".cloudskill-hooks-state/hooks.log"
log_event() {
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    printf '%s\trelease-cut-reminder\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LOG_FILE" 2>/dev/null
}

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

if ! echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*git[[:space:]]+push'; then
    exit 0
fi

# Needs an actual tag history to compare against; degrade silently on a
# repo with no tags yet rather than demanding one.
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
[ -n "$LAST_TAG" ] || exit 0

COUNT=$(git rev-list --count "${LAST_TAG}..HEAD" 2>/dev/null)
[ -n "$COUNT" ] || exit 0

if [ "$COUNT" -ge "$THRESHOLD" ]; then
    log_event "ADVISORY" "$COUNT commits since $LAST_TAG (threshold $THRESHOLD)"
    echo "=== Release Cut Reminder (advisory, not blocking) ===
  $COUNT commits since the last tag ($LAST_TAG) -- past the $THRESHOLD-commit
  check-in point. Worth considering a version bump / release cut now, before
  this grows into a large undocumented backlog (this repository's own
  CHANGELOG once fell 90 commits behind before anyone noticed).

  Not every push past this threshold is actually a good moment -- mid-batch
  work or an incomplete PR sequence is a fine reason to say 'not yet' and
  keep going. This is a periodic check-in, not an escalating demand.
==========================================" >&2
fi

exit 0
