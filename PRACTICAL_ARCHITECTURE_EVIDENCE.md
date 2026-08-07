# Practical Architecture Evidence Map

This document gives agents concrete evidence for the architect profile. It is not a résumé and should not be turned into marketing language.

## Internal Client/Server Web System

The reviewed project materials demonstrate an end-to-end architecture operating model for a small but production-relevant internal ordering system.

### Architecture evidence

- A browser-based employee client and a separate administration client.
- A single Node.js server providing UI resources and HTTP APIs.
- SQLite persistence through an in-memory SQL engine with explicit save/recovery behavior.
- Domain/application services extracted from a compatibility façade.
- Repository capabilities intentionally restricted from transaction, save, and close ownership.
- Server-side authority for price, store, deadline, balance, authorization, and order state.
- Explicit order-state transitions.
- One transaction for coupled order, balance, processing-state, event, and audit changes.
- Historical snapshots preserved after master records are removed.
- Additive and repeatable migrations with compatibility checks.
- Single-writer deployment constraints stated as part of architecture, not left as an operational accident.

### Frontend evidence

- Employee and administrator information architectures.
- Desktop and narrow mobile layouts.
- Mobile-specific cards and controls instead of merely shrinking desktop tables.
- Server validation retained even when the client also validates.
- Session ownership enforced by the server rather than accepting client-selected identities.
- Safe dynamic rendering and controlled dialog behavior.

### Operational evidence

- Windows and Synology NAS deployment targets.
- Reverse-proxy HTTPS guidance.
- Health endpoint and version consistency.
- Backup, integrity checking, logs, retention, and recovery.
- Release package, hash, changelog, requirement history, test report, and rollback discipline.
- Explicit statements of tests not performed, avoiding fabricated evidence.

### Engineering-governance evidence

- Repository `AGENTS.md`.
- Agent specification and domain invariants.
- Architecture/file map.
- API specification.
- Development standard.
- Risk-based model/agent routing.
- Main/architecture/development/test agent role separation.
- Git/worktree, commit, version, release, and documentation rules.

## Cross-platform OpenGL 2D Engine

The architect has practical experience implementing a 2D engine on iOS, Android, and Windows using OpenGL.

This supports reasoning about:

- Portable core versus native platform layer.
- Render-loop ownership.
- Graphics-context and resource lifecycle.
- Input and application lifecycle differences.
- Performance-sensitive architecture.
- Cross-platform build and deployment boundaries.

## Qt-based Cross-platform IC Tools

The architect has practical experience building Qt-based IC production/validation tools across Windows, Linux, and Android.

This supports reasoning about:

- Cross-platform GUI frameworks.
- Native and hardware integration.
- Device/transport abstraction.
- Platform-specific implementation behind stable contracts.
- Product-line and customer variation.
- Long-lived diagnostic and production-tool maintenance.

## Equipment Software

The current equipment domain adds:

- Real-world state reconciliation.
- Commands with physical side effects.
- Process recipes and equipment state.
- Fault recovery and operator intervention.
- Industrial protocol and deployment constraints.

## Interpretation Rule

These domains are evidence of broad architecture practice. Do not force one domain's patterns into another without validating:

- Lifecycle.
- authority.
- latency.
- failure consequences.
- deployment model.
- consistency requirements.
- user/operator interaction.
