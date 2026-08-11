# Tool and State Design

## Tool Contract

For every tool define:

- Purpose.
- Allowed caller/role.
- Input schema.
- Output schema.
- Side effects.
- Idempotency.
- Timeout.
- Retry eligibility.
- Error taxonomy.
- Audit fields.
- Version.
- Reversibility.
- Approval requirement.

## Tool Design Rules

- Prefer narrow tools over generic shell/database access.
- Validate all arguments outside the model.
- Enforce authorization in code, not only in instructions.
- Separate read, draft, and commit actions.
- Return structured errors.
- Include correlation IDs.
- Make consequential operations observable.
- Use dry-run or preview when practical.

## State Ownership

Define:

- Conversation state.
- Workflow state.
- Business/system state.
- Tool/external state.
- Memory.
- Cache.

For each state identify:

- Source of truth.
- Writer.
- Persistence.
- Consistency.
- Recovery.
- Retention.
- Privacy.
- Reconciliation.

Never assume the conversation transcript is the authoritative workflow state for consequential operations.
