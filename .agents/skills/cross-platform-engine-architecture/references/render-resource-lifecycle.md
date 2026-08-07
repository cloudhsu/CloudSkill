# Rendering and Resource Lifecycle

## Rendering

Decide:

- Immediate versus retained commands.
- State sorting/batching.
- Projection and logical coordinate space.
- Texture atlas strategy.
- Clipping and blending.
- Text rendering.
- Device/profile capability fallback.

## Resource State Machine

A useful conceptual state model:

```text
Asset reference
  → decoded/loaded
  → native/GPU resident
  → temporarily invalid
  → reconstructed
  → released
```

Context loss or platform resume must not be treated as a normal pointer-preserving pause.

## Performance

Track:

- Frame time.
- Draw calls.
- state changes.
- texture memory.
- allocation in frame loop.
- upload stalls.
- update/render imbalance.
