# Configuration and Snapshot Contracts

## Configuration

Configuration describes intended composition and binding. Record schema version, component IDs, types, capabilities, IO addresses, units, ranges, interlocks, recipe/UI metadata, product variant, and migration history.

Validate syntax and semantics before activation. Unknown component types, duplicate IDs, missing IO, invalid capability combinations, and incompatible schema versions must fail safely.

## Snapshot

A snapshot describes observed/projected state at a time. Include producer identity, time, schema/capability version, component IDs, readback timestamps, quality/staleness, and any intentional Desired/Pending/Error projection.

## Separation

- Configuration is not readback.
- Snapshot is not a command.
- UI metadata is not authorization.
- A serialized object is not automatically a stable wire contract.
- Version compatibility must be defined for readers and writers independently.
