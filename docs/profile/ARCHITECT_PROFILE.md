# Software and System Architect Profile

## Identity

The user is a hands-on software and system architect whose work spans product architecture, framework/engine design, Client/Server applications, cross-platform native systems, industrial control, deployment, quality governance, and engineering-process design.

The recurring capability is establishing system boundaries, authoritative state, contracts, lifecycle ownership, failure behavior, verification evidence, and controlled evolution across different technology domains.

## Evidence levels

- **Source-verified:** reviewed source and executable tests.
- **Repository-verified:** public or supplied repository/history inspected, but not necessarily rebuilt end to end.
- **Document-verified:** detailed controlled specifications.
- **User-stated:** supplied by the user without source verification in this repository.

Historical source demonstrates capability; it does not automatically define current implementation preference.

## Capability matrix

| Capability | Bento system | CloudBox | Qt component/tool suites | Equipment systems |
|---|---|---|---|---|
| Frontend architecture | Source-verified | Engine UI/components | Repository-verified | Current practice |
| Backend/application services | Source-verified | Not primary | Tool services and component hosts | Current practice |
| Client/Server and API contracts | Source-verified | Native service boundaries | Repository-verified utility/network components | Current practice |
| Data, transaction, migration, history | Source-verified | Resource/save state | Logging/configuration/history utilities | Recipe/history/state |
| Cross-platform native architecture | Deployment targets | Repository-verified | Repository-verified Qt/OpenCV/Designer suites | Windows/IPC focus |
| Rendering and engine lifecycle | Not primary | Repository-verified | Custom paint, Qt Charts, Qt3D, camera/video lifecycle | Analogies only |
| Device/hardware abstraction | Not primary | Platform adapters | Camera/OpenCV and native integration | Current practice |
| Recovery and lifecycle | Persistence recovery | App/resource lifecycle | Capture, plug-in and QObject ownership evidence | Current practice |
| Deployment and operations | Source-verified | Multi-platform builds | qmake/deployment plug-ins; modernization required | Current practice |
| Safe incremental refactoring | Source-verified | Historical evolution | Duplicate-source and compatibility migration case | Current practice |
| Quality/process governance | Source-verified | Historical release evidence | Characterization/build-matrix needs identified | Current practice |

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
- `../evidence/QT_COMPONENT_SUITE.md`
