# Sequence, Equipment Service, and Event Contract

## Responsibility split

Sequence owns process intent, path, decision, step state, hold/abort/recovery policy, and process completion. Equipment Service owns device execution, protocol, local safety checks, readback, normalized progress, and device recovery evidence.

## Lifecycle

A long-running command normally needs explicit states:

- Requested: intent created and validated by caller.
- Accepted: target owns the request or queue entry.
- InProgress: physical or device execution started.
- Completed: contract-specific completion evidence exists.
- Faulted: failure code, severity, retry safety, and recovery hint are known.
- Cancelled: cancellation was accepted; physical stop semantics are explicit.
- TimedOut: observer stopped waiting; final physical outcome may still be unknown.
- Reconciled: a late result or readback resolved the uncertain outcome.

## Correlation fields

Use stable identity appropriate to the operation:

- EventId / CommandId.
- CorrelationId.
- WaferId, LotId, SequenceId, StepId.
- ResourceId and target component.
- RequestId and AttemptId.
- Protocol/schema/capability version.

## Failure rules

- Retry only when duplicate execution is safe or detectable.
- A timeout does not prove non-execution.
- Late completion must be correlated and reconciled, not discarded blindly.
- Ordering must be defined per resource or workflow, not assumed globally.
- The authoritative resource manager arbitrates shared equipment.
- Interlock authority remains near the physical action even if process policy also checks it.
