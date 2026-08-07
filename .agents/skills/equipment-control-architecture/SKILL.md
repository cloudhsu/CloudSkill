---
name: equipment-control-architecture
description: Use when equipment software coordinates wafer, lot, chamber, robot, aligner, recipe, interlock, shared physical resources, simulation, or local and remote control boundaries.
---

# Equipment Control Architecture

## Core principle

Separate process intent from device execution without losing physical-state authority, safety, resource ownership, or restart recovery. A distributed topology is not complete until normal, partial-failure, and reconstruction behavior are explicit.

Read:

- `references/physical-runtime-and-network-topology.md`
- `references/sequence-service-event-contract.md`
- `references/config-driven-equipment-platform.md`
- `references/equipment-platform-modernization.md`

Use:

- `assets/EQUIPMENT_CONTROL_ARCHITECTURE.template.md`
- `assets/EQUIPMENT_EVENT_CONTRACT.template.md`

## Workflow

### 1. Define the physical process and product scope

Identify:

- Wafers, lots, carriers, chambers, loadlocks, robots, aligners, recipes, sensors, actuators, and external factory systems.
- Physical invariants, interlocks, exclusion zones, material-location rules, and irreversible operations.
- Supported products and chamber variants.
- Current and target hardware, operating systems, field buses, IPCs, PLCs, and deployment nodes.

Do not begin with process names or network boxes before the physical work and safety constraints are understood.

### 2. Separate four architecture views

Maintain distinct but traceable views:

1. **Physical equipment topology** — modules, motion paths, IO, material flow, and safety zones.
2. **Runtime/process topology** — executables, services, threads, state machines, and ownership.
3. **Communication topology** — clients, servers, sessions, protocols, connection direction, and message flow.
4. **Responsibility topology** — component owners, team boundaries, support ownership, and release authority.

Do not infer runtime or communication ownership from a hardware drawing alone. Do not treat team names as software interfaces.

### 3. Assign authoritative state and policy

For each concern identify one authority and any projections or caches:

- Hardware readback and IO state.
- Desired or commanded state.
- Sequence step and wafer location.
- Resource reservation and queue ownership.
- Recipe execution and parameter acceptance.
- Interlock and safety decision.
- Component/configuration schema.
- Alarm, event log, wafer history, and audit evidence.

GUI state is a projection. A command-send success is not hardware-state confirmation. Device or chamber control must revalidate safety-sensitive commands even when the UI already checked them.

### 4. Separate Sequence from Equipment Service

The Sequence or workflow layer owns:

- What must happen next.
- Wafer/lot path, conditions, retry policy, hold, abort, and recovery intent.
- Process-level state and completion criteria.

The Equipment Service layer owns:

- How a device action is executed.
- Hardware/protocol details, local interlocks, timing, retries allowed by the device contract, and readback.
- Normalized progress, completion, fault, and capability reporting.

Sequence must not reach through the service into a concrete driver. Equipment Service must not silently embed product workflow policy.

Use direct calls for bounded same-process operations only when synchronous semantics, failure propagation, and testability remain explicit. Use an asynchronous command/event contract when work is long-running, cancellable, remote, restartable, queued, or produces late completion.

### 5. Define command and event lifecycle

Specify states such as:

`Requested -> Accepted -> InProgress -> Completed | Faulted | Cancelled | TimedOut -> Reconciled`

Define at minimum:

- Event/command identity.
- Wafer, lot, sequence, step, resource, request, and attempt correlation.
- Source, target, timestamp, payload, result, and protocol/schema version.
- Ordering scope.
- Duplicate handling and idempotency key.
- Retry ownership and retry-safe operations.
- Cancellation semantics.
- Late completion after timeout or failover.
- Replay, retention, and trace requirements.

Timeout is an observer decision, not proof that the physical operation did not complete.

### 6. Model shared physical resources

Independent wafer sequences still contend for shared robots, aligners, loadlocks, chambers, and paths. Define:

