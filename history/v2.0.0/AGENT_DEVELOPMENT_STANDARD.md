# AI Agent Development Process Standard

**Document type:** Engineering process standard  
**Default status:** Draft for organizational tailoring  
**Applies to:** LLM agents, coding agents, tool-using agents, workflow agents, and multi-agent systems  
**Primary concern:** Delivering measurable, reviewable, recoverable, and governable agent behavior

## 1. Purpose

This standard defines a repeatable development lifecycle for AI agents.

It treats an agent as a system composed of:

- Model behavior.
- Instructions and context.
- Tools and permissions.
- Data retrieval and memory.
- Routing and orchestration.
- Guardrails and approval policies.
- Observability and traces.
- Evaluations and release gates.
- Runtime operations and improvement mechanisms.

A successful demonstration is not sufficient evidence of production quality.

## 2. Principles

1. Start from a task contract, not from a prompt.
2. Define autonomy and irreversible-action boundaries explicitly.
3. Define representative evaluations before large-scale implementation.
4. Prefer a minimum vertical slice over a broad speculative framework.
5. Preserve traces and evidence for every failed evaluation.
6. Separate deterministic control from probabilistic judgment.
7. Make tool contracts typed, narrow, observable, and reversible where possible.
8. Require human approval where the consequence of a wrong action exceeds the approved risk threshold.
9. Measure successful task completion, not only response quality.
10. Improve through controlled changes backed by repeatable evaluations.

## 3. Lifecycle

### Phase 0 — Intake and Risk Classification

Required outputs:

- Problem statement.
- Stakeholders and affected systems.
- Expected value.
- Non-goals.
- Autonomy level.
- Data classification.
- Risk category.
- Initial release constraints.

Classify autonomy:

| Level | Description | Default control |
|---|---|---|
| A0 | Advisory response only | User validates output |
| A1 | Produces drafts or plans | Human approves before use |
| A2 | Executes tools with per-action approval | Approval before consequential actions |
| A3 | Executes bounded workflows automatically | Policy, allowlist, limits, audit log |
| A4 | Conditionally autonomous operation | Formal governance, monitoring, rollback, incident process |

A4 must not be selected merely for convenience.

### Phase 1 — Task Contract and Acceptance

Define:

- Inputs and their trust level.
- Required outputs and output schema.
- Allowed assumptions.
- Prohibited actions.
- Tool access.
- Completion conditions.
- Escalation conditions.
- Timeout and retry policy.
- Human approval points.
- Quality targets.

Create initial acceptance examples and negative examples.

### Phase 2 — Agent Architecture

Define:

- Single-agent or multi-agent topology.
- Model selection and routing criteria.
- Instruction hierarchy.
- Context assembly and retrieval.
- Tool interfaces and authorization.
- Memory scope and retention.
- State ownership.
- Error propagation.
- Recovery and restart behavior.
- Observability and trace boundaries.
- Cost and latency budget.

Use deterministic code for rules that must always hold. Do not delegate stable validation, authorization, accounting, or irreversible workflow control to probabilistic reasoning without an explicit justification.

### Phase 3 — Evaluation Design

Create an evaluation set before optimization.

Minimum coverage:

- Normal successful cases.
- Boundary cases.
- Ambiguous requests.
- Missing data.
- Tool failure.
- Partial completion.
- Conflicting instructions.
- Unsafe or unauthorized requests.
- Duplicate execution.
- Timeout and late response.
- Recovery after interruption.
- Regression cases from real failures.

Define metrics and thresholds. Examples:

- End-to-end task success rate.
- Correct tool-selection rate.
- Unauthorized-action rate.
- False completion rate.
- Recovery success rate.
- Escalation precision and recall.
- Grounding or evidence completeness.
- P50/P95 latency.
- Cost per successful task.
- Trace completeness.
- Human override rate.

### Phase 4 — Minimum Vertical Slice

Implement the smallest complete path that:

- Accepts a real input.
- Performs a bounded task.
- Uses real or contract-faithful tools.
- Produces the required output.
- Emits a reviewable trace.
- Passes a small evaluation suite.
- Can fail safely.

Do not build generalized multi-agent infrastructure before one valuable path is proven.

### Phase 5 — Implementation and Iteration

For each iteration:

1. Select failed or missing evaluation cases.
2. Identify whether the cause is instruction, context, tool, model, orchestration, data, or policy.
3. Change the smallest responsible component.
4. Re-run targeted evaluations.
5. Re-run the regression suite.
6. Record the decision and evidence.
7. Update documentation and release notes.

Do not change multiple independent components when one controlled experiment can isolate the cause.

### Phase 6 — Hardening

Required reviews:

- Tool authorization and least privilege.
- Prompt-injection and untrusted-content handling.
- Sensitive-data handling.
- Idempotency and duplicate prevention.
- Rate, cost, and resource limits.
- Timeout, retry, and circuit-breaker behavior.
- State recovery after process interruption.
- Observability and incident diagnosis.
- Model or dependency version changes.
- Human approval and override paths.
- Rollback or safe-disable mechanism.

### Phase 7 — Release Gate

A release candidate must include:

- Approved agent specification.
- Architecture and tool contracts.
- Evaluation plan and results.
- Known limitations.
- Risk register.
- Operational dashboard or monitoring plan.
- Rollback/disable procedure.
- On-call or ownership definition.
- Versioned instructions and configuration.
- Change log.

No release is approved only because average evaluation scores are high. Critical safety, authorization, or irreversible-action cases are hard gates.

### Phase 8 — Operation

Monitor:

- Task success.
- Failure clusters.
- Tool errors.
- Human corrections.
- Escalations.
- Cost and latency.
- Drift in input distribution.
- Model/version changes.
- Security or policy violations.
- Repeated work and duplicate actions.

Preserve enough trace evidence to reconstruct consequential decisions while respecting data-retention and privacy requirements.

### Phase 9 — Improvement Loop

Use this loop:

```text
Production traces
    → human/model review
    → classified failure evidence
    → new or updated evaluation cases
    → controlled harness change
    → regression validation
    → reviewed release
```

A production failure is not considered closed until the relevant expectation becomes repeatable as an evaluation, control, or monitoring rule.

## 4. Required Artifacts

| Artifact | Purpose |
|---|---|
| `AGENT_SPEC.md` | Task contract, autonomy, tools, data, quality targets |
| `AGENT_ARCHITECTURE.md` | Components, state, control flow, recovery |
| `TOOL_CONTRACTS.md` | Tool schemas, permissions, errors, idempotency |
| `AGENT_EVAL_PLAN.md` | Cases, metrics, thresholds, regression policy |
| `RISK_REGISTER.md` | Risks, controls, owners, residual risk |
| `EXEC_PLAN.md` | Living plan for complex implementation |
| `TRACE_REVIEW.md` | Failure evidence and diagnosis |
| `RELEASE_CHECKLIST.md` | Release gate and operational readiness |
| `CHANGELOG.md` | Versioned behavior and configuration changes |

Templates are provided in the `agent-development-process` skill.

## 5. Process Tailoring

This standard may be used with:

- Waterfall governance for fixed contractual milestones.
- Iterative delivery for uncertain agent behavior.
- Agile planning for incremental value delivery.
- XP engineering practices for tests, integration, refactoring, and rapid feedback.
- Hybrid hardware/software stage gates.

The agent lifecycle remains evidence-driven regardless of the management process selected.
