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

## Compact Extraction Decision

Choose the seam and test shape from the pressure being isolated. Several rows
may apply; when they conflict, preserve the higher-authority boundary and split
the extraction into smaller slices.

| Pressure | Extraction seam | Test shape | Dependency/bootstrap rule | Boundary that stays authoritative |
| --- | --- | --- | --- | --- |
| Pure calculation or normalization | Pure function or value object | Input/output characterization and boundary values | No I/O dependency | Calling use case retains orchestration |
| Existing monkeypatch, callback, or fault injection | Stable method/port at the observed substitution point | Old/new path comparison plus injected failure | Inject the narrow collaborator; do not construct it at import time | Existing lifecycle and failure owner |
| Expensive or externally connected dependency | Factory or lazy capability port | Construct policy without I/O; assert first-use and failure behavior separately | Lazy creation with explicit close/retry owner | Composition root owns creation and lifecycle |
| Authentication or authorization precedes policy | Authenticated identity or least-capability authorization context | Negative authorization before policy invocation plus allowed-path equivalence | Do not pass session, request, or privileged façade unless required | Transport/application security boundary retains authentication; domain/application owner retains consequential authorization policy |
| Transactional write | Command or unit-of-work port | Ordering, rollback, duplicate, late-failure and commit tests | Transaction owner injects the narrow command capability | Existing transaction owner until a separate migration proves transfer |

Do not preserve every incidental internal symbol merely because one test reaches
it. Preserve a seam when it carries compatibility, substitution, diagnosis, or
fault-injection value, and replace it only after equivalent evidence exists.
