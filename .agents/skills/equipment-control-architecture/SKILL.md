---
name: equipment-control-architecture
description: Use when equipment software coordinates material flow, pump/vent or chamber readiness, wafer/lot sequences, robots, recipes, interlocks, shared physical resources, simulation, or distributed control across equipment modules.
---

# Equipment Control Architecture

## Core principle

Separate process intent from device execution without losing physical-state authority, safety, resource ownership, process readiness, or restart recovery. A distributed topology is not complete until normal, partial-failure, and reconstruction behavior are explicit.

**REQUIRED COMPANION:** Use `semiconductor-equipment-domain-knowledge` when the physical purpose, vacuum/process state, component capability, or completion evidence is uncertain.

Read:

- `references/physical-runtime-and-network-topology.md`
- `references/sequence-service-event-contract.md`
- `references/config-driven-equipment-platform.md`
- `references/equipment-platform-modernization.md`
- `references/physical-process-readiness-and-interlocks.md`

Use:

- `assets/EQUIPMENT_CONTROL_ARCHITECTURE.template.md`
- `assets/EQUIPMENT_EVENT_CONTRACT.template.md`

## Workflow

### 1. Define physical process, material path, and product scope

Identify:

- Carriers, wafers, lots, load ports, aligners, loadlocks, transfer chambers, process chambers, robots, recipes, sensors, actuators, utilities, and factory systems.
- Material path, atmosphere/vacuum/high-vacuum boundaries, contamination isolation, and process-ready conditions.
- Physical invariants, interlocks, exclusion zones, material-location rules, and irreversible operations.
- Supported products and chamber variants.
- Current and target hardware, operating systems, field buses, IPCs, PLCs, and deployment nodes.

Do not begin with process names or network boxes before the physical work, environmental transitions, and safety constraints are understood.

### 2. Separate four architecture views

Maintain distinct but traceable views:

1. **Physical equipment topology** — EFEM/Main Frame/chamber modules, motion paths, IO, material flow, vacuum regions, utilities, and safety zones.
2. **Runtime/process topology** — executables, services, threads, state machines, recipe engines, and ownership.
3. **Communication topology** — clients, servers, sessions, protocols, connection direction, and message flow.
4. **Responsibility topology** — component owners, team boundaries, support ownership, and release authority.

Do not infer runtime or communication ownership from a hardware drawing alone. Do not treat team names as software interfaces or UI pages as physical modules.

### 3. Assign authoritative state and policy

For each concern identify one authority and any projections or caches:

- Hardware readback, sensor validity, and IO state.
- Desired or commanded state.
- Wafer identity, location, occupancy, and custody.
- Sequence step, recipe phase, and process readiness.
- Pressure/environment state and boundary-open permission.
- Resource reservation and queue ownership.
- Recipe execution and parameter acceptance.
- Interlock and safety decision.
- Component/configuration schema.
- Alarm, event log, wafer history, and audit evidence.

GUI state is a projection. A command-send success is not hardware-state confirmation. Device or chamber control must revalidate safety-sensitive commands even when the UI or Sequence already checked them.

### 4. Model location, environment, readiness, and boundary state together

A safe material move depends on more than source and destination names. Define:

- Authoritative source/destination occupancy.
- Robot/blade position and reservation.
- Loadlock/chamber pressure domain and gauge validity.
- Door/slit/gate actual position.
- Pressure equalization or isolation conditions.
- Process/chamber availability and contamination boundary.
- Post-move location confirmation and rollback/recovery state.

Pump-down and vent complete on authoritative physical criteria, not elapsed time alone. Opening a vacuum boundary requires current pressure, valve, path, and interlock evidence. After restart or reconnect, reconstruct these facts before accepting new movement.

### 5. Separate Sequence from Equipment Service

The Sequence or workflow layer owns:

- What must happen next.
- Wafer/lot path, recipe/process phase, conditions, retry policy, hold, abort, and recovery intent.
- Process-level state and completion criteria.

The Equipment Service layer owns:

- How a device or physical operation is executed.
- Hardware/protocol details, local interlocks, timing, retries allowed by the device contract, and readback.
- Normalized readiness, progress, completion, fault, and capability reporting.

