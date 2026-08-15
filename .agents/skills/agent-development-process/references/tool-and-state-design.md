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

## Fixing a Gap: Harness Component vs. Memory

When a discovered gap has one fixed, repeatable answer (a required step that must
always happen the same way — a follow-up action, a validation, a notification),
fix it in the harness component that owns it (instructions, a tool contract, a
workflow script, a CI gate) so it structurally cannot be silently skipped again.
Do not rely on a memory note, a reminder, or a background monitor as the primary
fix — those depend on being recalled or triggered at the right moment, and the
same class of gap can recur silently in exactly the same way. Reserve
memory/state for judgment calls whose correct answer genuinely changes over time
and has no fixed procedure a harness component could enforce. See SKILL.md Step 8.
