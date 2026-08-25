#!/bin/bash
# Claude Code Stop / Codex CLI Stop / Gemini CLI AfterAgent hook -- MANDATORY
# (blocking, not merely advisory) reminder that outstanding work should be
# synced into the project-management tracker (project-management-sync's
# convention: consolidate unfinished/worth-tracking items into a task after
# finishing implementation/analysis/review) before the turn actually ends.
#
# Deliberately blunt, not smart: it cannot judge WHAT is worth tracking --
# that stays a model judgment call -- it only checks one narrow, syntactic
# fact: did this turn's transcript show real commit activity with zero
# mention of the tracker anywhere in the same transcript? If so, force one
# more pass to make that judgment explicitly, rather than silently skipping
# it. It fires at most once per stop attempt (see stop_hook_active below),
# so the forced pass is never repeated even if the agent's answer on that
# pass still decides nothing needs tracking.
#
# "Tracker" is detected generically by URL/keyword, not hardcoded to one
# instance -- match PROJECT_TRACKER_HINT below to your own setup, or export
# it as an env var before invoking the agent to override per-project without
# editing this installed copy.
#
# stop_hook_active (present in all 3 providers' Stop/AfterAgent input) is
# true when this exact stop attempt was already forced to continue once by
# a hook -- always allow in that case. This is the standard anti-loop
# mechanism these events are designed around; without it a hook that keeps
# seeing the same "no tracker mention yet" condition would block forever.
#
# Exit 0 = allow. Exit 2 = block with the reason on stderr (same mechanism
# on all 3 providers per their own hook docs -- Claude "Stop", Codex "Stop",
# Gemini "AfterAgent" all treat exit 2 + stderr as "retry/continue with this
# feedback", so this one script works unmodified across all 3; only the
# event name + config file in the manifest differs).

PROJECT_TRACKER_HINT="${PROJECT_TRACKER_HINT:-vikunja}"

# LOG_FILE: every time this hook forces a continue, that event is also
# appended here (gitignored) so all of this project's hooks can be checked
# from one place -- `tail -f .cloudskill-hooks-state/hooks.log` -- instead
# of only from session scrollback. Does not change the exit 2 behavior.
LOG_FILE=".cloudskill-hooks-state/hooks.log"
log_event() {
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    printf '%s\tvikunja-sync-reminder\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LOG_FILE" 2>/dev/null
}

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    STOP_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
    TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')
else
    STOP_ACTIVE=$(echo "$INPUT" | grep -oE '"stop_hook_active"[[:space:]]*:[[:space:]]*(true|false)' | grep -oE 'true|false')
    TRANSCRIPT=$(echo "$INPUT" | grep -oE '"transcript_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*:[[:space:]]*"//;s/"$//')
fi

# Anti-loop: this exact stop attempt was already forced to continue once.
[ "$STOP_ACTIVE" = "true" ] && exit 0

[ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ] || exit 0

# Bound the read -- transcripts can be large; recent activity is what
# matters for "did this turn just do something worth tracking".
RECENT=$(tail -c 300000 "$TRANSCRIPT" 2>/dev/null)
[ -n "$RECENT" ] || exit 0

# Loose text match, deliberately -- same style as this repo's other hooks
# (equipment blocking-wait check, art-draft-catalog): looking for real
# signal, not parsing the transcript's exact schema per provider.
echo "$RECENT" | grep -qiE 'git[[:space:]]+commit' || exit 0
echo "$RECENT" | grep -qi "$PROJECT_TRACKER_HINT" && exit 0

log_event "FORCED_CONTINUE" "commit activity with no '$PROJECT_TRACKER_HINT' mention in transcript"
echo "=== Tracker Sync Reminder: forcing one more pass (not a permanent block) ===
  This turn's transcript shows git commit activity with no mention of
  '$PROJECT_TRACKER_HINT' anywhere in it. Per project-management-sync's
  convention (see coding-agent-project-governance and the standing
  end-of-work sync habit): before actually stopping, decide explicitly
  whether anything from this turn belongs in the tracker as an outstanding
  item -- then either sync it, or state plainly that nothing needs tracking
  and why. This reminder will not repeat on this same stop attempt either
  way (stop_hook_active prevents that); it forces one explicit decision,
  not an unconditional task creation.
==============================================================" >&2
exit 2
