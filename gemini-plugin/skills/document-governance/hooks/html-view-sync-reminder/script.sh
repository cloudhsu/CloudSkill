#!/bin/bash
# Claude Code / Codex CLI PreToolUse hook (Gemini CLI: BeforeTool) --
# ADVISORY ONLY reminder for document-governance's
# references/html-overview-views.md convention: a governed domain that has
# already opted into a static index.html overview page (product/index.html,
# art/index.html, or equivalent) should keep it committed together with the
# Markdown changes it summarizes. This detects only domains that have
# already opted in (an index.html already exists in that top-level
# directory) -- it never suggests creating one, and it never fires for a
# domain that hasn't adopted the convention.
#
# Deliberately non-blocking: whether a given Markdown edit actually needs
# the HTML view refreshed (a typo fix vs. a real decision/status change) is
# a judgment call this script cannot make. It prints a reminder and always
# allows the commit -- same posture as coding-agent-project-governance's
# lifecycle-evidence-reminder hook.
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
    printf '%s\thtml-view-sync-reminder\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2" >> "$LOG_FILE" 2>/dev/null
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

STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
[ -n "$STAGED" ] || exit 0

# Domains: top-level directories that already contain an index.html (i.e.
# have already opted into the convention).
STALE=""
while IFS= read -r file; do
    case "$file" in
        *.md) ;;
        *) continue ;;
    esac
    domain="${file%%/*}"
    [ "$domain" != "$file" ] || continue   # skip root-level .md files, no domain dir
    index_path="$domain/index.html"
    [ -f "$index_path" ] || continue        # domain hasn't opted in, nothing to remind
    if ! echo "$STAGED" | grep -qF "$index_path"; then
        case "$STALE" in
            *"  - $domain/index.html"*) ;;  # already noted this domain once
            *) STALE="$STALE\n  - $index_path (staged Markdown: $file)" ;;
        esac
    fi
done <<< "$STAGED"

if [ -n "$STALE" ]; then
    log_event "ADVISORY" "governed Markdown changed without its domain index.html"
    echo -e "=== HTML Overview View Reminder (advisory, not blocking) ===
  This commit changes governed Markdown in a domain that already has a
  human-readable index.html overview, but the overview wasn't touched in
  the same commit:$STALE

  Per document-governance/references/html-overview-views.md: not every edit
  needs the HTML view refreshed (wording/typo fixes don't), but a real
  decision or status change does -- an HTML page that silently drifts out
  of sync looks authoritative while being wrong. Confirm before committing.
==============================================================" >&2
fi

exit 0
