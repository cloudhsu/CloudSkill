---
name: code-review
description: Use when production C, C++, C#, Qt, WinForms, WPF, framework, device-control, communication, or industrial code must be checked for correctness, concurrency, state, lifetime, recovery, maintainability, or boundary violations.
---

# Code Review

Review code as executable behavior within a system, not as isolated syntax.

Read `references/code-review-checklist.md` when the change touches state, communication, threads, devices, persistence, deployment, or framework boundaries.

## Review Order

### 1. Reconstruct behavior

Identify:

- Inputs.
- Outputs.
- State read and written.
- Side effects.
- Thread or callback context.
- Error paths.
- Lifetime and ownership.
- Callers and downstream dependencies.

### 2. Check correctness risks

Prioritize:

- Duplicate execution.
- Lost updates.
- Stale state.
- Race conditions.
- Deadlocks.
- Reentrancy.
- Unbounded retry.
- Timeout and late response.
- Partial completion.
- Resource leaks.
- Invalid lifetime.
- Integer, buffer, encoding, and boundary errors.
- Incorrect recovery after restart or disconnect.

### 3. Check architecture boundaries

Determine whether the change:

- Places domain policy in infrastructure or UI code.
- Leaks platform-specific behavior across an abstraction.
- Creates hidden dependencies.
- Duplicates state ownership.
- Adds unnecessary indirection.
- Bypasses central logging, validation, command, or recovery mechanisms.

### 4. Check maintainability

Evaluate:

- Naming and domain clarity.
- Local reasoning cost.
- Call depth.
- Cohesion.
- Testability.
- Compatibility.
- Migration impact.
- Whether a smaller change can solve the same problem.

### 5. Recommend changes

Classify findings:

- Critical: may cause unsafe behavior, data corruption, deadlock, repeated command, or unrecoverable state.
- Major: likely functional defect, operational failure, or architecture erosion.
- Moderate: maintainability or diagnostic weakness with concrete future cost.
- Minor: local clarity or consistency issue.

For each finding include:

- Evidence.
- Failure scenario.
- Impact.
- Smallest safe correction.
- Test that would prove the correction.

## Output Format

1. Review summary
2. Critical and major findings
3. Moderate findings
4. Architecture observations
5. Suggested patch sequence
6. Required tests
7. Uncertainties

Do not fabricate defects when evidence is insufficient. Mark uncertain risks explicitly.

## Persistence-model Review

Do not assume a SQL `COMMIT` is the final durable boundary.

Review the actual persistence path:

- Engine-managed durable database.
- In-memory database exported to a file.
- Remote acknowledgement.
- Event append.
- Temporary-file rename.
- Deferred flush.

Check whether process restart, save failure, or failed restoration can leave memory and durable state divergent.
