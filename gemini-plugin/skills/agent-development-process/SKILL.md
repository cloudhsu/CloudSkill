---
name: agent-development-process
description: Use when building or improving an AI-agent product whose task contract, autonomy, tools, context, memory, orchestration, evaluation, guardrails, release, or operations must be designed.
---

# AI-agent System Development Process

This skill governs the product engineering of an AI agent or agentic system. For repository rules controlling Codex or other coding agents, use `coding-agent-project-governance`.


Follow `references/agent-lifecycle.md`.

Also read when relevant:

- `references/evaluation-strategy.md`
- `references/tool-and-state-design.md`
- `references/security-and-governance.md`
- `references/coding-agent-workflow.md`

Use the templates in `assets/`.

## Workflow

### 1. Define the task contract

Specify:

- Users and stakeholders.
- Business/engineering outcome.
- Inputs and trust boundaries.
- Output schema.
- Completion condition.
- Non-goals.
- Allowed and prohibited actions.
- Escalation conditions.
- Autonomy level.
- Cost and latency budget.

Distinguish the short-lived chat session from the durable Agent role this
contract defines: the session ends, the role, permissions, state, evidence,
and human accountability do not. Treat every new session as an onboarding
event that reconstructs work from controlled sources (task contract, status
record, evidence store) rather than from private chat memory that the next
session or model cannot see. Define who/what holds authority for task status,
document revision, tool-call trace, ownership, approval, and recovery path,
and keep planned, implemented, verified, released, and field status as
separate fields rather than one collapsed label. Before a resumed session
performs a side effect, reconcile it against the current state of that
minimum handoff package and escalate rather than guess when authority,
version, owner, approval, or recovery evidence is missing -- an inherited
transcript is not proof that permissions, prior approval, or an external
write's result carried over.

### 2. Define risks and controls

Classify:

- Wrong-answer risk.
- Wrong-action risk.
- Data/security risk.
- Operational interruption.
- Duplicate or irreversible action.
- External communication.
- Safety or compliance impact.
- Unverified platform/vendor capability risk — an architecture decision that
  quietly assumes an undocumented behavior of the host platform, framework, or
  vendor product.

Define approval points and safe failure behavior.

For any decision that depends on a specific platform or vendor capability (for
example, whether one installed component preloads or shares state with another
at runtime), verify it against authoritative documentation or a direct test
*before* finalizing the decision — not after other work has already been built
on top of the assumption. If it cannot be confirmed, say so explicitly and
default to the smaller, more reversible structure until it is.

### 3. Design evaluations before optimization

Create representative cases:

- Normal.
- Boundary.
- Ambiguous.
- Missing context.
- Tool failure.
- Adversarial/untrusted input.
- Duplicate execution.
- Interrupted/restarted workflow.
- Regression from known failures.

Define metrics and release thresholds.

### 4. Design the harness

The harness includes:

- Instructions.
- Context assembly and retrieval.
- Model selection/routing.
- Tool contracts and permissions.
- State and memory.
- Orchestration.
- Guardrails.
- Output validation.
- Traces.
- Evals.
- Runtime limits.

Do not attribute every failure to the model.

### 5. Build a minimum vertical slice

Implement one end-to-end valuable path with:

- Realistic input.
- Bounded tool use.
- Typed outputs.
- Reviewable traces.
- Failure handling.
- Evaluation evidence.

### 6. Iterate using evidence

For each failure:

1. Preserve trace.
2. Classify cause.
3. Add or update an evaluation.
4. Change the smallest responsible harness component.
5. Run targeted tests.
6. Run regression.
7. Record decision.
8. Release through the defined gate.

### 7. Harden and release

Review:

- Authorization.
- Prompt injection.
- Untrusted data.
- Idempotency.
- Retry and timeout.
- State recovery.
- Cost/rate limits.
- Monitoring.
- Human override.
- Rollback/disable.
- Model/version changes.

### 8. Operate and improve

Use production traces and feedback to create repeatable evaluation evidence. Do not close a recurring issue only by changing prompt text or a memory note when it has one fixed answer — fix the harness component that owns it (`references/tool-and-state-design.md`).

## Required Output

1. Agent task contract
2. Autonomy and risk classification
3. Architecture/harness
4. Tool and state contracts
5. Evaluation plan
6. Minimum vertical slice
7. Hardening controls
8. Release gate
9. Operational metrics
10. Improvement loop
