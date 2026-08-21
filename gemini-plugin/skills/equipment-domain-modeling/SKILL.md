---
name: equipment-domain-modeling
description: Use when modeling valves, MFCs, pumps, gauges, heaters, power supplies, robots, chamber snapshots, equipment commands, hardware readback, Actual and Desired values, capabilities, engineering units, or metadata-driven UI.
---

# Equipment Domain Modeling

## Core principle

Model physical identity, authority, lifecycle, units, measurement quality, and temporal meaning before optimizing fields or inheritance. Similar fields prove a repeated capability or data pattern; they do not prove two device types have the same identity.

**REQUIRED COMPANION:** Use `semiconductor-equipment-domain-knowledge` when the component purpose, measurement range, vacuum/process meaning, or completion evidence is uncertain.

Read:

- `references/state-command-reconciliation.md`
- `references/command-catalog-and-capability-model.md`
- `references/config-and-snapshot-contracts.md`
- `references/equipment-component-state-patterns.md`

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
- Measurement sample and quality.
- Chamber/equipment snapshot.
- Readiness, alarm, interlock, and fault state.
- Recipe parameter, controller setpoint, process value, and history record.
- Wire DTO, persistence schema, and UI view model.

Do not use one class as long-lived state, command payload, execution service, measurement contract, and UI metadata at the same time.

### 2. Define domain vocabulary and stable identity

For each component define:

- Equipment/chamber/component identity.
- Physical purpose and supported capabilities.
- Component family: actuator, sensor, regulator, measurement, motion, pump, thermal utility, or process-energy source.
- Engineering units, command range, measurement range, precision, enum semantics, and mode.
- Read/write ownership.
- Readiness, interlock, availability, and fault conditions.
- Lifecycle, communication binding, and configuration source.

Use domain names such as valve position, gas flow, chamber pressure, RF/DC power, pump speed, temperature setpoint, process value, or readback rather than generic numeric slots when the meaning is stable. Communication protocol does not define domain identity.

### 3. Assign authority, measurement quality, and temporal semantics

Distinguish:

- `Actual` / `Readback`: last authoritative hardware observation.
- `Desired`: software target, not proof of device acceptance.
- `Commanded`: value sent in a specific attempt.
- `SetPoint (SP)`: control target reported or accepted by the controller.
- `Process Value (PV)`: measured process result.
- `Pending`: reconciliation is incomplete.
- `Error`: the command/readback relationship failed or remains uncertain.
- `Quality/Validity`: measurement is usable, out of range, transitioning, faulted, or unknown.
- `Stale`: observation age exceeds the contract.
- `Ready`: a derived predicate with named dependencies, not a manually edited Boolean.

A measurement model should normally carry value, unit, timestamp, quality/status, source/range, and applicable uncertainty or alarm state. A pressure value without a valid sensing range may be unusable even when numeric.

GUI must not directly overwrite Actual. A successful transport write must not update Actual unless the device contract explicitly defines write acknowledgement as authoritative state.

### 4. Select a component-state pattern deliberately

Common patterns include:

- **Binary actuator:** desired command, actual position/state, transitioning, fail state, interlock.
- **Discrete sensor:** actual state, polarity, debounce/quality, timestamp, alarm.
- **Analog regulator:** desired setpoint, accepted/readback setpoint, process value, units, range, mode, stabilization.
- **Measurement:** value, units, range/source, validity, timestamp, alarm; often no Desired value.
- **Motion:** command/target, actual position, homed/in-position, motion state, path/resource, fault.
- **Pump/utility lifecycle:** command, mode, ready, speed/temperature/pressure dependencies, cooldown/regeneration, fault.
- **Process-energy source:** enable, desired/actual power, mode, ramp, forward/reflected or vendor status, cooling/match/plasma-related evidence.

These are capability patterns, not a mandate for one base class. `Signal<T>` is useful when values share writable/readback reconciliation; it is usually inappropriate for immutable identity, pure telemetry, complex pump lifecycle, alarms, or workflow state without a demonstrated common contract.

### 5. Design command models by risk and complexity

Choose deliberately:

1. **Simple envelope plus nullable payload** — acceptable for a small stable command set when receiver-side validation is mandatory.
2. **Envelope plus typed/discriminated payload** — use when payload shape varies materially or cross-process compatibility matters.
3. **Dedicated command types and handlers** — use for high-risk, complex, versioned, or authorization-sensitive operations.

Every command defines:

- Target identity.
- Command type and payload type.
- Value range/enum/unit/mode.
- Preconditions, permission, interlock, and idempotency.
- Timeout, cancellation, result, and correlation.
- Schema/protocol version.
- Expected readback or physical completion evidence.

Do not treat `CommandId` plus unrelated default-valued fields as a valid union. `StartPump`, `OpenSlitValve`, `MoveRobot`, and `EnablePower` require different lifecycle and completion semantics even if each begins as an “On” command.

### 6. Use inheritance, composition, interfaces, and generics by semantic role

