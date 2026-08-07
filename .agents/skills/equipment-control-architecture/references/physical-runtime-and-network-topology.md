# Physical, Runtime, Network, and Responsibility Topology

Use separate views because one diagram cannot safely answer every architecture question.

## View matrix

| View | Shows | Must not imply by itself |
|---|---|---|
| Physical | Chambers, robots, loadlocks, material paths, IO, safety zones | Process or network ownership |
| Runtime | Executables, services, state machines, threads, authoritative stores | Machine placement or connection direction |
| Network | Endpoints, sessions, protocol, message flow, ports, trust boundaries | Domain responsibility |
| Responsibility | Team/component owner, release authority, support escalation | Runtime coupling |

## Traceability questions

- Which runtime owner controls each physical resource?
- Which endpoint publishes readback and which only renders it?
- Which process survives or reconstructs state after another process restarts?
- Which protocol carries command intent, progress, completion, and snapshots?
- Which team owns the contract, implementation, deployment, and field diagnosis?

## Deployment-node checklist

For each node record role, process, machine, hardware connection, authority, dependencies, startup order, health, version, log/config path, update, rollback, and degraded mode.

Avoid ambiguous diagrams that draw many lines without direction, operation type, lifecycle, or failure semantics.
