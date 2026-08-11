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

## Controlled external execution

For reusable CLI or MCP-style operations, select a narrow capability from one
versioned registry. The model supplies only contract-valid business arguments;
the host owns executable selection, root and secret resolution, authority, and
process environment. Never turn the adapter layer into model-authored shell.

Persist a stable action and idempotency identity before mutation. A timeout,
disconnect, or malformed response is `UNCERTAIN` when external completion
cannot be disproved. Reconcile with the external authoritative system before
retry. The adapter reports evidence but cannot expand authority, revise the
lifecycle plan, or select its next attempt.

Keep raw logs and large artifacts outside model context. Return bounded
summaries, hashes, artifact references, observed effects, and redacted
diagnostics. Deterministic no-change paths should end with zero model calls.