- Reservation owner and resource state authority.
- Queueing, priority, fairness, and starvation policy.
- Atomic acquisition for multi-resource moves.
- Deadlock avoidance or detection.
- Lease/heartbeat behavior when the owner disappears.
- Release, compensation, and operator takeover.
- Interaction with interlocks and equipment faults.

Do not let each sequence infer availability from a stale snapshot and issue competing commands.

### 7. Preserve Local, Simulate, and Remote semantics

All implementations must share the same externally observable contract for:

- Accepted/completed/faulted meaning.
- Capability and version discovery.
- Timeouts, cancellation, retries, and late responses.
- State/readback ownership.
- Error classification and recovery hints.

Simulation may accelerate time but must not erase ordering, resource, disconnection, or fault behavior that the production contract requires. Record which hardware phenomena are not simulated.

### 8. Design distributed deployment explicitly

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

### 9. Govern config-driven composition and automatic UI

Treat configuration as executable architecture. Define:

- Stable component identity and type/capability model.
- IO binding, engineering units, ranges, interlocks, recipe binding, and UI metadata.
- Schema and capability version.
- Validation, migration, defaults, provenance, and approval.
- Unknown field/type behavior.
- Configuration signing or integrity control where unsafe modification has physical consequences.
- Runtime reload policy and restart requirement.

Automatic UI must be derived from an authoritative catalog/capability model; it must not become the only command validator. Configuration may compose known capabilities but should not become an unbounded scripting language unless its execution, safety, and version model are intentionally designed.

### 10. Modernize through a deployment ladder

Use independently verifiable stages:

1. Characterize current behavior and contracts.
2. Establish source and binary authority for shared libraries/contracts.
3. Prove one end-to-end component vertical slice with simulated IO.
4. Separate responsibilities while preserving current deployment.
5. Run client/server in one machine.
6. Run multiple simulated nodes over the real protocol.
7. Pilot one real equipment path.
8. Expand product and chamber coverage only after evidence and rollback exist.

Each checkpoint needs observable acceptance, artifact versions, known exclusions, rollback, and a decision to continue. Do not combine common-library extraction, product convergence, process split, network semantics, and real-hardware migration in one release.

### 11. Verify and operate

Require evidence for:

- Command/readback reconciliation.
- Duplicate, delayed, lost, and out-of-order messages.
- Disconnect during motion or recipe execution.
- Process and IPC restart.
- Resource-owner loss and reservation recovery.
- Interlock changes during execution.
- Config/schema mismatch.
- Local/simulate/remote semantic parity.
- Deployment/update rollback.
- Trace continuity from wafer/step to device command and readback.

## Common mistakes and red flags

- “The GUI sent it successfully, so the hardware is already in that state.”
- “Every chamber is a client, therefore connection and session ownership are obvious.”
- “The same DLL makes distributed components compatible.”
- “Different folders plus different config files are enough instance isolation.”
- “Simulation passed, so the real device timing and failure modes are covered.”
- “Each wafer has its own state machine, so shared-resource arbitration is unnecessary.”
- “Config-driven means no code or schema migration is required.”
- “A network split automatically improves reliability.”

## Skill composition

- Use `equipment-domain-modeling` for component state, command payloads, Actual/Desired, capabilities, snapshots, and metadata-driven UI.
- Use `framework-design` when the shared equipment kernel and product-line extension contracts are the main concern.
- Use `application-client-server-architecture` for generic API, security, persistence, and service deployment concerns outside equipment-specific semantics.
- Use `safe-incremental-refactoring` when moving an existing equipment system through the deployment ladder.
- Use `development-process-tailoring` for roadmap, staffing, checkpoint, hardware dependency, and release-train governance.
- Use `software-quality-iso25010` to convert reliability, compatibility, maintainability, usability, performance, and security into release evidence.

## Required output

1. Physical process and scope
2. Four-view topology map
3. Authority and responsibility matrix
4. Sequence/service boundaries
5. Command/event lifecycle and correlation contract
6. Resource and interlock model
7. Local/simulate/remote parity contract
8. Distributed deployment and recovery model
9. Configuration and automatic-UI contract
10. Modernization ladder and checkpoints
11. Verification, observability, rollback, and open risks
