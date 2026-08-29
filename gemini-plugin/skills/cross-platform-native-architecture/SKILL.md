---
name: cross-platform-native-architecture
description: Use when a native or Qt system spans OS-specific lifecycle, HID/USB devices, firmware update, privileged integration, packaging, Designer plug-ins, or Qt build/version migration boundaries.
---

# Cross-platform Native Architecture

When a missing material architecture decision would change the design, follow
`../architecture-review/references/architecture-decision-elicitation.md`.

Read:

- `references/platform-boundary-principles.md`
- `references/opengl-engine-checklist.md`
- `references/qt-tool-checklist.md`
- `references/qt-component-modernization.md` when the repository contains legacy Qt widgets, Designer plug-ins, duplicated component sources, qmake coupling, or a Qt-version migration.
- `references/touch-device-utility-architecture.md` when a native utility owns device discovery, HID/USB commands, monitor/input mapping, privileged OS functions, firmware update, or installer/startup behavior.

Use:

- `assets/platform-capability-matrix.template.md` when platform differences are material.
- `assets/qt-component-modernization-plan.template.md` for a legacy Qt component-suite migration.

## Workflow

### 1. Define supported platforms and products

Record:

- Operating systems and supported versions.
- CPU/ABI and driver architecture.
- Graphics/API requirements.
- Device/hardware interfaces and protocol versions.
- Windowing, display topology, input, and raw-input mechanisms.
- Privilege, signing, service, scheduled-task, or startup requirements.
- Packaging, upgrade, rollback, and deployment channels.
- Supported Qt/native dependency versions.
- Product/customer variants and performance targets.

### 2. Build a capability matrix

For each platform and product variant identify:

- Available capability.
- Semantic differences.
- Lifecycle differences.
- Thread-affinity constraints.
- Permission/security model.
- File-system and path behavior.
- Driver and device-discovery behavior.
- Packaging/deployment constraints.
- Diagnostics and crash evidence.

Do not hide a meaningful semantic difference behind a falsely uniform API.

### 3. Separate portable core from platform mechanisms

Candidates for portable core:

- Domain and device-mode rules.
- Protocol framing, parsing, validation, and command construction.
- Math, geometry, mapping, and coordinate conversion.
- Configuration schema and normalization.
- Firmware metadata and update policy.
- Application state and testable policies.

Candidates for platform layer:

- Window/surface/context creation.
- App lifecycle, tray, single-instance, startup, and session behavior.
- Input, global hooks, raw input, touch, keyboard, and sensors.
- Display enumeration, rotation, calibration, and mapping.
- File/resource access and public/private configuration paths.
- Thread integration and native UI bridge.
- Hardware transport, HID/USB access, driver calls, and hot-plug notification.
- Logging/crash reporting, installer, signing, update, and rollback.

### 4. Define authority, lifecycle, and ownership

For graphics/native resources specify:

- Creation thread/context.
- Owner and authoritative state.
- Sharing and synchronization.
- Destruction order.
- Suspend/resume and login/session changes.
- Surface/context/device loss.
- Reload/reconstruction and hot-plug reconciliation.
- Background/foreground transitions.

For Qt components also specify QObject parent ownership, worker-thread affinity, cancellation, queued/direct connection assumptions, and plug-in unload behavior.

For device utilities explicitly identify authority for:

- Discovered-device inventory and selected device.
- Device enabled/disabled state.
- Configuration loaded from disk versus state read from firmware.
- Command execution, retries, timeouts, and late responses.
- Firmware-update session and recovery after interruption.
- Display/input mapping and topology changes.

### 5. Design the device and OS integration pipeline

Use an explicit path such as:

`UI/use case -> application host -> protocol/command service -> device façade -> platform transport -> OS/driver/device`

Keep reverse notifications explicit:

`OS hot-plug/session/display event -> platform adapter -> authoritative inventory/state -> application event -> UI projection`

Check:

- Partial read/write and report-length validation.
- Device removal during I/O.
- Duplicate or late notifications.
- Retry limits and idempotency.
- Privilege denial and secure-desktop/login-screen constraints.
- Firmware reset/re-enumeration.
- Multiple devices with different capabilities.
- Configuration reconciliation after restart.
- Operator-safe degraded behavior.

