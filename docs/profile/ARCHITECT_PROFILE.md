# Software and System Architect Profile

## Identity

The user is a hands-on software and system architect whose work spans product architecture, framework/engine design, Client/Server applications, cross-platform native and device utilities, industrial control, deployment, quality governance, product evolution, and engineering-process design.

The recurring capability is establishing system boundaries, authoritative state, contracts, lifecycle ownership, failure behavior, verification evidence, release/operational fit, and controlled evolution across different technology domains.

## Evidence levels

- **Source-verified:** reviewed source and executable tests.
- **Repository-verified:** public or supplied repository/history inspected, but not necessarily rebuilt end to end.
- **Document-verified:** detailed controlled or historical specifications/plans reviewed.
- **User-stated:** supplied by the user without source verification in this repository.

Historical source demonstrates capability; it does not automatically define current implementation preference.

## Capability matrix

| Capability | Bento system | CloudBox | Qt component/device tools | Equipment systems |
|---|---|---|---|---|
| Frontend architecture | Source-verified | Engine UI/components | Repository/document-verified Qt utilities and touch-oriented UX | Current practice |
| Backend/application services | Source-verified | Not primary | Application hosts, configuration, device inventory, protocol services | Current practice |
| Client/Server and API contracts | Source-verified | Native service boundaries | Utility/network components and native contracts | Current practice |
| Data, transaction, migration, history | Source-verified | Resource/save state | Configuration, mapping artifacts, logs, import/export, version history | Recipe/history/state |
| Cross-platform native architecture | Deployment targets | Repository-verified | Repository-verified Qt/OpenCV/Designer and touch-device suites | Windows/IPC focus |
| Rendering and engine lifecycle | Not primary | Repository-verified | Custom paint, Qt Charts/3D, camera/video and UI lifecycle | Analogies only |
| Device/hardware abstraction | Not primary | Platform adapters | Repository-verified HID/USB façade, protocol, hot plug, firmware and OS adapters | Current practice |
| Recovery and lifecycle | Persistence recovery | App/resource lifecycle | Device removal/re-enumeration, retries, restart/config reconciliation, update/installer concerns | Current practice |
| Deployment and operations | Source-verified | Multi-platform builds | qmake, installers, startup/tasks, privilege, driver/signing, logs and field support | Current practice |
| Product and requirement evolution | Source-verified delivery history | Historical evolution | Repository/document-verified specifications, release tags, customer feedback, variants and field fixes | Current practice |
| Safe incremental refactoring | Source-verified | Historical evolution | Legacy replacement, duplicate-source and compatibility migration cases | Current practice |
| Quality/process governance | Source-verified | Historical release evidence | Documented planning, specifications, release/installer evidence and governance gaps | Current practice |

## Demonstrated working style

- Start from the actual user/operational problem rather than copying a legacy UI or architecture.
- Reconstruct current behavior, environment, and build/deployment constraints before redesign.
- Preserve externally visible behavior before structural refactoring.
- Establish tests, prototypes, and fault-injection seams before moving high-risk responsibility.
- Separate protocol/transport/platform mechanisms from application policy and UI.
- Keep device, configuration, transaction, state, and release ownership visible.
- Use incremental releases and technical spikes to reduce uncertainty around OS, hardware, firmware, driver, and integration behavior.
- Treat installer, privilege, startup, compatibility, logs, rollback, and field support as architecture and completion criteria.
- Distinguish request, accepted requirement, implementation, verification, release, and field closure.
- Preserve compatibility through controlled façades during migration.
- Report verification and environmental limitations truthfully.

## Domain interpretation

Do not force patterns across domains without validating lifecycle, authority, latency, failure consequences, deployment, consistency, user/operator interaction, privilege, compatibility, and physical-side-effect risk.

Detailed evidence:

- `../evidence/BENTO_SYSTEM.md`
- `../evidence/CLOUDBOX_ENGINE.md`
- `../evidence/QT_COMPONENT_SUITE.md`
- `../evidence/SIS_TOUCH_UTILITY.md`
