#!/bin/bash
# Claude Code / Codex CLI PreToolUse hook (Gemini CLI: BeforeTool) --
# deterministic backstop for coding-agent-project-governance's
# references/no-fabricated-identity.md rule: never fill an unrequested
# attribution/owner/proposer/submitted-by field from ambient session
# identity (host git config, logged-in account) when the task supplied no
# such fact.
#
# This does NOT try to detect the semantic pattern (a model can always
# invent a new, differently-named field to carry the same fact -- that
# defeat was observed for real during this repository's own eval work).
# Instead it checks one narrow, deterministic fact: does the *exact*
# ambient git identity (this checkout's `git config user.email` /
# `user.name`) appear in a newly-added line of a staged text file? That is
# a strong, low-false-positive signal specifically for the fabrication
# pattern -- legitimate reasons to commit your own literal email/name into
# a brand-new document field are rare in this workflow, and the project's
# own rule already says to omit the field or use a generic placeholder
# instead.
#
# BLOCKING: git commit is refused if a staged addition contains the
# checkout's own configured email or name in a way that looks like a
# document field (heuristic: same line as a `:` or `-` list-item marker),
# not just anywhere in a diff (a commit message quoting an error log that
# happens to contain an email, for example, should not trip this).
#
# If this is a genuine, requested attribution (a CONTACT file, a LICENSE
# copyright line, an explicit user-provided byline) -- ask the user to
# confirm, then have the user run the commit from a plain shell outside
# this agent session; there is no bypass flag by design, matching the
# equipment-paired-test and push-auth-loop-breaker hooks' posture that a
# BLOCKED state should be reported, not routed around automatically.
#
# Exit 0 = allow. Exit 2 = block (stderr shown to the agent).

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

if ! echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*git[[:space:]]+commit'; then
    exit 0
fi

EMAIL=$(git config user.email 2>/dev/null)
NAME=$(git config user.name 2>/dev/null)

# Nothing to check against -- degrade silently rather than block on an
# unconfigured checkout.
[ -n "$EMAIL" ] || [ -n "$NAME" ] || exit 0

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
[ -n "$STAGED_FILES" ] || exit 0

HITS=""

while IFS= read -r file; do
    [ -f "$file" ] || continue
    # Skip obviously-binary paths cheaply; git diff itself will no-op on
    # real binaries anyway, this just avoids noisy false attempts.
    case "$file" in
        *.png|*.jpg|*.jpeg|*.gif|*.pdf|*.zip|*.ico|*.woff*) continue ;;
    esac

    ADDED=$(git diff --cached -- "$file" | grep -E '^\+' | grep -vE '^\+\+\+')
    [ -n "$ADDED" ] || continue

    for needle in "$EMAIL" "$NAME"; do
        [ -n "$needle" ] || continue
        # Require the needle to sit on a line that also looks like a
        # document field (": " or "- " nearby) -- narrows away incidental
        # mentions (e.g. a quoted log line, a code comment referencing an
        # unrelated example) and targets the "owner:", "- submitted by"
        # shape the real defeats actually took.
        MATCH=$(echo "$ADDED" | grep -F "$needle" | grep -E ':|^\+[[:space:]]*-')
        if [ -n "$MATCH" ]; then
            HITS="$HITS\n  $file: contains \"$needle\" (this checkout's own git identity) in a field-shaped added line"
        fi
    done
done <<< "$STAGED_FILES"

if [ -n "$HITS" ]; then
    echo -e "=== Identity Leak Backstop: BLOCKED ===
  A staged change adds this checkout's own configured git identity
  ($([ -n "$EMAIL" ] && echo "email: $EMAIL")$([ -n "$NAME" ] && echo ", name: $NAME"))
  into what looks like a document field.$HITS

  Per coding-agent-project-governance/references/no-fabricated-identity.md:
  never fill an unrequested attribution/owner/proposer/submitted-by field
  from ambient session identity. If the task did not supply this fact,
  omit the field or use a generic placeholder instead.

  If this really is a requested, intentional attribution (a CONTACT file,
  a LICENSE copyright line, an explicit user-provided byline): report
  BLOCKED and ask the user to confirm and commit it themselves outside
  this session, rather than bypassing this check automatically.
==========================================" >&2
    exit 2
fi

exit 0
