# Hybrid Lifecycle Example

## Stage 0 — Business and Feasibility

Evidence:

- Product goal.
- Major constraints.
- Risk assessment.
- Feasibility prototypes.
- Initial quality priorities.

## Stage 1 — System Baseline

Evidence:

- System boundary.
- Hardware/software responsibilities.
- Interface contracts.
- Safety and reliability assumptions.
- Verification strategy.
- Increment roadmap.

## Stage 2 — Incremental Construction

Each increment:

- Selects a vertical capability.
- Refines requirements.
- Updates design decisions.
- Implements and integrates.
- Produces automated and system evidence.
- Updates risks and operational documentation.

Use XP practices within the increment where appropriate.

## Stage 3 — System Integration

Evidence:

- Hardware/software integration.
- Fault and recovery tests.
- Performance/capacity tests.
- Compatibility matrix.
- Operator/service validation.
- Release candidate.

## Stage 4 — Release and Field Validation

Evidence:

- Deployment/upgrade/rollback.
- Release notes.
- Known limitations.
- Field telemetry.
- Incident and feedback loop.

## Stage 5 — Maintenance and Product Evolution

Use a flow-based process for defects and operational work, while larger changes re-enter an appropriate architecture and release gate.

## Controlled external-tool vertical slice

For a reusable CLI or future MCP capability, the lifecycle owner retains the
versioned plan while the adapter reports bounded execution evidence. The
adapter cannot revise the plan, expand authority, discard completed evidence,
or choose retry. An `UNCERTAIN` result enters reconciliation before retry;
changed authority or risk replans only affected future work; a broken state
authority, persistence, or recovery model returns to architecture.

Use two iterations as a default discovery shape: first establish the contract
and one end-to-end capability, then exercise interruption and reconciliation.
This is not a mandatory iteration count. Evidence-rich low-risk work may use a
shorter path, while remote mutation or uncertain external state adds gates.
