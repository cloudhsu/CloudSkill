# Durable State Contracts

Use separate contracts for pressures that may coexist but have different
authorities and recovery behavior.

## Logical commit versus durable persistence

Name each commitment boundary: in-memory/SQL transaction commit, file export or
atomic rename, remote acknowledgement, and externally observable completion.
When logical state has committed but authoritative durable persistence fails,
enter an explicit divergence state. Do not report durable success or admit
dependent writes that assume it. Define fail-stop or bounded degraded behavior,
recovery ownership, restart detection, and reconciliation against the actual
durable source.

## Schema compatibility versus product release

Product version and schema version are independent contracts. Persist a schema
version and compare it with an explicit supported schema range; never infer
compatibility from product release numbering. A future unsupported schema must
fail before any write, automatic downgrade, or normalization. Define legacy,
minimum supported, current, and future-version behavior separately.

## Immutable history and correction

If history is evidence, do not rewrite or delete the original fact to make the
current projection convenient. Record a correlated compensating fact with its
authority, reason, time, and target. Define how projections combine the
original and compensation while preserving both provenance and historical
snapshots after current master data changes or disappears.

## Post-external-commit lifecycle

Model local commitment, external request, external acknowledgement, unresolved
timeout, late completion, compensation, and reconciliation as explicit durable
operation states. Carry correlation and idempotency identity across retries and
restarts. Before retrying or compensating, reconcile the local operation record
with the external system; a timeout is uncertainty, not proof of failure.

Keep this lifecycle distinct from logical-commit/file-persistence divergence:
the former reconciles an independently authoritative external side effect; the
latter restores agreement between representations owned by one persistence
design.
