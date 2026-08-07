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
