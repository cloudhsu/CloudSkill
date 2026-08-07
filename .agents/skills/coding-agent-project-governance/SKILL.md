---
name: coding-agent-project-governance
description: Create or review repository instructions and software-delivery rules for Codex or other coding agents: AGENTS.md, risk routing, subagent roles, worktrees, plans, tests, migrations, documentation sync, release, and truthful handoff. Do not use to design the AI agent product itself.
---

# Coding-agent Project Governance

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

### 5. Assign agent roles only when useful

Possible roles:

- Main/Integrator.
- Architecture.
- Development.
- Test/Adversarial review.
- Security.
- Documentation/release.

Do not use subagents when tasks cannot be isolated or when they will edit the same critical files concurrently.

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

### 8. Release safely

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
