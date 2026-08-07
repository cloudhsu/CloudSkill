---
name: cross-platform-engine-architecture
description: Design or review a cross-platform 2D/game/graphics engine with a portable core, director/scene lifecycle, update/render loop, rendering backend, actions/events, resources, input, platform services, and iOS/Android/Windows adapters. Use for engine architecture rather than ordinary application UI.
---

# Cross-platform Engine Architecture

Read:

- `references/engine-core.md`
- `references/render-resource-lifecycle.md`
- `references/platform-adapters.md`
- `references/historical-evidence-rule.md`

Use `assets/ENGINE_CAPABILITY_MATRIX.template.md`.

## Workflow

### 1. Define engine scope

Identify:

- Supported products and platforms.
- 2D/3D boundary.
- Rendering API/backend.
- Fixed or variable timestep.
- Scene/world model.
- UI/component requirements.
- Resource types.
- Audio/input/platform services.
- Tooling and asset pipeline.
- Performance envelope.

### 2. Define the portable runtime core

Clarify ownership for:

- Director/application orchestration.
- Scene transition.
- Update and render traversal.
- Action/tween scheduling.
- Event dispatch.
- Layout and coordinate systems.
- Resource identifiers and caches.
- Component/view lifecycle.

Keep native lifecycle and OS services behind explicit platform contracts.

### 3. Define rendering abstraction

Specify:

- Draw-command or immediate API.
- Backend interface.
- Graphics context ownership.
- Texture/buffer/shader ownership.
- Batching and state changes.
- Coordinate/projection policy.
- DPI/orientation/resolution adaptation.
- Context/device-loss behavior.

Do not create an abstraction that only renames the graphics API without isolating real variation or lifecycle.

### 4. Define resource lifecycle

For every resource state:

- Source asset.
- Decoded CPU representation.
- GPU/native handle.
- Owner.
- Cache/pool.
- Reference/lifetime policy.
- Background/suspend behavior.
- Context-loss reconstruction.
- Memory-pressure release.
- Hot reload where applicable.

### 5. Define platform adapters

Possible platform capabilities:

- Application lifecycle.
- Window/surface/context.
- Touch/mouse/keyboard/controller.
- Audio.
- Dialog.
- Motion/sensors.
- Store/IAP.
- Social/service integration.
- File/user defaults.
- URL/open external app.
- Logging/crash reporting.

Document semantic differences rather than forcing lowest-common-denominator behavior.

### 6. Define threading

Specify:

- Render thread.
- Update thread.
- Platform UI thread.
- Input delivery.
- Resource upload.
- Audio callbacks.
- Cross-thread queueing.
- Shutdown ordering.

### 7. Verify

Use:

- Pure core tests.
- Scene/action/event lifecycle tests.
- Resource reconstruction tests.
- Platform adapter contract tests.
- Device lifecycle tests.
- Frame-time and memory profiling.
- Long-run suspend/resume tests.
- Packaging/build matrix.

## Output Format

1. Engine scope
2. Portable core
3. Director/scene/update-render lifecycle
4. Rendering backend
5. Resource lifecycle
6. Input/events/actions/components
7. Platform adapters
8. Threading and performance
9. Build/test matrix
10. Risks and evolution path
