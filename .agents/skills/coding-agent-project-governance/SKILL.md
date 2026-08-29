---
name: coding-agent-project-governance
description: Use when a repository needs coding-agent instructions, risk routing, worktree rules, multi-agent ownership, test evidence, migration controls, release rules, or truthful handoff.
---

# Coding-agent Project Governance

When executing a lifecycle plan, require the current authoritative plan
revision, declared task/artifact ownership, dependency-complete entry, explicit
authority, and completion evidence. A stale agent or worker result cannot
advance the plan. Repository actions remain bounded by worktree, test, commit,
PR, migration, and release controls even when another plugin generated the
detailed task steps.

Read:

- `references/instruction-architecture.md`
- `references/risk-routing.md`
- `references/multi-agent-delivery.md`
- `references/artifact-matrix.md`

Use templates in `assets/`.

## Goal

Create a repository operating model in which coding agents can modify software without relying on hidden conversation context, bypassing domain invariants, fabricating evidence, or corrupting unrelated work.

## Workflow

### 1. Inspect before prescribing

Identify:

- Repository root.
- Existing instruction files.
- Source-of-truth code.
- Build/test commands.
- Deployment targets.
- Data and migration risks.
- Domain invariants.
- Git state.
- Existing release/version policy.
- Host toolchain and environment actually available (installed compilers,
  SDKs, target architecture) when the task involves building, cross-compiling,
  or configuring for a specific platform — verify by inspection, do not
  assume from the task description or from what the task "should" need.

Do not generate generic rules that contradict the actual repository.

### 2. Define instruction layers

Keep global `AGENTS.md` concise.

Use repository and nested instructions for:

- Build/test commands.
- Domain invariants.
- Directory responsibilities.
- Security.
- release.
- local exceptions.

Use references and skills for longer workflows.

### 3. Create a project entry map

Provide:

- `00_START_HERE.md`.
- Canonical repository guidance in `AGENTS.md`.
- A minimal `CLAUDE.md` importing `AGENTS.md` when Claude Code is used.
- `PROJECT_CONTEXT.md`.
- `DOMAIN_INVARIANTS.md`.
- `ARCHITECTURE_AND_FILE_MAP.md`.
- `DEVELOPMENT_STANDARDS.md`.
- API/interface docs where applicable.
- Operations/release/checklist docs.
- Decision and requirement history where necessary.

When the repository hosts both a product and a separately-versioned reusable
engine or component library, give product direction (owned by
`document-governance`'s product-direction document role) and visual-artifact
governance (owned by a private companion capability's draft-governance step, when the
repository has one) their own sibling top-level lanes alongside the
development-evidence lane above -- not nested under it. Define what each lane
does and does not have authority over, and require an explicit cross-link
whenever a product or visual decision changes implementation scope, rather
than letting the change land unlinked in only one lane.

Verify the real repo root/branch first; stale pointers are `document-governance` §0.

### 4. Route by risk

Classify work as low, medium, or high risk based on consequence, not code size.

Escalate for:

- Money or balances.
- Authentication/authorization.
- Personal or sensitive data.
- Schema/migration.
- historical data.
- transaction boundaries.
- irreversible external side effects.
- production deployment.
- large architecture changes.
- physical device/process control.

Adopting a new tool-calling/execution-capable dependency (an agent
framework, CLI, plugin marketplace, or similar) as project infrastructure is
itself a security-relevant decision, not just a technology choice.
Independently verify its security track record across multiple authoritative
sources (security-media, vendor advisories, CVE trackers) before recommending
adoption — a single third-party comparison article's summary is not
sufficient evidence, especially when it states a vulnerability count without
detail.

### 5. Assign agent roles only when useful

Possible roles:

- Main/Integrator.
- Architecture.
- Development.
- Test/Adversarial review.
- Security.
- Documentation/release.

Do not use subagents when tasks cannot be isolated or when they will edit the same critical files concurrently. When two or more isolated subagents' inputs do not depend on each other's output, dispatch them in parallel within the same turn rather than serializing work that has no ordering dependency.

### 6. Preserve evidence before it is committed

- Commit product-direction and visual-artifact discussion documents,
  proposal registers, draft images, provenance metadata, and templates once
  they become project evidence -- do not leave the only copy in chat
  history, an ignored worktree, or a generation cache. A commit records
  existence and recoverability, not approval: preserve DRAFT/status
  markers inside the committed artifact itself rather than treating the
  commit event as human sign-off, runtime validation, or release
  readiness. Use versioned filenames or append-only records instead of
  overwriting an earlier draft, and link each checkpoint to its commit.

A dispatched, worktree-isolated subagent's own worktree is not guaranteed to
outlive the subagent's completion -- some are torn down automatically before
the dispatcher retrieves anything from them, others persist, and this is not
predictable in advance. For a read-only investigation/analysis subagent whose
deliverable is a report rather than a commit, require the full findings in
the subagent's own final report message (the channel the dispatcher's task
notification actually preserves), not solely in a file written inside its
own worktree; treat any such file as a best-effort bonus copy the dispatcher
must retrieve immediately if it wants one, never as the only copy of record.