Sequence must not reach through the service into a concrete driver. Equipment Service must not silently embed product workflow policy. A process phase should complete on defined physical/readback evidence, not merely because a command returned or a timer expired.

Use direct calls for bounded same-process operations only when synchronous semantics, failure propagation, and testability remain explicit. Use an asynchronous command/event contract when work is long-running, cancellable, remote, restartable, queued, or produces late completion.

### 6. Define command and event lifecycle

Specify states such as:

`Requested -> Accepted -> InProgress -> PhysicalConditionReached -> Completed | Faulted | Cancelled | TimedOut -> Reconciled`

Define at minimum:

- Event/command identity.
- Wafer, lot, sequence, step, recipe phase, resource, request, and attempt correlation.
- Source, target, timestamp, payload, result, and protocol/schema version.
- Ordering scope.
- Duplicate handling and idempotency key.
- Retry ownership and retry-safe operations.
- Cancellation semantics.
- Late completion after timeout or failover.
- Replay, retention, and trace requirements.

Timeout is an observer decision, not proof that the physical operation did not complete. Transport acknowledgement is not proof of valve position, wafer location, pressure readiness, plasma, or deposition completion.

### 7. Model shared physical resources

Independent wafer sequences still contend for shared robots, aligners, loadlocks, chambers, paths, and utilities. Define:

- Reservation owner and resource state authority.
- Queueing, priority, fairness, and starvation policy.
- Atomic acquisition for multi-resource moves.
- Deadlock avoidance or detection.
- Lease/heartbeat behavior when the owner disappears.
- Release, compensation, and operator takeover.
- Interaction with interlocks, pressure states, and equipment faults.

Do not let each sequence infer availability from a stale snapshot and issue competing commands.

### 8. Preserve Local, Simulate, and Remote semantics

All implementations must share the same externally observable contract for:

- Accepted/readiness/in-progress/completed/faulted meaning.
- Capability and version discovery.
- Timeouts, cancellation, retries, and late responses.
- State/readback ownership and sensor-quality semantics.
- Error classification and recovery hints.

Simulation may accelerate time but must not erase ordering, pressure transition, stabilization, shared-resource, disconnection, or fault behavior that the production contract requires. Record which hardware phenomena are not simulated, such as pump dynamics, gauge range transitions, plasma ignition, thermal inertia, or vendor-specific faults.

### 9. Design distributed deployment explicitly

For every IPC/process define:

- Role and authoritative state.
- Client/server direction and session owner.
- Address/port/configuration discovery.
- Startup order and partial-availability behavior.
- Heartbeat, reconnect, duplicate session, and stale connection handling.
- Protocol and capability negotiation.
- Clock/time-source assumptions.
- Backpressure and bounded queues.
- Security, privilege, and network trust boundary.
- Logs, health, version, update, and rollback.

Logical separation, process separation, and machine separation are independent decisions. Validate a process boundary on one machine before assuming multi-machine deployment is ready.

### 10. Govern config-driven composition and automatic UI

Treat configuration as executable architecture. Define:

- Stable component identity and type/capability model.
- IO binding, communication binding, engineering units, ranges, sensor quality, interlocks, recipe binding, and UI metadata.
- Schema and capability version.
- Validation, migration, defaults, provenance, and approval.
- Unknown field/type behavior.
- Configuration signing or integrity control where unsafe modification has physical consequences.
- Runtime reload policy and restart requirement.

Automatic UI must be derived from an authoritative catalog/capability model; it must not become the only command validator. Configuration may compose known capabilities but should not become an unbounded scripting language unless its execution, safety, and version model are intentionally designed.

### 11. Modernize through a deployment ladder

Use independently verifiable stages:

1. Characterize current physical and software behavior and contracts.
2. Establish source and binary authority for shared libraries/contracts.
3. Prove one end-to-end component vertical slice with simulated IO and explicit physical assumptions.
4. Prove a bounded material/vacuum transition with readiness and readback.
5. Separate responsibilities while preserving current deployment.
6. Run client/server in one machine.
7. Run multiple simulated nodes over the real protocol.
8. Pilot one real equipment path with controlled rollback.
9. Expand product, chamber, and process coverage only after evidence exists.

