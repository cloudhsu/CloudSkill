# Equipment Control Platform Evidence

## Evidence status

- **Document-verified:** private architecture and engineering-training material supplied by the user.
- **Public-sanitization rule:** this evidence record intentionally omits company/product names, customer information, dates, detailed topology, proprietary protocol values, schedules, and hardware identifiers.
- **Scope:** the evidence supports generalized capability claims; it does not make every historical design choice a current normative preference.

## Verified capability areas

The supplied material demonstrates practical architecture work involving:

- Separation of workflow/sequence intent from equipment/device execution.
- Event-oriented command progress, completion, fault, correlation, retry, and recovery considerations.
- Distributed FrontEnd, coordination, and chamber/device responsibilities across process and IPC boundaries.
- Config-driven component composition and metadata-driven UI reduction of repetitive update code.
- Equipment state and command separation, including Actual, Desired, Pending, Error, polling, and readback reconciliation.
- Capability-oriented modeling using inheritance, composition, interfaces, and generics according to semantic role.
- Local, simulated, and remote implementations under a shared contract.
- Incremental migration through prototype, simulated deployment, process/network separation, and real-equipment validation checkpoints.
- Architecture boundaries aligned with project, UI/UX, device, system/platform, and internal-tool responsibilities.

## Generalized pressures extracted into skills

- Physical, runtime, network, and responsibility diagrams answer different questions.
- Shared physical resources require explicit arbitration even when each wafer has an independent workflow instance.
- Transport acknowledgement is not the same as physical completion or readback consistency.
- Configuration is executable architecture and requires schema, validation, versioning, migration, and rollback.
- Automatic UI is a projection of catalog/capability metadata, not the command or safety authority.
- Logical separation, process separation, and machine separation should be validated independently.
- Capability and deployment roadmaps should be linked but not collapsed into a single undifferentiated schedule.

## CloudSkill ownership

- `equipment-control-architecture` owns sequence/service, topology, shared resources, interlocks, distributed deployment, configuration governance, and recovery.
- `equipment-domain-modeling` owns state, command, readback, capabilities, snapshots, command catalogs, and metadata-driven UI models.
- Existing framework, refactoring, process, quality, documentation, and client/server skills remain companion owners for their respective concerns.