### 6. Design performance-critical loops

For an engine, polling device, gesture detector, or real-time UI define:

- Update/poll/render cadence.
- Fixed versus variable timestep.
- UI and I/O latency budget.
- Work queues and cancellation.
- Synchronization and backpressure.
- Allocation policy.
- Profiling evidence.
- Degraded behavior and stop conditions.

### 7. Design extension and product variation

Choose among:

- Compile-time platform modules.
- Runtime capability selection.
- Plug-ins and adapters.
- Configuration and feature policy.
- Product-specific UI/composition modules.

Separate shared device/protocol capability from customer/product presentation. Require a real variation, ownership, deployment, or lifecycle boundary before introducing an abstraction. Do not let preprocessor flags or copied project trees become the only product-line model.

### 8. Modernize legacy Qt component suites safely

Before changing implementation, inventory:

- Active, duplicate, backup, example, generated, and abandoned sources.
- QWidget class names, `Q_PROPERTY`, signals/slots, Designer IID, `domXml()`, `includeFile()`, resource URLs, binary/install paths, ABI consumers, and `.ui` files.
- qmake `.pro/.pri` rules, absolute paths, hidden deployment scripts, compiler settings, and dependency versions.
- Runtime widget code versus design-time adapter code.
- Optional Qt/OpenCV/Eigen/Charts/Multimedia/3D feature families.

Then migrate in independent slices:

1. Establish characterization/component-gallery and focused core tests.
2. Select one authoritative copy of each capability.
3. Split runtime libraries from thin Designer adapters while retaining the existing build.
4. Add CMake beside qmake and compare artifacts.
5. Establish a known Qt 5 baseline when it is still a compatibility target.
6. Add Qt 6 support feature family by feature family.
7. Retire legacy names/builds only after downstream form, source, ABI, package, and rollback evidence exists.

Do not combine source deduplication, build-system replacement, Qt-version migration, API renaming, and behavior changes in one patch.

### 9. Build, release, and operate

Define:

- Toolchains and dependency versions.
- Build and product-variant matrix.
- ABI/public/protocol/configuration contracts.
- Driver architecture, signing, and test-signing policy.
- Asset, firmware, and localization pipeline.
- Installer upgrade/downgrade and silent-install behavior.
- Startup, scheduled task, service, tray, and single-instance behavior.
- Log/configuration locations and support evidence.
- Designer plug-in discovery and deployment.
- Automated tests and device/platform test matrix.
- Rollback, compatibility, and field-support procedure.

## Skill composition

- Use `$framework-design` when reusable device, command, protocol, or product-line boundaries are the primary problem.
- Use `$safe-incremental-refactoring` when moving responsibility from a legacy utility or duplicate implementation without changing behavior.
- Use `$development-process-tailoring` for requirement evolution, release trains, customer feedback, variants, and project controls.
- Use `$document-governance` for versioned specifications, decisions, release notes, and traceability.
- Use `$software-quality-iso25010` to define usability, reliability, compatibility, security, maintainability, and release evidence.
- Use `$code-review` for specific correctness, lifetime, concurrency, protocol, or failure defects.

## Output Format

1. Platform/product/device scope
2. Capability and compatibility matrix
3. Current source/build/protocol/configuration authority map
4. Portable core, application hosts, device/protocol services, platform adapters, and UI composition
5. State/lifecycle/resource/thread ownership
6. Hot-plug, I/O, firmware-update, privilege, display/input, and recovery behavior
7. Build, dependency, ABI, driver, packaging, installer, and deployment matrix
8. Incremental migration slices and characterization evidence
9. Performance and quality scenarios
10. Risks, rejected abstractions, rollback, and stop conditions

## Engine Routing

Use this skill for general Qt/native application, hardware utility, and platform architecture.

When the primary problem is a director/scene model, update-render loop, rendering backend, texture/resource lifecycle, game actions/events, or engine platform adapters, use a private companion capability.
