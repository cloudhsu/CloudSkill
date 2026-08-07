# Software and System Architect Profile

## Identity

The user is a hands-on software and system architect whose experience spans product architecture, framework and engine design, frontend/backend systems, Client/Server systems, cross-platform native development, industrial control, deployment, quality governance, and engineering-process design.

Do not reduce this identity to the user's current semiconductor-equipment domain. Do not reduce it to framework architecture alone.

The recurring capability is:

> Establishing system boundaries, authoritative state, contracts, lifecycle ownership, failure behavior, verification evidence, and controlled evolution across different technology and product domains.

## Evidence Classification

Use these confidence levels when reasoning about experience:

- **Source-verified:** directly supported by reviewed source code and executable tests.
- **Repository-verified:** supported by a public repository and its history, but not rebuilt in the current environment.
- **Document-verified:** supported by detailed specifications and controlled project documents.
- **User-stated:** supplied by the user but not independently verified from source in this pack.

Never convert a user-stated or historical fact into a present-day coding preference without additional evidence.

## Source-verified Full-stack and Client/Server Architecture

The reviewed lunch-ordering system demonstrates practical end-to-end responsibility for:

- Employee and administration frontend architecture.
- A Node.js HTTP server and API surface.
- Server-authoritative business rules.
- Authentication, session management, RBAC, denial audit, and password policy.
- Application services, repositories, transaction boundaries, and compatibility façades.
- SQLite through `sql.js`, whole-file persistence, backup, integrity checks, and recovery behavior.
- Historical snapshots that survive master-record deletion.
- Additive migration, schema-version gates, old-database compatibility, and fail-closed future-version handling.
- Responsive desktop/mobile behavior.
- Windows and Synology NAS build/deployment concerns.
- Version, release, rollback, test-evidence, and coding-agent governance.

This is architecture and implementation evidence, not only requirement-writing evidence.

## Repository-verified Cross-platform OpenGL 2D Engine

The public CloudBox repository demonstrates a cross-platform framework/game-engine implementation for iOS, Android, and Win32 using a portable native core and OpenGL/OpenGL ES-era platform integration.

Demonstrated concerns include:

- Director and scene lifecycle.
- Action, event, view, component, layout, and resource systems.
- Rendering abstraction and OpenGL backend.
- Texture pooling and reconstruction.
- Touch/input, orientation, Retina/display adaptation.
- Background/foreground and Android resume behavior.
- Audio, dialog, motion, store/IAP, social, and native platform services.
- JNI/Java integration on Android.
- Objective-C++ and native integration on iOS.
- Win32 integration and build variants.

Treat this as historical architecture evidence. Do not infer that raw pointers, global singletons, fixed-function OpenGL, macros, or the original build system are the user's current preferred implementation style.

## User-stated Qt Cross-platform IC Tool Architecture

The user reports practical Qt-based IC production and validation tool experience across Windows, Linux, and Android.

Relevant capability areas include:

- Cross-platform GUI/application frameworks.
- Hardware and communication abstraction.
- Platform-independent policy versus native implementation.
- Product/customer variation.
- Long-lived diagnostic and production-tool maintenance.
- Build, packaging, deployment, and platform-specific behavior.

This area is user-stated unless a corresponding source repository is supplied.

## Current Equipment and Industrial-control Architecture

Current work includes:

- Equipment-control frameworks.
- Command and state modeling.
- Recipe/process flow.
- Device and industrial communication.
- Recovery and operator intervention.
- Deployment, remote update, HA, and distributed-control considerations.
- Field-service and operational constraints.

Do not copy game-engine or web-system patterns into equipment control without validating authority, timing, safety, recovery, and physical-side-effect semantics.

## Demonstrated Architecture Style

The source evidence shows a pragmatic style:

1. Preserve externally visible behavior before structural refactoring.
2. Establish tests and fault-injection seams before moving responsibility.
3. Extract pure policy first.
4. Restrict repository capability instead of passing a powerful database object.
5. Keep transaction ownership at the application-service/use-case boundary.
6. Preserve compatibility through a façade during migration.
7. Split high-risk command flows into independently reviewable slices.
8. Make migration additive and reversible where practical.
9. Treat deployment topology and persistence limits as architecture.
10. Report tests and environmental limits truthfully.

## Architecture Capabilities

The user's practical capability spans:

- Frontend architecture.
- Backend and application-service architecture.
- Client/Server architecture.
- API and protocol contracts.
- Data, transaction, migration, and history design.
- Cross-platform native architecture.
- Framework and engine architecture.
- Rendering, resource, and application lifecycle.
- Device/hardware abstraction.
- Safe brownfield refactoring.
- Operational and release architecture.
- ISO/IEC 25010 quality governance.
- Waterfall, iterative, Agile, XP, and hybrid process tailoring.
- Coding-agent and AI-agent engineering governance.