- **Inheritance — is-a:** stable identity/classification relationship.
- **Composition — has-a:** component owns a state or capability object.
- **Interface capability — can-do:** generic UI, executor, polling, recipe binding, or tests need to operate by supported capability.
- **Generic — same pattern, different type:** state/reconciliation structure repeats across bool, numeric, enum, or value objects.

Ask whether a future base-class behavior applies to every subtype. If not, do not inherit merely to reuse fields.

### 7. Define command catalog and metadata-driven UI

A command/capability catalog may define:

- Command identity and display label.
- Payload/value type.
- Enum options, command range, step, engineering units, and validation.
- Required capability, mode, permission, and readiness.
- Grouping and presentation hints.
- Protocol/schema version.

The UI uses catalog metadata to generate or bind controls. The executor remains authoritative for capability, permission, units, range, mode, interlock, readiness, and current-state validation.

Do not branch UI behavior on concrete class names when the real rule is a capability. Do not put hardware execution logic in the catalog or view model.

### 8. Model command/readback reconciliation

Define the state transition for each writable signal or operation:

1. Command accepted or rejected.
2. Desired/commanded value and attempt recorded.
3. Pending/in-progress begins.
4. Transport/controller/device action occurs.
5. Polling/callback updates Actual/readback/measurement.
6. Consistency or readiness rule completes Pending or records timeout/mismatch.
7. Late readback or reconnect reconciles uncertain state.

Specify concurrency when multiple commands target the same signal: replace, queue, reject, supersede, or version by attempt. Stabilization may require a tolerance and time window rather than one equal-value sample.

### 9. Govern snapshots and configuration

A snapshot defines:

- Snapshot identity/time and source node.
- Component identity and capability/schema version.
- Actual/readback timestamp, unit, range/source, quality, and stale threshold.
- Desired/pending/error projection if intentionally included.
- Derived readiness and its dependency version if exposed.
- Serialization compatibility and unknown-field behavior.

Configuration defines component composition and binding; it is not the live hardware state. Validate references, capability compatibility, IO/communication bindings, units, command and measurement ranges, defaults, interlocks, and migration before activation.

### 10. Verify the model

Test:

- Invalid command/payload combinations.
- Unsupported capability or wrong operating mode.
- Out-of-range, wrong-unit, or wrong-gas-line values.
- Write success followed by readback mismatch.
- Measurement out of valid range or invalid quality.
- Polling delay, stale state, disconnect, and restart.
- Two overlapping commands for one signal.
- Stabilization timeout or oscillation.
- Snapshot version compatibility.
- Config referencing missing or incompatible IO.
- Metadata-driven UI and executor using the same catalog contract.

## Component-contract ownership boundary

When the main deliverable is the component-level `Commanded`, `Desired`, `Pending`, `Actual/Readback`, ACK, physical completion, timeout, late readback, and reconciliation contract, this Skill remains primary.

- Use it alone when Sequence/Equipment Service responsibility, shared-resource policy, deployment, and recovery topology are explicitly out of scope.
- Add `equipment-control-architecture` only when cross-layer timeout, late-completion, interlock, retry, shared-resource, reconnect, restart, or recovery responsibility is separately requested.
- Do not add `semiconductor-equipment-domain-knowledge` when physical purpose and completion evidence are already supplied.
- In a combined request, define the component contract first, then allocate cross-layer responsibility.

## Common mistakes and red flags

- “RF and Valve both have OnOff, so RF inherits Valve.”
- “The GUI changed the value, therefore Actual can be updated immediately.”
- “The pressure is a double, so range and gauge status do not belong in the model.”
- “MFC setpoint and actual flow are the same property.”
- “Every repeated field belongs in a base class.”
- “Every value should be wrapped in Signal<T>.”
- “All pumps can use one OnOff model.”
- “The generated UI is the command authority.”
- “Configuration and snapshot are interchangeable because both serialize.”
- “Polling will eventually fix inconsistent command state without an explicit reconciliation model.”

## Skill composition

- Use `semiconductor-equipment-domain-knowledge` for equipment topology, component purpose, vacuum/gas/thermal/power/plasma semantics, and process interpretation.
- Use `equipment-control-architecture` when sequence, material flow, shared resources, interlocks, deployment, events, or distributed recovery dominate.
- Use `framework-design` when turning the model into a reusable multi-product platform.
- Use `application-client-server-architecture` for generic API, authorization, persistence, and transport concerns.
- Use `code-review` for concrete command, polling, serialization, concurrency, or validation defects.
- Use `document-governance` when converting the model into controlled specifications or training material.

## Required output

1. Domain vocabulary, physical purpose, and identity
2. Model-purpose and lifecycle map
3. Authority, units, quality, and temporal semantics
4. Component-state pattern decisions
5. State/readback and reconciliation model
6. Command contract and payload strategy
7. Capability, composition, inheritance, and generic decisions
8. Catalog and metadata-driven UI contract
9. Snapshot/configuration schema and compatibility
10. Validation cases, risks, and product-specific unknowns
