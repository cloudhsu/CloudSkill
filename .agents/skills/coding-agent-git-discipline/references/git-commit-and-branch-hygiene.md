# Git Commit and Branch Hygiene

Practices distilled from real mistakes made in this repository's own
development, none of them hypothetical. Originally written under
`coding-agent-project-governance` (which had no byte budget left to point
here directly); moved to `coding-agent-git-discipline` 2026-08-23 when git
mechanics were split out into their own skill, which does point here from
its own SKILL.md.

## Commit messages: avoid backticks in shell-invoked commit text

A commit message written with inline backtick-quoted paths (for example
`` `.worktrees/` ``) passed through certain shell invocation styles gets the
backticks interpreted as command substitution before git ever sees the
message -- the quoted text silently disappears from the actual commit,
discovered only by reading back `git log -1 --format=%B` afterward. Prefer
`git commit -F -` with a single-quoted heredoc delimiter for any multi-line
commit message that references file paths or code, and verify the message
landed as written before treating the commit as done, not just before
pushing it.

## Pushing to an existing PR's branch: verify, don't guess

Before pushing a fix onto an already-open PR's branch, fetch the actual
branch name (`gh pr view <number> --json headRefName -q .headRefName`)
rather than guessing it from a naming-convention pattern remembered from
elsewhere in the session. A guessed name that happens to be plausible but
wrong creates a stray branch on the remote (which then needs separate local
and remote deletion to clean up) while the actual PR branch silently never
receives the fix.

## Branch cleanup after merge: local and remote are separate operations

Deleting a completed branch after it merges into the default branch is two
distinct operations -- local (`git branch -d`) and remote (`git push origin
--delete` or a merge tool's own `--delete-branch` flag) -- and either can
fail or be skipped independently of the other. A branch delete failing
locally because a fork agent's isolated worktree still has it checked out
is not itself a problem; it just means local cleanup happens later, once
that worktree is removed. Never delete a branch that is still an active
handoff point for other in-progress work merely because it looks
"completed" from one vantage point.

## Creating the next work branch: confirm the actual current name

After merging into the default branch and starting the next unit of work,
create the new branch from a freshly pulled default branch
(`git checkout main && git pull` before `git checkout -b <new-branch>`),
not from whatever branch happened to be checked out a moment before --
local and remote branch names can differ (a renamed remote branch, a
locally-renamed tracking branch, a stray branch from an earlier mistake),
and starting the next branch from the wrong base silently carries over
content that should not be there.
