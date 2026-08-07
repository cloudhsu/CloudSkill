# Refactoring Evidence Checklist

## Contract

- Public methods unchanged or versioned.
- API routes/status/error codes preserved.
- Return shape preserved.
- Ordering semantics preserved.
- Authentication/RBAC preserved.

## Data

- Transaction invariants preserved.
- Historical snapshots preserved.
- Migration idempotent.
- Integrity check passes.
- Source database remains unchanged during compatibility tests.
- Future-version refusal is zero-write.

## Failure

- Validation failure performs no write.
- Mid-transaction failure rolls back.
- Persistence failure restores or blocks safely.
- Duplicate/retry behavior is defined.
- Audit/event writes follow the required order.

## Delivery

- Focused tests pass.
- Regression passes.
- Build/package verified when affected.
- Documentation synchronized.
- Diff contains no unrelated generated artifact.
- Unrun tests are explicitly listed.
