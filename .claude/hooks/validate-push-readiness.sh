#!/bin/bash
# Claude Code / Codex CLI PreToolUse (Gemini CLI: BeforeTool) hook for the
# cloudbox-skills repository itself: catches the exact class of gap that
# defeated PR #72 tonight -- content committed and pushed without re-running
# sync_gemini_plugins.py/sync_private_codex_plugin.py first, caught only
# after CI ran on GitHub instead of locally before the push.
#
# BLOCKING: git push is refused if the canonical Gemini projection is stale
# relative to .agents/skills/ (the single cheapest, most frequently-missed
# check; mirrors what CI's own first failing step actually checks).
#
# This is deliberately narrower than re-running the full run_all_checks.py
# suite on every push (that takes real time and this hook has a short
# timeout) -- it targets specifically the mistake that was actually observed
# tonight. Extend the SKIP-conditions below if a genuinely local-only
# uncommitted-experiment push needs to bypass it.
#
# Exit 0 = allow. Exit 2 = block (stderr shown to the agent, which can then
# run the sync scripts and retry).
#
# LOG_FILE: every real finding (blocked push, or the checker itself failing
# to run) is appended here in addition to stderr -- gitignored, one line per
# event, so a noisy environment can be triaged from its own history (`tail
# -f .cloudskill-hooks-state/hooks.log`) instead of only from session
# scrollback. This does not replace the stderr message on an actual block --
# the agent still needs that to react -- it only adds a durable trail.

LOG_FILE=".cloudskill-hooks-state/hooks.log"
log_event() {
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    printf '%s\tvalidate-push-readiness\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LOG_FILE" 2>/dev/null
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

# Only meaningful inside an actual cloudbox-skills checkout -- degrade
# silently (allow) anywhere else rather than erroring on a repo that
# happens to also use this hook file by coincidence.
[ -f "SKILL_MANIFEST.json" ] && [ -d ".agents/skills" ] || exit 0

PYTHON_CMD=""
for cmd in python3.11 python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON_CMD="$cmd"
        break
    fi
done
[ -n "$PYTHON_CMD" ] || exit 0

if ! "$PYTHON_CMD" scripts/sync_gemini_plugins.py --check >/tmp/cloudskill-push-readiness.$$ 2>&1; then
    OUTPUT=$(cat /tmp/cloudskill-push-readiness.$$)
    rm -f /tmp/cloudskill-push-readiness.$$

    # Behavior unchanged from before (still always blocks push on any
    # non-zero result, including a checker crash) -- this only mirrors the
    # same detail into LOG_FILE as well, tagged so a script-crash can be
    # told apart from a real staleness finding when triaging the log.
    if echo "$OUTPUT" | grep -q "Traceback (most recent call last)"; then
        log_event "BLOCKED_SCRIPT_ERROR" "$(echo "$OUTPUT" | tr '\n' ' ' | cut -c1-200)"
    else
        log_event "BLOCKED" "$(echo "$OUTPUT" | tr '\n' ' ' | cut -c1-200)"
    fi
    echo "=== Push Readiness: BLOCKED ===
  Gemini/Codex plugin projections are stale relative to .agents/skills/ --
  the exact gap that failed this repository's own CI on a real PR tonight.
  Run before pushing:
    $PYTHON_CMD scripts/sync_gemini_plugins.py
    $PYTHON_CMD scripts/sync_private_codex_plugin.py
  Then re-add and re-commit the projection files, and retry the push.
  Detail:
$OUTPUT
================================" >&2
    exit 2
fi
rm -f /tmp/cloudskill-push-readiness.$$

exit 0
