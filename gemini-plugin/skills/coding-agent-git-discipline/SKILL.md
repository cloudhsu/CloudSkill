---
name: coding-agent-git-discipline
description: Use when a coding agent must commit, push, branch, or clean up git state safely -- avoiding shell-quoting bugs in commit messages, verifying an existing PR's real branch name before pushing fixes, recovering from a failed push (GitHub or a self-hosted forge like Forgejo/Gitea) without a login loop, working a forge through its REST API when `gh` is unavailable, detecting a possibly-shared working tree before committing, and reminding about an overdue version/release cut.
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

The examples below use the GitHub CLI (`gh`) because most of these
mistakes were first hit on GitHub, and GitHub is still in active use.
Every rule applies unchanged to a self-hosted forge (Forgejo, Gitea,
GitLab): there `gh` is typically absent, so the same operation goes
through the forge's REST API, and its token comes from the git
credential helper rather than `gh auth`. A repository may use both at
once (e.g. a self-hosted forge for day-to-day PRs, GitHub for release
mirrors) -- check which remote a given command targets.

## Trigger conditions

- Committing, pushing, branching, or cleaning up branches in a git
  repository as a coding agent.
- Recovering from a failed `git push` (GitHub or self-hosted-forge
  authentication).
- Pushing a fix onto an already-open PR's branch.
- Opening or inspecting a PR/issue on a forge where `gh` is unavailable
  (self-hosted Forgejo/Gitea/GitLab) -- through its REST API.
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
   (`gh pr view <number> --json headRefName -q .headRefName`; on a forge
   with no `gh`, `GET /api/v1/repos/{owner}/{repo}/pulls/{n}` on
   Forgejo/Gitea or `/api/v4/projects/{id}/merge_requests/{n}` on GitLab,
   and read the head-ref field) before pushing a fix, never guess it from
   a naming-convention pattern. A guessed name that is merely plausible
   creates a stray branch needing separate local and remote cleanup, while
   the real PR branch never receives the fix.
3. **Committing in a possibly-shared working tree**: before `git commit`,
   check for unstaged-modified or untracked content not part of the
   commit (`git status --porcelain`). Content sitting dirty at commit
   time that is not yours is the concrete, repeatable signal that another
   agent or session is concurrently working in the same checkout --
   isolate your own changes (`git stash push -u -- <your files>`) and
   work in a separate `git worktree add` checkout rather than committing
   into a possibly-shared tree. See `references/git-commit-and-branch-hygiene.md`.
4. **Recovering from a failed push (GitHub or self-hosted forge)**:
   preserve the local commit, run the read-only `gh auth status` check
   once with redacted output (off GitHub, inspect the git credential
   helper for the forge host directly). If it reports an active account,
   inspect the configured credential helper, remote/protocol, and
   repository/branch permission, then try the existing helper once -- do
   not invoke or repeat `gh auth login` (or the forge's login flow)
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
   behind before anyone noticed. For the mirror question -- is an
   *installed or deployed* build current with its released source (a
   directory/path-source install is a pinned copy that does not advance
   with the source) -- see `coding-agent-project-governance` SS9, which
   owns the release/version-policy treatment; a version-currency prompt
   routes to either skill by phrasing.
7. **A forge that is not GitHub / no `gh`**: use the forge's own REST API
   (Forgejo/Gitea `/api/v1/...`, GitLab `/api/v4/...`) for PR, issue, and
   status-check operations. Get the token from the git credential helper
   for the forge host at call time
   (`printf 'protocol=https\nhost=<forge-host>\n\n' | git credential fill`,
   read the `password=` line) and pipe it into the request -- never
   hardcode a token (including one seen earlier in a `git remote set-url`
   command), echo it to visible output, or write it into a committed file
   or a persisted script, and prefer the existing credential store over
   asking the operator to re-supply a secret the machine already holds.
   After any write, read the object back through the API before reporting
   success.

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
- Reaching for `gh` on a self-hosted forge that has no `gh`, or
  hardcoding a forge token (or re-asking the operator for it) instead of
  pulling it from the git credential helper (real: post-Forgejo-migration
  PRs opened via the forge REST API).

## Supporting references

- `references/git-push-auth-recovery.md` -- full bounded-retry sequence
  and diagnosis table for a failed push (GitHub-specific commands; the
  same sequence on a self-hosted forge substitutes the credential helper
  for `gh auth`).
- `references/git-commit-and-branch-hygiene.md` -- the 4 real-mistake
  lessons in fuller detail (backtick quoting, branch-name verification,
  branch cleanup, next-branch creation).

## Hooks bundled with this skill

`record-push-outcome` + `block-push-auth-loop` (deterministic loop-breaker
for repeated push-auth failures), `shared-checkout-guard` (advisory,
unstaged/untracked-at-commit check), `release-cut-reminder` (advisory,
commits-since-tag check) -- see each hook's own `hooks/<name>/manifest.json`
for install details via this repository's optional hook-installer tool.
