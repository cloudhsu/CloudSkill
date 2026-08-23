#!/bin/bash
# Claude Code / Codex CLI PreToolUse hook (Gemini CLI: BeforeTool) --
# ADVISORY ONLY reminder for a real, recurring failure this repository's
# own agents hit at least 3 times in one session: editing/committing in a
# checkout another concurrent agent (a different session, Luna/Codex, etc.)
# is also actively working in, without noticing until well into the work.
#
# Deliberately simple, matching this repository's "don't over-engineer"
# posture: it cannot know WHOSE uncommitted changes are sitting in the
# working tree, or prove concurrent activity -- it only checks one
# deterministic fact at the one point this class of mistake was actually
# caught in practice every time: is there unstaged/untracked content in
# this repo right now, at the moment of `git commit`? A checkout being
# worked in by only one agent is normally either fully clean or fully
# staged by that same agent right before a commit; unstaged/untracked
# leftovers at commit time are the concrete, repeatable signal that showed
# up every real time this went wrong.
#
# This is intentionally NOT a git-add-time or edit-time check (which would
# need per-provider Edit/Write tool-name matcher research this repository
# hasn't verified yet) -- git-commit-time, with the existing well-tested
# Bash matcher, is where the problem was actually discovered in practice
# every time, so that's where this hook checks too.
#
# Exit 0 always (advisory).

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
    COMMAND=$(echo "$INPUT" | grep -oE '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

if ! echo "$COMMAND" | grep -qE '(^|&&|;)[[:space:]]*git[[:space:]]+commit'; then
    exit 0
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# Unstaged-modified ("M " in column 2) or untracked ("??") entries --
# content sitting in the working tree that this commit will NOT include.
DIRTY=$(git status --porcelain 2>/dev/null | grep -E '^.[MD?]|^\?\?')
[ -n "$DIRTY" ] || exit 0

COUNT=$(echo "$DIRTY" | wc -l | tr -d ' ')

echo "=== Shared Checkout Guard (advisory, not blocking) ===
  $COUNT file(s) in this working tree are modified or untracked but NOT
  part of this commit:
$(echo "$DIRTY" | sed 's/^/    /' | head -10)

  This is the exact pattern that showed up multiple times this session
  when another agent (a different coding-agent session, Codex/Luna, etc.)
  was concurrently working in this same checkout. Before committing:
  confirm these files are your own known leftovers, not another process's
  in-progress work -- 'git status' alone can't tell you which. If unsure,
  isolate your own changes with 'git stash push -u -- <your files>' and
  work in a separate 'git worktree add' checkout instead of committing
  into a possibly-shared working tree.
==========================================" >&2

exit 0
