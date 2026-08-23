# GitHub Push Authentication Recovery

This reference governs a failed `git push` to a GitHub remote. It is a
recovery procedure, not authorization to change credentials or bypass branch
protection.

## Required sequence

1. Preserve the local commit, branch, and worktree. Do not reset, rewrite, or
   create a replacement commit merely because the remote push failed.
2. Run `gh auth status` once as a read-only diagnostic. Redact token values,
   account details not needed for diagnosis, headers, cookies, and raw provider
   responses.
3. Inspect the configured Git credential helper, remote URL/protocol, target
   repository, branch, and known permission or protection errors.
4. If `gh auth status` reports an active usable account, use the configured
   credential helper for one bounded push attempt. Do not force an alternative
   token path just because the helper was not tried.
5. If authentication is absent, expired, or rejected, stop and report
   `BLOCKED`／`MANUAL REQUIRED`. The operator may explicitly perform one
   credential refresh or `gh auth login`; the agent must not start a login loop.
6. If the bounded retry fails with the same authentication error, stop. Do not
   repeat login, token retrieval, or push attempts. Reconcile only when the
   error indicates an unknown remote outcome rather than authentication
   rejection.

## Diagnosis table

| Evidence | Next action | Do not do |
|---|---|---|
| `gh auth status` is healthy, push auth fails | inspect helper, protocol, repo／branch permission; try helper once | repeatedly log in or print tokens |
| `gh auth status` is not authenticated | hand off for explicit operator login／credential refresh | automatically invoke `gh auth login` |
| repository／branch permission or protection rejection | report required permission／review／PR path | treat it as a credential problem and re-login repeatedly |
| network／DNS／proxy failure | diagnose transport or wait for external recovery | rotate credentials or rewrite repository files |
| timeout after request may have committed | read remote state before retrying | assume failure and push a duplicate |

## Handoff minimum

Report the repository and branch in scope, local commit hash, sanitized error
class, `gh auth status` result category, helper/protocol diagnosis, whether a
bounded helper retry was attempted, and the exact manual action remaining.
Never report token text, Authorization headers, full account identifiers, or a
successful push unless the remote branch was read back and matched the local
commit.
