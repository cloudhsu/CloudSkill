---
name: cross-platform-native-architecture
description: Design or review cross-platform native software, Qt tools, OpenGL 2D engines, platform layers, rendering loops, input, resources, hardware integration, build systems, and deployment across Windows, Linux, Android, or iOS. Do not use for ordinary browser-only frontend architecture.
---

# Cross-platform Native Architecture

Read:

- `references/platform-boundary-principles.md`
- `references/opengl-engine-checklist.md`
- `references/qt-tool-checklist.md`

Use `assets/platform-capability-matrix.template.md` when platform differences are material.

## Workflow

### 1. Define supported platforms and products

Record:

- Operating systems.
- CPU/ABI.
- Graphics/API requirements.
- Device/hardware interfaces.
- Windowing and input systems.
- Packaging and store/deployment channels.
- Supported versions.
- Performance targets.

### 2. Build a capability matrix

For each platform identify:

- Available capability.
- Semantic differences.
- Lifecycle differences.
- Thread-affinity constraints.
- Permission/security model.
- File-system and path behavior.
- Packaging/deployment constraints.
- Diagnostics and crash evidence.

Do not hide a meaningful semantic difference behind a falsely uniform API.

### 3. Separate portable core from platform mechanisms

Candidates for portable core:

- Domain rules.
- Scene/game logic.
- Math and geometry.
- Resource metadata.
- Protocol parsing.
- Application state.
- Testable policies.

Candidates for platform layer:

- Window/surface/context creation.
- App lifecycle.
- Input and sensors.
- File/resource access.
- Thread integration.
- Native UI bridge.
- Hardware/device transport.
- Logging/crash reporting.
- Packaging/update.

### 4. Define lifecycle and ownership

For graphics/native resources specify:

- Creation thread/context.
- Owner.
- Sharing.
- Destruction order.
- Suspend/resume.
- Surface/context loss.
- Device loss.
- Reload/reconstruction.
- Background/foreground transitions.

### 5. Design performance-critical loops

For an engine or real-time UI define:

- Update/render cadence.
- Fixed versus variable timestep.
- Frame budget.
- Work queues.
- Resource upload.
- Synchronization.
- Allocation policy.
- Profiling evidence.
- Degraded behavior.

### 6. Design extension and product variation

Choose among:

- Compile-time platform modules.
- Runtime capability selection.
- Plug-ins.
- Adapters.
- Configuration.
- Product-specific modules.

Require a real variation or lifecycle boundary before introducing an abstraction.

### 7. Build and release

Define:

- Toolchains.
- Dependency versions.
- Build matrix.
- ABI/public contract.
- Asset pipeline.
- Signing.
- Packaging.
- Automated tests.
- Device/platform test matrix.
- Rollback and compatibility.

## Output Format

1. Platform/product scope
2. Capability matrix
3. Portable core and platform layers
4. Lifecycle/resource ownership
5. Rendering/input/device architecture
6. Build and deployment matrix
7. Performance and quality scenarios
8. Risks, rejected abstractions, and migration

## Engine Routing

Use this skill for general Qt/native application and platform architecture.

When the primary problem is a director/scene model, update-render loop, rendering backend, texture/resource lifecycle, game actions/events, or engine platform adapters, use `$cross-platform-engine-architecture`.
