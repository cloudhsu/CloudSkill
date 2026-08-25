#!/bin/bash
# PreToolUse hook (Bash): blocks a repeated git push or an automatic
# `gh auth login` once the journal (written by the companion PostToolUse
# hook, record-push-outcome.sh) shows the last N consecutive `git push`
# attempts failed with the same authentication-related classification.
#
# This is the deterministic enforcement of
# coding-agent-project-governance/references/git-push-auth-recovery.md's
# core rule -- "if the bounded retry fails with the same authentication
# error, stop... do not repeat login, token retrieval, or push attempts" --
# so a session cannot loop through login prompts even if it forgets the
# skill's own instruction to stop.
#
# THRESHOLD consecutive auth_failure entries (most recent first) trigger a
# block. A success entry, or an entry older than STALE_MINUTES, resets the
# count -- this is a loop-breaker for the current situation, not a
# permanent ban on ever pushing again in this project.
#
# Exit 0 = allow. Exit 2 = block (stderr shown to the agent).
#
# LOG_FILE: every block this hook issues is also appended here (gitignored)
# so all of this project's hooks can be checked from one place --
# `tail -f .cloudskill-hooks-state/hooks.log` -- instead of only from
# session scrollback. Does not change the exit 2 behavior.
LOG_FILE=".cloudskill-hooks-state/hooks.log"
log_event() {
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    printf '%s\tblock-push-auth-loop\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LOG_FILE" 2>/dev/null
}

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

IS_PUSH=0
IS_LOGIN=0
echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*git[[:space:]]+push' && IS_PUSH=1
echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*gh[[:space:]]+auth[[:space:]]+login' && IS_LOGIN=1

if [ "$IS_PUSH" -eq 0 ] && [ "$IS_LOGIN" -eq 0 ]; then
    exit 0
fi

JOURNAL_FILE=".cloudskill-hooks-state/push-auth-journal.jsonl"
[ -f "$JOURNAL_FILE" ] || exit 0

THRESHOLD=2
STALE_MINUTES=30

CONSECUTIVE=$(python3 - "$JOURNAL_FILE" "$STALE_MINUTES" 2>/dev/null <<'PYEOF'
import json, sys, datetime

path, stale_minutes = sys.argv[1], int(sys.argv[2])
try:
    lines = [json.loads(l) for l in open(path) if l.strip()]
except Exception:
    print(0)
    sys.exit(0)

now = datetime.datetime.now(datetime.timezone.utc)
count = 0
for entry in reversed(lines):
    try:
        ts = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
    except Exception:
        break
    if (now - ts).total_seconds() > stale_minutes * 60:
        break
    cls = entry.get("class")
    if cls == "auth_failure":
        count += 1
    else:
        break
print(count)
PYEOF
)

CONSECUTIVE=${CONSECUTIVE:-0}

if [ "$CONSECUTIVE" -ge "$THRESHOLD" ]; then
    log_event "BLOCKED" "$CONSECUTIVE consecutive auth_failure entries within ${STALE_MINUTES}m"
    echo "=== Push-Auth Loop Breaker: BLOCKED ===
  $CONSECUTIVE consecutive git push attempts recorded the same authentication-failure
  class within the last $STALE_MINUTES minutes ($JOURNAL_FILE).
  Per references/git-push-auth-recovery.md: stop here. Report BLOCKED/MANUAL REQUIRED
  with the local commit hash and the recorded failure class. The operator may run
  'gh auth login' or refresh credentials manually -- this agent must not do it
  automatically or retry the push again until that happens.
========================================" >&2
    exit 2
fi

exit 0
