# Agent Evaluation Strategy

## Evaluation Layers

### Deterministic unit tests

Test:

- Tool adapters.
- Schema validation.
- Authorization rules.
- State transitions.
- Retry/idempotency logic.
- Parsing and formatting.

### Tool contract tests

Test:

- Input validation.
- Permission denial.
- Partial failure.
- Timeout.
- Duplicate request.
- Version mismatch.
- Rollback behavior.

### Scenario evaluations

Evaluate complete agent outcomes against representative tasks.

Measure task completion, not only textual similarity.

### Adversarial and negative evaluations

Include:

- Prompt injection.
- Conflicting instructions.
- Misleading retrieved data.
- Unauthorized request.
- Ambiguous identity.
- Missing required approval.
- High-confidence wrong completion.

### Operational evaluation

Use:

- Shadow mode.
- Human-reviewed pilot.
- Limited allowlist.
- Bounded production rollout.
- Comparison with baseline process.

## Metrics

Possible metrics:

- Task success rate.
- Correct refusal/escalation.
- False completion rate.
- Unauthorized action rate.
- Tool-call success.
- Recovery success.
- Evidence/citation completeness.
- Human correction rate.
- P95 latency.
- Cost per successful task.
- Trace completeness.

## Release Rule

Critical cases are pass/fail gates. Do not compensate for a safety or authorization failure using a high average score.
