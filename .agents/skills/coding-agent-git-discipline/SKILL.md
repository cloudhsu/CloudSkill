---
name: coding-agent-git-discipline
description: Use when a coding agent must commit, push, branch, or clean up git state safely -- avoiding shell-quoting bugs in commit messages, verifying an existing PR's real branch name before pushing fixes, recovering from a failed GitHub push without a login loop, detecting a possibly-shared working tree before committing, and reminding about an overdue version/release cut.
---

# Coding-agent Git Discipline

Extracted from `coding-agent-project-governance` (2026-08-23): that skill
covers the abstract shape of agent governance (instruction layers, risk
routing, agent roles); this skill covers the concrete mechanics of git
itself. A repository typically needs both, composed together, not one in
place of the other.

## Core principle

Git operations are mechanically unforgiving -- a wrong branch name, a
mangled commit message, or a commit into an unexpectedly shared working
tree fails silently or ambiguously rather than with a clear error. Verify
the actual state (branch names, working-tree cleanliness, remote history)
before trusting an assumption or a naming convention, and prefer
deterministic hooks over remembering the rule, since every mistake this
skill's content is drawn from was a real, observed failure to remember.

## Trigger conditions

- Committing, pushing, branching, or cleaning up branches in a git
  repository as a coding agent.
- Recovering from a failed `git push` (especially GitHub authentication).
- Pushing a fix onto an already-open PR's branch.
- Working in a repository another concurrent agent or session might also
  be actively modifying.
- Deciding whether a version bump / release cut is due.

## Non-trigger conditions

- Designing instruction-file layering, risk routing, or agent-role
  assignment for a repository -- use `coding-agent-project-governance`.
- Resolving an in-progress merge/rebase conflict's actual content --
  that is a code-content decision, not a git-mechanics one.

## Required workflow

1. **Commit messages**: for any multi-line commit message referencing file
   paths or code, use `git commit -F -` with a single-quoted heredoc
   delimiter, not a `-m` string containing inline backticks. A backtick in
   shell-invoked commit text can be interpreted as command substitution
   before git ever sees it, silently deleting the quoted text from the
   actual commit -- verify the message landed as written
   (`git log -1 --format=%B`) before treating the commit as done.
2. **Pushing to an existing PR's branch**: fetch the actual branch name
   (`gh pr view <number> --json headRefName -q .headRefName`) before
   pushing a fix, never guess it from a naming-convention pattern. A
   guessed name that is merely plausible creates a stray branch needing
   separate local and remote cleanup, while the real PR branch never
   receives the fix.
3. **Committing in a possibly-shared working tree**: before `git commit`,
   check for unstaged-modified or untracked content not part of the
   commit (`git status --porcelain`). Content sitting dirty at commit
   time that is not yours is the concrete, repeatable signal that another
   agent or session is concurrently working in the same checkout --
   isolate your own changes (`git stash push -u -- <your files>`) and
   work in a separate `git worktree add` checkout rather than committing
   into a possibly-shared tree. See `references/git-commit-and-branch-hygiene.md`.
4. **Recovering from a failed GitHub push**: preserve the local commit,
   run the read-only `gh auth status` check once with redacted output. If
   it reports an active account, inspect the configured credential
   helper, remote/protocol, and repository/branch permission, then try
   the existing helper once -- do not invoke or repeat `gh auth login`
   automatically. If the same authentication failure recurs, stop as
   `BLOCKED`／`MANUAL REQUIRED` and report the exact cause and remaining
   local commit instead of asking the operator to log in repeatedly. See
   `references/git-push-auth-recovery.md`.
5. **Branch cleanup after merge**: local (`git branch -d`) and remote
   (`git push origin --delete` or a merge tool's `--delete-branch`) are
   separate operations; either can fail independently. Never delete a
   branch that is still an active handoff point for other in-progress
   work merely because it looks completed from one vantage point. When
   starting the next unit of work, create the new branch from a freshly
   pulled default branch, not from whatever was checked out a moment
   before -- local and remote branch names can differ.
6. **Version/release cadence**: when commits-since-last-tag has grown
   noticeably (the `release-cut-reminder` hook's threshold, default 6),
   treat it as worth a deliberate check-in -- not every push past the
   threshold is actually a good moment to cut a release, but silently
   never checking is how a repository's own tags once fell 90 commits
   behind before anyone noticed.

## Required output

1. The exact commands run and their real exit status/output.
2. For a push failure: the classified cause (auth/protection/network/
   unknown) and whether it is `BLOCKED`／`MANUAL REQUIRED`.
3. For a branch cleanup: confirmation both local and remote deletion
   succeeded, or which one did not and why.

## Common mistakes

- Guessing a PR's branch name from a naming-convention pattern instead of
  fetching it (real: created a stray branch, the actual PR never got the
  fix until caught and corrected).
- A commit message with inline backticks silently losing the quoted text
  to shell command substitution (real: caught only by reading the commit
  back afterward, fixed via `--amend`).
- Repeating `gh auth login` or a push attempt after the same
  authentication failure recurs, instead of stopping as `BLOCKED`.
- Committing into a working tree without checking for another agent's
  concurrent uncommitted changes first (real: hit repeatedly in one
  session before a deterministic hook was built for it).

## Supporting references

- `references/git-push-auth-recovery.md` -- full bounded-retry sequence
  and diagnosis table for a failed GitHub push.
- `references/git-commit-and-branch-hygiene.md` -- the 4 real-mistake
  lessons in fuller detail (backtick quoting, branch-name verification,
  branch cleanup, next-branch creation).

## Hooks bundled with this skill

`record-push-outcome` + `block-push-auth-loop` (deterministic loop-breaker
for repeated push-auth failures), `shared-checkout-guard` (advisory,
unstaged/untracked-at-commit check), `release-cut-reminder` (advisory,
commits-since-tag check) -- see each hook's own `hooks/<name>/manifest.json`
for install details via this repository's optional hook-installer tool.
