# Engine Core

## Director/Application Orchestrator

Owns:

- Startup and shutdown.
- Current/next scene.
- Deferred scene transitions.
- Update/render cadence.
- Pause/background/foreground integration.
- Top-level event flow.

Avoid making the director a global dumping ground for unrelated platform services.

## Scene and Components

Define:

- Scene lifecycle.
- Ownership of nodes/views/components.
- Attach/detach order.
- Update traversal.
- Render ordering.
- Event subscription lifetime.
- Transition cleanup.

## Actions and Events

Specify:

- Time source.
- Cancellation.
- Completion.
- Composition.
- Ownership when targets disappear.
- Reentrancy.
- Thread of dispatch.
- Queueing between platform and engine threads.
