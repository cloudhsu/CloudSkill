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

### 6. Control branches and worktrees

- Preserve existing changes.
- Use isolated branches/worktrees for concurrent writers.
- Keep commits single-purpose, testable, and reversible.
- Do not use destructive reset or fabricate history.
- Main/Integrator owns final diff and conflict resolution.

### 7. Require evidence

Handoff must separate:

- PASS.
- FAIL.
- BLOCKED.
- NOT RUN.
- MANUAL REQUIRED.

Do not claim device, OS, deployment, browser, or external-system tests that were not executed.

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
