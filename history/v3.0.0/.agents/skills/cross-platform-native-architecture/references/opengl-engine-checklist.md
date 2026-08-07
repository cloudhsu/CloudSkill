# OpenGL 2D Engine Checklist

## Rendering

- Context/surface lifecycle.
- Render-thread ownership.
- Fixed/variable timestep.
- Draw ordering and batching.
- State-change control.
- Texture and buffer lifetime.
- Context-loss recovery.
- Resolution, DPI, orientation, and viewport.
- Frame-time and memory targets.

## Resources

- Asset identifiers.
- Packaging differences.
- Async loading.
- Cache ownership.
- Hot reload where supported.
- Device-specific formats.
- Reconstruction after memory pressure or context loss.

## Input and Lifecycle

- Touch, mouse, keyboard, controller.
- Coordinate normalization.
- Focus and interruption.
- App suspend/resume.
- Background behavior.
- Native event-loop integration.

## Testing

- Pure math/scene tests.
- Golden rendering tests where stable.
- Platform smoke tests.
- Long-run memory/resource tests.
- Context/surface recreation.
- Performance profiling on representative devices.