For the git mechanics themselves (branches, worktrees, commit hygiene,
push-auth recovery, shared-checkout detection, release cadence), use
`$coding-agent-git-discipline`.

### 7. Require evidence

Handoff must separate:

- PASS.
- FAIL.
- BLOCKED.
- NOT RUN.
- MANUAL REQUIRED.

Do not claim device, OS, deployment, browser, or external-system tests that were not executed.

Do not fabricate an attribution, author, submitted-by, or other identity
field that the task never supplied, even when a report-style deliverable
"looks like" it should carry one -- see `references/no-fabricated-identity.md`
for the rule, why it recurs across unrelated skills, and how it differs from
the separate known-identity redaction case. A bundled `identity-leak-backstop`
hook enforces this deterministically at commit time.

A CI/PR status-check polling command (or a background task wrapping one) can
report a nonzero exit code or a "failed"-labeled status purely because a check
is still pending, not because it actually failed -- read the command's real
per-check output before classifying the result. Re-run the exact status
command directly to confirm real pass/fail/pending state before reporting a
result to the user or beginning failure diagnosis; do not treat "pending" as
FAIL.

### 8. Stop escalation on repeated failure

After a small fixed number of repeated failures on the same gate/check (for
example, the same push, review, validation, or login/auth step failing again
in essentially the same way), stop and diagnose the cause instead of
continuing:

- Determine whether the blocker is environmental (sandbox/permission denial,
  authentication, network, quota) rather than a code defect. Do not "fix" an
  environment block by rewriting application logic.
- Do not silently retry the identical failing command a fourth, fifth, or
  further time hoping the result changes. A repeated identical failure is
  itself the signal to stop, not evidence that one more attempt is warranted.
- Report BLOCKED with the exact repeated error and the suspected cause, and
  stop there, rather than silently continuing to attempt new workarounds.
- Do not rewrite a core mechanism (security, trust, verification, transport)
  more than once in response to the same repeated failure without an
  explicit user checkpoint. A defensive change made to satisfy one review
  pass must not introduce a new conflict with the agent's own prior changes.

For a failed GitHub `git push` or any other git-mechanics failure, use
`$coding-agent-git-discipline`.

### 9. Release safely

Define:

- Version source.
- Artifact source.
- Build process.
- Migration.
- backup.
- rollback.
- health/version verification.
- changelog.
- requirement/test documentation.
- artifact hash/tag policy.

Checkpoint (commit/tag) scoped exactly to the evidence boundary already
established — not ahead of it, not behind it. Merge only after the target
branch is clean and the tag is reachable from it. When a step remains that
the agent cannot complete itself (a remaining push, an external approval),
leave a precise operator handoff naming exactly what is left and why,
rather than an ambiguous "done" that omits it.

Before rebuilding a GUI or other long-running executable, verify no relevant
process still holds the target output and remind the operator to close it
first. Treat that lock as a stop condition for the operator to resolve —
never force-close a user's running process merely to unblock a build.

## Output Format

1. Repository operating model
2. Instruction hierarchy
3. Entry/read order
4. Domain invariants and authority
5. Risk-routing table
6. Agent roles and concurrency model
7. Git/worktree rules
8. Test and evidence contract
9. Documentation synchronization
10. Release/rollback checklist

## Source-derived Evidence Discipline

For compatibility-sensitive repositories:

- Preserve public method/API inventories as executable contract tests where valuable.
- Preserve database/source hashes during migration tests.
- Test old database copies and future-version refusal.
- Separate product version changes from pure internal refactoring.
- Do not commit regenerated bundles merely because tests rebuilt them unless the release requires it.
- Keep known behavior fixes separate from structural refactoring.
