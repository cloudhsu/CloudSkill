# Architecture Review Checklist

## Responsibility

- Is each module's purpose expressible in one precise sentence?
- Is policy separated from mechanism where the separation is useful?
- Are orchestration and execution responsibilities distinguishable?
- Is there duplicated ownership of the same business or runtime state?

## State

- What is the source of truth?
- Is state transient, persisted, derived, cached, or externally authoritative?
- Can two actors write it?
- What ordering guarantees exist?
- What happens after restart?
- What happens after an incomplete command?
- Is reconciliation defined?

## Commands and Side Effects

- Is the command accepted, queued, executing, completed, failed, cancelled, or unknown?
- Are retries safe?
- Is idempotency required?
- Can duplicate delivery occur?
- Can completion arrive after timeout?
- Is correlation identity preserved across layers?

## Failure and Recovery

- Communication loss.
- Process crash.
- Machine restart.
- Partial database write.
- Version mismatch.
- Device state divergence.
- Duplicate command.
- Delayed or out-of-order event.
- Configuration corruption.
- Operator intervention during automatic recovery.

## Boundaries

- Compile-time boundary.
- Process boundary.
- Machine boundary.
- Network boundary.
- Trust boundary.
- Deployment boundary.
- Team ownership boundary.
- Product variation boundary.
- Platform or hardware boundary.

## Maintainability

- Can the primary behavior be traced without excessive indirection?
- Are names aligned with domain language?
- Are extension points explicit?
- Are obsolete compatibility paths visible?
- Can junior engineers identify the correct modification location?
- Can tests prove behavior rather than implementation shape?
