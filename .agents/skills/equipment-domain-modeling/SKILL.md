---
name: equipment-domain-modeling
description: Use when modeling chamber or component state, equipment commands, hardware readback, Actual and Desired values, pending writes, snapshots, capability interfaces, metadata-driven UI, or typed command payloads.
---

# Equipment Domain Modeling

## Core principle

Model identity, authority, lifecycle, and temporal meaning before optimizing fields or inheritance. Similar fields prove a repeated capability or data pattern; they do not prove two device types have the same identity.

Read:

- `references/state-command-reconciliation.md`
- `references/command-catalog-and-capability-model.md`
- `references/config-and-snapshot-contracts.md`

Use:

- `assets/EQUIPMENT_DOMAIN_MODEL.template.md`
- `assets/EQUIPMENT_COMMAND_CONTRACT.template.md`

## Workflow

### 1. Classify every model by purpose and lifecycle

Separate:

- Component identity and capability definition.
- Hardware/readback state.
- Desired or commanded state.
- One-time command request.
- Command definition/catalog metadata.
- Execution result and progress event.
- Chamber/equipment snapshot.
- Recipe parameter, process value, alarm, interlock, and history record.
- Wire DTO, persistence schema, and UI view model.

Do not use one class as long-lived state, command payload, execution service, and UI metadata at the same time.

### 2. Define domain vocabulary and stable identity

For each component define:

- Equipment/chamber/component identity.
- Device type and supported capabilities.
- Engineering units, range, precision, and enum semantics.
- Read/write ownership.
- Interlock and availability conditions.
- Lifecycle and configuration source.

Use domain names such as valve position, RF power, flow setpoint, process value, or readback rather than generic numeric slots when the meaning is stable.

### 3. Assign authority and temporal semantics

Distinguish:

- `Actual` / `Readback`: last authoritative hardware observation.
- `Desired`: software target, not proof of device acceptance.
- `Commanded`: value sent in a specific attempt.
- `SetPoint (SP)`: control target reported or accepted by the controller.
- `Process Value (PV)`: measured process result.
- `Pending`: reconciliation is incomplete.
- `Error`: the command/readback relationship failed or remains uncertain.
- `Stale/Quality`: observation age or confidence is outside the acceptable contract.

GUI must not directly overwrite Actual. A successful transport write must not update Actual unless the device contract explicitly defines write acknowledgement as authoritative state.

### 4. Design command models by risk and complexity

Choose deliberately:

1. **Simple envelope plus nullable payload** — acceptable for a small stable command set when receiver-side validation is mandatory.
2. **Envelope plus typed/discriminated payload** — use when payload shape varies materially or cross-process compatibility matters.
3. **Dedicated command types and handlers** — use for high-risk, complex, versioned, or authorization-sensitive operations.

Every command defines:

- Target identity.
- Command type and payload type.
- Value range/enum/unit.
- Preconditions, permission, interlock, and idempotency.
- Timeout, cancellation, result, and correlation.
- Schema/protocol version.

Do not treat `CommandId` plus unrelated default-valued fields as a valid union.

### 5. Use inheritance, composition, interfaces, and generics by semantic role

- **Inheritance — is-a:** stable identity/classification relationship.
- **Composition — has-a:** component owns a state or capability object.
- **Interface capability — can-do:** generic UI, executor, polling, recipe binding, or tests need to operate by supported capability.
- **Generic — same pattern, different type:** state/reconciliation structure repeats across bool, numeric, enum, or value objects.

Ask whether a future base-class behavior applies to every subtype. If not, do not inherit merely to reuse fields.

`Signal<T>` or equivalent is appropriate for writable/readback values that share reconciliation semantics. Do not force immutable identity, pure telemetry, alarms, or complex workflow state into the same generic wrapper without a demonstrated common contract.

### 6. Define command catalog and metadata-driven UI

A command/capability catalog may define:

- Command identity and display label.
- Payload/value type.
- Enum options, range, step, units, and validation.
- Required capability and permission.
- Grouping and presentation hints.
- Protocol/schema version.

The UI uses catalog metadata to generate or bind controls. The executor remains authoritative for capability, permission, range, interlock, and current-state validation.

Do not branch UI behavior on concrete class names when the real rule is a capability. Do not put hardware execution logic in the catalog or view model.

### 7. Model command/readback reconciliation

Define the state transition for each writable signal:

1. Command accepted or rejected.
2. Desired/commanded value and attempt recorded.
3. Pending begins.
4. Transport/device write occurs.
5. Polling/callback updates Actual/readback.
6. Consistency rule completes Pending or records timeout/mismatch.
7. Late readback or reconnect reconciles uncertain state.

Specify concurrency when multiple commands target the same signal: replace, queue, reject, supersede, or version by attempt.

### 8. Govern snapshots and configuration

A snapshot defines:

- Snapshot identity/time and source node.
- Component identity and capability/schema version.
- Actual/readback timestamp, quality, and stale threshold.
- Desired/pending/error projection if intentionally included.
- Serialization compatibility and unknown-field behavior.

Configuration defines component composition and binding; it is not the live hardware state. Validate references, capability compatibility, IO bindings, units, ranges, defaults, interlocks, and migration before activation.

### 9. Verify the model

Test:

- Invalid command/payload combinations.
- Unsupported capability.
- Out-of-range or wrong-unit values.
- Write success followed by readback mismatch.
- Polling delay, stale state, disconnect, and restart.
- Two overlapping commands for one signal.
- Snapshot version compatibility.
- Config referencing missing or incompatible IO.
- Metadata-driven UI and executor using the same catalog contract.

## Common mistakes and red flags

- “RF and Valve both have OnOff, so RF inherits Valve.”
- “The GUI changed the value, therefore Actual can be updated immediately.”
- “Null means unused, so CommandId/payload validation is unnecessary.”
- “Every repeated field belongs in a base class.”
- “Every value should be wrapped in Signal<T>.”
- “The generated UI is the command authority.”
- “Configuration and snapshot are interchangeable because both serialize.”
- “Polling will eventually fix inconsistent command state without an explicit reconciliation model.”

## Skill composition

- Use `equipment-control-architecture` when sequence, shared resources, interlocks, deployment, events, or distributed recovery dominate.
- Use `framework-design` when turning the model into a reusable multi-product platform.
- Use `application-client-server-architecture` for generic API, authorization, persistence, and transport concerns.
- Use `code-review` for concrete command, polling, serialization, concurrency, or validation defects.
- Use `document-governance` when converting the model into controlled specifications or training material.

## Required output

1. Domain vocabulary and identity
2. Model-purpose and lifecycle map
3. Authority and temporal semantics
4. State/readback and reconciliation model
5. Command contract and payload strategy
6. Capability, composition, inheritance, and generic decisions
7. Catalog and metadata-driven UI contract
8. Snapshot/configuration schema and compatibility
9. Validation cases, risks, and rejected abstractions
