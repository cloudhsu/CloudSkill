---
name: cross-platform-native-architecture
description: Design or review cross-platform native software, Qt tools and Designer plug-ins, OpenGL 2D engines, platform layers, rendering loops, input, resources, hardware integration, build systems, packaging, and legacy Qt/qmake-to-CMake or Qt 5-to-Qt 6 modernization. Do not use for ordinary browser-only frontend architecture.
---

# Cross-platform Native Architecture

Read:

- `references/platform-boundary-principles.md`
- `references/opengl-engine-checklist.md`
- `references/qt-tool-checklist.md`
- `references/qt-component-modernization.md` when the repository contains legacy Qt widgets, Designer plug-ins, duplicated component sources, qmake coupling, or a Qt-version migration.

Use:

- `assets/platform-capability-matrix.template.md` when platform differences are material.
- `assets/qt-component-modernization-plan.template.md` for a legacy Qt component-suite migration.

## Workflow

### 1. Define supported platforms and products

Record:

- Operating systems.
- CPU/ABI.
- Graphics/API requirements.
- Device/hardware interfaces.
- Windowing and input systems.
- Packaging and store/deployment channels.
- Supported Qt/native dependency versions.
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

For Qt components also specify QObject parent ownership, worker-thread affinity, cancellation, queued/direct connection assumptions, and plug-in unload behavior.

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

### 7. Modernize legacy Qt component suites safely

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

### 8. Build and release

Define:

- Toolchains.
- Dependency versions.
- Build matrix.
- ABI/public contract.
- Asset pipeline.
- Signing.
- Packaging.
- Designer plug-in discovery and deployment.
- Automated tests.
- Device/platform test matrix.
- Rollback and compatibility.

## Skill composition

- Use `$framework-design` when reusable product-line boundaries and extension contracts are the primary design problem.
- Use `$safe-incremental-refactoring` when the main task is moving responsibility between duplicate/legacy implementations without changing behavior.
- Use `$code-review` for specific correctness, lifetime, concurrency, or failure defects.
- Keep this skill as the owner of Qt/platform/build/ABI/Designer and native lifecycle constraints.

## Output Format

1. Platform/product scope
2. Capability and compatibility matrix
3. Current source/build/plug-in authority map
4. Portable core, runtime libraries, design-time adapters, and platform layers
5. Lifecycle/resource/thread ownership
6. Build, dependency, ABI, packaging, and Designer deployment matrix
7. Incremental migration slices and characterization evidence
8. Performance and quality scenarios
9. Risks, rejected abstractions, rollback, and stop conditions

## Engine Routing

Use this skill for general Qt/native application and platform architecture.

When the primary problem is a director/scene model, update-render loop, rendering backend, texture/resource lifecycle, game actions/events, or engine platform adapters, use `$cross-platform-engine-architecture`.
