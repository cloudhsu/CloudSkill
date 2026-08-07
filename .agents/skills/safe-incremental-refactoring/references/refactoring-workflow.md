# Refactoring Workflow

## Characterization First

Capture what the system does, including undesirable behavior that callers may depend on.

Useful evidence:

- Public method list.
- API status/error contracts.
- Database state before/after.
- Audit/event order.
- Snapshot semantics.
- Version/health output.
- UI selectors or content contracts.
- Deployment artifact structure.

## Smallest Coherent Slice

A good slice:

- Moves one responsibility.
- Has one clear owner.
- Keeps the system runnable.
- Has focused tests.
- Can be reverted independently.
- Does not require broad simultaneous edits.

A bad slice:

- Renames everything.
- Introduces multiple patterns.
- Changes behavior and schema.
- Rewrites API/UI and persistence together.
- Has no intermediate runnable state.

## Refactoring Sequence Example

```text
God Class
  → pure policy modules
  → query/command capability ports
  → read repositories
  → read/query services
  → low-risk commands
  → high-risk transaction services
  → migration components
  → transport/UI decomposition
```

Use this only as a candidate sequence. The real sequence must follow system risk and dependency shape.
