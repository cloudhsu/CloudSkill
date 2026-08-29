#!/bin/bash
# PostToolUse hook (Bash): records the outcome of a `git push` attempt into
# a small local journal, so the companion PreToolUse hook
# (block-push-auth-loop) can detect a repeated identical authentication
# failure and stop the loop deterministically -- implementing
# coding-agent-project-governance/references/git-push-auth-recovery.md's
# "stop as BLOCKED/MANUAL REQUIRED... do not repeat login" rule without
# relying on the model remembering to stop itself.
#
# Generic: works in any git repository, not just cloudbox-skills. Originally
# built and tested in cloudbox-skills itself (which still keeps its own
# directly-installed copy); this bundled copy is the reusable, installable
# form for other repositories via install_skill_hooks.py.
#
# Input schema (PostToolUse for Bash): includes tool_input.command and the
# command's own result. Provider PostToolUse payload shapes differ slightly;
# this reads whichever of tool_response/tool_output/output/stdout+stderr is
# present and degrades to "unknown outcome, do not record a failure" if none
# parse -- a missed record only weakens the loop-breaker, it never blocks a
# push that would otherwise succeed.
#
# Journal: .cloudskill-hooks-state/push-auth-journal.jsonl -- add that path
# to the installed project's own .gitignore before relying on it; the
# installer does this automatically, a manual install should too.
#
# Always exits 0 -- this hook only records, it never blocks (blocking is
# block-push-auth-loop's job, running as PreToolUse on the *next* call).

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
    RAW_OUTPUT=$(echo "$INPUT" | jq -r '(.tool_response.output // .tool_response.stdout // .tool_output // .output // "") + "\n" + (.tool_response.stderr // .error // "")' 2>/dev/null)
    EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_response.exit_code // .tool_response.exitCode // empty' 2>/dev/null)
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
    RAW_OUTPUT="$INPUT"
    EXIT_CODE=""
fi

if ! echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*git[[:space:]]+push'; then
    exit 0
fi

JOURNAL_DIR=".cloudskill-hooks-state"
JOURNAL_FILE="$JOURNAL_DIR/push-auth-journal.jsonl"
mkdir -p "$JOURNAL_DIR"

# Classify the outcome from output text (loose, deliberately -- a missed
# classification just means this entry looks like "unknown", not "failed").
CLASS="unknown"
if echo "$RAW_OUTPUT" | grep -qiE 'authentication failed|could not read username|could not read password|403|permission denied \(publickey\)|support for password authentication was removed|remote: invalid username or password'; then
    CLASS="auth_failure"
elif echo "$RAW_OUTPUT" | grep -qiE 'protected branch|required status check|review required|branch is protected'; then
    CLASS="protection_rejection"
elif [ -n "$EXIT_CODE" ] && [ "$EXIT_CODE" = "0" ]; then
    CLASS="success"
elif echo "$RAW_OUTPUT" | grep -qiE '! \[rejected\]|failed to push|error: failed'; then
    CLASS="other_failure"
fi

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '{"timestamp":"%s","class":"%s"}\n' "$TIMESTAMP" "$CLASS" >> "$JOURNAL_FILE"

# Also mirror non-success/non-unknown outcomes into the unified hooks log
# (gitignored) so a failing push shows up in the same place as every other
# hook's findings -- `tail -f .cloudskill-hooks-state/hooks.log` -- without
# duplicating every routine successful push into it.
if [ "$CLASS" != "success" ] && [ "$CLASS" != "unknown" ]; then
    printf '%s\trecord-push-outcome\t%s\tgit push outcome recorded\n' "$TIMESTAMP" "$CLASS" >> ".cloudskill-hooks-state/hooks.log" 2>/dev/null
fi

exit 0
