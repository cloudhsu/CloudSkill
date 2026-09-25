# Multi-agent Delivery

## Main/Integrator

- Reconstructs the task and repository.
- Assigns isolated work.
- Owns final architecture and diff.
- Resolves conflicts.
- Runs or verifies final regression.
- Produces the handoff.

## Architecture Agent

- Identifies boundaries, invariants, risk, migration, and acceptance.
- Should not produce abstract advice disconnected from existing code.

## Development Agent

- Implements only the approved slice.
- Preserves public contracts.
- Adds tests.
- Stops when the design cannot be implemented safely.

## Test Agent

- Reads requirements and diff independently.
- Tests negative, boundary, duplicate, timeout, rollback, and permission cases.
- Does not merely rerun the developer's happy path.

## Concurrency Rule

Parallelize only when tasks have:

- Separate file ownership.
- clear contracts.
- independent verification.
- low merge ambiguity.

Use worktrees/branches for concurrent writers.

## Recurring-role Persistence

When a functional role (Architecture, Development, Test, or another role
above) is expected to recur across a multi-milestone project rather than
handle one isolated task, bind one persistent agent identity to that role as
the starting default at the very first task dispatched to it -- not as an
optimization retrofitted after the project has already paid the cost of not
having it. Maintain a visible roster mapping each recurring role to its
current persistent agent identity so a new dispatch can look up whether to
resume before spawning, and so the mapping survives context resets. Do not
default to spawning a brand-new agent instance for every dispatched task
without first checking whether an existing, resumable agent already owns
that role. If a project's history shows this binding arrived late, report it
as a cost that was paid, not as a neutral learning-curve improvement.
