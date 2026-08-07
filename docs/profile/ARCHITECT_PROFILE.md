# Software and System Architect Profile

## Identity

The user is a hands-on software and system architect whose work spans product architecture, framework/engine design, Client/Server applications, cross-platform native systems, industrial control, deployment, quality governance, and engineering-process design.

The recurring capability is establishing system boundaries, authoritative state, contracts, lifecycle ownership, failure behavior, verification evidence, and controlled evolution across different technology domains.

## Evidence levels

- **Source-verified:** reviewed source and executable tests.
- **Repository-verified:** public repository/history inspected, but not necessarily rebuilt.
- **Document-verified:** detailed controlled specifications.
- **User-stated:** supplied by the user without source verification in this repository.

Historical source demonstrates capability; it does not automatically define current implementation preference.

## Capability matrix

| Capability | Bento system | CloudBox | Qt IC tools | Equipment systems |
|---|---|---|---|---|
| Frontend architecture | Source-verified | Engine UI/components | User-stated | Current practice |
| Backend/application services | Source-verified | Not primary | Tool services | Current practice |
| Client/Server and API contracts | Source-verified | Native service boundaries | User-stated | Current practice |
| Data, transaction, migration, history | Source-verified | Resource/save state | User-stated | Recipe/history/state |
| Cross-platform native architecture | Deployment targets | Repository-verified | User-stated | Windows/IPC focus |
| Rendering and engine lifecycle | Not primary | Repository-verified | Not primary | Analogies only |
| Device/hardware abstraction | Not primary | Platform adapters | User-stated | Current practice |
| Recovery and lifecycle | Persistence recovery | App/resource lifecycle | User-stated | Current practice |
| Deployment and operations | Source-verified | Multi-platform builds | User-stated | Current practice |
| Safe incremental refactoring | Source-verified | Historical evolution | User-stated | Current practice |
| Quality/process governance | Source-verified | Historical release evidence | User-stated | Current practice |

## Demonstrated working style

- Preserve externally visible behavior before structural refactoring.
- Establish tests and fault-injection seams before moving high-risk responsibility.
- Extract pure policy and use-case boundaries incrementally.
- Restrict component capability instead of passing powerful infrastructure objects.
- Keep transaction and state ownership visible.
- Preserve compatibility through controlled façades during migration.
- Treat deployment topology, recovery, and persistence limits as architecture.
- Report verification and environmental limitations truthfully.

## Domain interpretation

Do not force patterns across domains without validating lifecycle, authority, latency, failure consequences, deployment, consistency, user/operator interaction, and physical-side-effect risk.

Detailed evidence:

- `../evidence/BENTO_SYSTEM.md`
- `../evidence/CLOUDBOX_ENGINE.md`