Each checkpoint needs observable acceptance, artifact versions, known exclusions, rollback, and a decision to continue. Do not combine common-library extraction, product convergence, process split, network semantics, and real-hardware migration in one release.

### 12. Verify and operate

Require evidence for:

- Command/readback reconciliation.
- Duplicate, delayed, lost, and out-of-order messages.
- Disconnect during motion, pump/vent, stabilization, power-up, or recipe execution.
- Process and IPC restart.
- Resource-owner loss and reservation recovery.
- Interlock or readiness changes during execution.
- Invalid/stale/out-of-range sensor state.
- Config/schema mismatch.
- Local/simulate/remote semantic parity.
- Deployment/update rollback.
- Trace continuity from wafer/step/recipe phase to device command, sensor readback, and completion decision.

## Minimum distributed ownership/recovery deliverable

For a focused distributed ownership and recovery request, explicitly provide:

1. One authority for chamber physical/readback state, material identity/location/custody, shared-resource reservations, interlocks/readiness, command attempts, and recovery decisions.
2. A reconnect admission gate that blocks new work until session identity, current readback, reservations, in-flight attempts, and material state are reconciled.
3. Restart reconstruction from current hardware evidence and durable history, with conflicts marked `Unknown` or `RecoveryRequired`.
4. Failover fencing using an epoch/term, lease, fencing token, or equivalent single-writer mechanism that rejects commands from the previous or stale owner.
5. Command ID, attempt ID, idempotency/duplicate policy, timeout as observer state, cancellation, late completion, and reconciliation.
6. Fresh interlock/readiness revalidation before resuming or issuing safety-sensitive commands.
7. Concrete disconnect, restart, duplicate/out-of-order message, owner-loss/failover, late-completion, and stale-readback fault-injection scenarios.
8. Assumptions and unresolved inputs for failover topology, authority store, lease/epoch implementation, clocks, material-identification evidence, and operator recovery.

Do not invent a backup chamber, majority vote, shared state store, timeout duration, or plant-specific topology.

## Common mistakes and red flags

- “The GUI sent it successfully, so the hardware is already in that state.”
- “The pump command finished, so the chamber is at vacuum.”
- “The valve is open in the model, so adjacent pressure domains are compatible.”
- “Power is on, so plasma and deposition are confirmed.”
- “Every chamber is a client, therefore connection and session ownership are obvious.”
- “The same DLL makes distributed components compatible.”
- “Different folders plus different config files are enough instance isolation.”
- “Simulation passed, so real pump, gauge, plasma, and thermal behavior are covered.”
- “Each wafer has its own state machine, so shared-resource arbitration is unnecessary.”
- “Config-driven means no code or schema migration is required.”
- “A network split automatically improves reliability.”

## Skill composition

- Use `semiconductor-equipment-domain-knowledge` for EFEM/Main Frame/chamber roles, component purpose, vacuum/gas/thermal/power/plasma semantics, and PVD process interpretation.
- Use `equipment-domain-modeling` for component state, command payloads, Actual/Desired, capabilities, snapshots, engineering units, quality, and metadata-driven UI.
- Use `framework-design` when the shared equipment kernel and product-line extension contracts are the main concern.
- Use `application-client-server-architecture` for generic API, security, persistence, and service deployment concerns outside equipment-specific semantics.
- Use `safe-incremental-refactoring` when moving an existing equipment system through the deployment ladder.
- Use `development-process-tailoring` for roadmap, staffing, checkpoint, hardware dependency, and release-train governance.
- Use `software-quality-iso25010` to convert reliability, compatibility, maintainability, usability, performance, and security into release evidence.

## Required output

1. Physical process, material path, and scope
2. Four-view topology map
3. Authority and responsibility matrix
4. Location/environment/readiness/interlock model
5. Sequence/service boundaries
6. Command/event lifecycle and correlation contract
7. Resource model
8. Local/simulate/remote parity contract
9. Distributed deployment and recovery model
10. Configuration and automatic-UI contract
11. Modernization checkpoints
12. Verification, risks, and current-spec unknowns
