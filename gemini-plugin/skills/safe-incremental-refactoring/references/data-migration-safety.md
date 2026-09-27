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

## Externalizing Compiled Constants into Tunable Data

When a slice moves hardcoded/compiled constants (tuning tables, balance
values, non-safety-critical configuration) into a runtime-loaded,
schema-validated data file, treat this as an additive migration whose old
compiled values are the fallback, not as a wholesale replacement:

- Keep the compiled defaults reachable and used whenever the new file is
  missing, unreadable, or a caller constructs the type directly and bypasses
  the loader entirely -- existing call sites and tests need zero changes.
- Apply the file's contents as a per-field, per-id merge over the compiled
  defaults (only overwrite a field the file actually specifies), not a
  wholesale replace, so a partial or hand-edited file degrades safely
  instead of erasing every field the author didn't intend to touch.
- A missing or malformed file is a warning plus a fallback to the compiled
  defaults, not a hard startup failure -- reserve fail-closed startup for
  state where an unvalidated default would be unsafe or authoritative
  (see the safety-critical caveat below), not for tunable content whose old
  compiled values already shipped safely.
- Give the new rule family its own schema and its own rule-ID prefix under
  the project's existing validator, rather than folding a functionally
  distinct family into an existing unrelated rule category merely because
  the validator already has a home for it. Add data-specific consistency
  checks beyond schema validity: duplicate ids, missing expected ids,
  unknown ids, and any cross-field check between two fields meant to
  represent the same real-world quantity.

This fallback-on-missing-file guidance does not apply to authoritative or
safety-critical state (equipment limits, security/authorization data,
transaction-affecting configuration) -- there, a missing or invalid file
must fail closed per this skill's ordinary "preserve ordering and failure
semantics" rule, not silently fall back to a compiled value that may no
longer be correct.

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
