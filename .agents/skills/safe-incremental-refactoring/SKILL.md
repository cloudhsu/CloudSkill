---
name: safe-incremental-refactoring
description: Plan or execute behavior-preserving modernization of a legacy or brownfield system, especially god classes, monoliths, persistence layers, transaction-heavy code, or compatibility-sensitive APIs. Use when responsibilities must move without breaking contracts, data, release behavior, or fault-injection seams.
---

# Safe Incremental Refactoring

Read:

- `references/refactoring-workflow.md`
- `references/compatibility-facade.md`
- `references/data-migration-safety.md`
- `references/evidence-checklist.md`

Use `assets/REFACTOR_SLICE.template.md` for each non-trivial slice.

## Goal

Reduce structural risk without combining behavioral change, architecture migration, schema change, and release change into one unverifiable batch.

## Workflow

### 1. Establish the behavioral baseline

Identify:

- Public methods, APIs, events, files, and data contracts.
- State and transaction invariants.
- Existing defects that must not be silently changed.
- Deployment and persistence constraints.
- Current tests and missing safety nets.
- Fault-injection or monkeypatch seams relied upon by tests or operations.

Add characterization tests before moving responsibility.

### 2. Classify the extraction candidate

Prefer this order when appropriate:

1. Pure policy and value normalization.
2. Read-only queries/projections.
3. Narrow repository primitives.
4. Low-risk application services.
5. High-risk transaction commands.
6. Schema/migration orchestration.
7. HTTP/UI composition and routing.

Do not follow this order mechanically when a different dependency or failure boundary dominates.

### 3. Define the slice

Each slice must state:

- Exact methods/use cases moved.
- Exact behavior intentionally unchanged.
- Public compatibility surface retained.
- Transaction owner.
- State owner.
- Capabilities granted to the new component.
- Tests proving equivalence.
- Rollback path.
- Explicit exclusions.

### 4. Restrict capability

Do not pass a powerful façade or raw database object when a narrower port is sufficient.

Examples:

- Query-only port.
- Command-only port.
- Unit-of-work/transaction port.
- Clock.
- ID generator.
- External service contract.
- Mapper.

The new component must not gain lifecycle, transaction, save, close, deployment, or security authority accidentally.

### 5. Preserve ordering and failure semantics

For transaction-heavy work, verify:

- Validation precedence.
- Query/write order.
- Audit/event order.
- Error code/status.
- Retry and idempotency.
- Rollback.
- Post-commit persistence.
- Late or partial failure.
- Return shape.

Equivalent final data is not sufficient when operational ordering is part of the contract.

### 6. Separate refactor from behavior change

When an existing defect is discovered:

- Record it.
- Add a reproducing test if safe.
- Decide whether the current slice preserves or fixes it.
- Do not quietly fix it inside a structural change.
- Use a separate decision, patch, and release note for the behavior change.

### 7. Verify

Run:

- Focused unit/characterization tests.
- Contract/prototype/API tests.
- Fault-injection tests.
- Integration tests.
- Realistic database-copy or fixture tests.
- Migration idempotency.
- Build/package checks when affected.
- `git diff --check`.

### 8. Handoff

Report:

- Responsibilities moved.
- Compatibility retained.
- Tests actually executed.
- Tests not executed.
- Behavior intentionally preserved.
- Known defects isolated.
- Next safe slice.
- Stop/escalation conditions.

## Output Format

1. Current responsibility map
2. Behavioral and data invariants
3. Safety-net gaps
4. Proposed refactoring slices
5. Capability and ownership design
6. Per-slice verification
7. Rollback and stop conditions
8. Known defects kept separate
9. Recommended next slice
