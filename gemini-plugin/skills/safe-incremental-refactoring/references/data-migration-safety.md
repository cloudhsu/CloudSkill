# Data and Migration Safety

## Before Change

- Back up the authoritative source.
- Calculate a source hash when feasible.
- Work on copies.
- Define schema/version support.
- Define rollback/recovery.
- Preserve historical semantics.
- Identify multi-writer/process assumptions.

## Additive Migration

Prefer additive changes when:

- Old software must still read the database.
- History must remain intact.
- Deployment cannot perform a long offline conversion.
- Risk of destructive rebuild is unacceptable.

Additive does not mean automatically safe. Verify:

- Defaults.
- Backfill.
- nullability.
- indexes.
- uniqueness.
- performance.
- idempotency.
- old-data interpretation.

## Version Gates

A safe gate distinguishes:

- Unversioned/legacy database.
- Minimum supported version.
- Current version.
- Future unsupported version.

A future version should normally fail before any write.

## Persistence Model

Understand whether commit means:

- Database-engine durable commit.
- In-memory commit awaiting file export.
- Remote service acknowledgement.
- Event append.
- File rename.

Design recovery for the actual persistence model, not the SQL vocabulary alone.
