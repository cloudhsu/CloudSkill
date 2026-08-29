# Synchronization contract

## Authority

The source backlog owns intended work and provenance. The provider owns its
remote identifier, permission checks, status representation, and committed
remote result. A local mapping is a cache of identity, not proof that a remote
mutation succeeded.

Recommended mapping fields:

```text
source_system, source_key, target_provider, target_profile,
target_project_key, target_record_id, last_seen_revision, last_reconciled_at
```

Keep mapping data local/private unless the repository explicitly governs it;
never store credentials in it.

## Field ownership and conflicts

For one-way sync, list the source-owned fields and preserve provider-owned
fields. For bidirectional sync, record an owner and conflict policy per field:

```text
field, source_owner, target_owner, conflict_policy, last_reconciled_revision
```

Use explicit policies such as `source-wins`, `target-wins`, `manual-review`, or
`merge`. Do not silently use last-write-wins, wall-clock ordering, or a whole
record overwrite when the field contract is missing or stale.

## Operation states

```text
planned -> requested -> acknowledged -> verified
                    \-> unknown -> reconciled -> verified|blocked
```

`unknown` covers timeout, connection loss, process termination, or a lost
response after a request could have committed. Reconcile by remote read before
retrying. Carry a correlation/idempotency key across retries and restarts when
the provider supports one.

## Matching and mutation

- Prefer a persisted source key or remote ID.
- A single exact fallback match may be proposed, but must be shown in the plan.
- Multiple matches, missing required project scope, or changed ownership block
  mutation.
- Create only after the complete target scope has been enumerated.
- Update only fields owned by the source; do not overwrite provider-owned
  comments, work logs, permissions, or custom fields without an explicit rule.
- Treat a missing, stale, or conflicting field-ownership rule as read-only for
  that field and surface it as `blocked` or `manual-review`.
- Never delete as part of ordinary synchronization.

For the bundled Vikunja helper, status ownership must be declared explicitly
as `source_owned_fields: ["status"]`. Omitting it keeps remote status read-only.

## Time and status

Map canonical states through an explicit table. Preserve `unknown` when a
provider has no safe equivalent. Use provider completion fields such as
`done_at` when available; derive elapsed time from authoritative timestamps only
when the provider has no duration field, and label it as derived.

Dates must include timezone and source (`provider`, `source`, or `derived`). Do
not use a planning `end_date` as a completion timestamp unless the provider
contract explicitly defines it that way.

## Verification

After each mutation, read back the record and verify the fields changed, its
remote ID, completion timestamp, and any revision/updated marker. Re-enumerate
the scope when create/no-duplicate claims matter. A local success message is
not sufficient evidence.
