# Coding Agent Workflow

## Before Modification

- Read applicable `AGENTS.md`.
- Reconstruct the repository and build/test commands.
- Identify the requested behavior and acceptance criteria.
- Inspect relevant code and tests.
- Determine whether an execution plan is required.
- Record assumptions.

## Plan

For complex work, create or update an ExecPlan.

Plan milestones that leave the repository runnable and testable.

## Implement

- Make the smallest coherent change.
- Preserve existing behavior unless change is intentional.
- Avoid unrelated refactoring.
- Update tests with behavior.
- Keep architecture decisions explicit.
- Update controlled documentation when interfaces or behavior change.

## Verify

Run:

- Focused tests.
- Broader regression.
- Build/static analysis.
- Failure/recovery cases.
- Relevant quality gates.

Do not claim a test passed unless it was executed and its result observed.

## Handoff

Report:

- Files changed.
- Behavior changed.
- Tests executed.
- Results.
- Assumptions.
- Remaining risks.
- Follow-up work.
