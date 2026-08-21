---
name: architecture-review
description: Use when comparing or assessing architecture decisions, module boundaries, state ownership, distributed design, platform/domain separation, failure behavior, or migration risk.
---

# Architecture Review

Perform an architecture review that is grounded in the actual domain and operational constraints rather than in methodology compliance.

## Required Inputs

Use available repository files, diagrams, requirements, issue descriptions, logs, and user explanations. Do not invent missing operational constraints.

When critical information is absent, list the uncertainty and continue with explicit assumptions unless the missing item prevents a responsible recommendation.

Read these references when relevant:

- `references/architect-context.md`
- `references/review-checklist.md`
- `references/architecture-decision-elicitation.md` when a missing material
  decision can change the review conclusion.

## Workflow

### 1. Define the decision

State:

- What problem is being solved.
- What decision must be made.
- What is outside the current scope.
- Which constraints are fixed and which are negotiable.

### 2. Reconstruct the current architecture

Identify:

- Entry points.
- Major modules and responsibilities.
- State owners.
- Data and command flow.
- External side effects.
- Runtime and deployment boundaries.
- Recovery and restart behavior.
- Cross-platform or hardware-dependent boundaries.

Do not infer architecture solely from folder names.

### 3. Identify the real pressure

Classify the architectural pressure:

- Product variation.
- Platform variation.
- Hardware variation.
- Runtime isolation.
- Deployment independence.
- Reliability or high availability.
- Team ownership.
- Testability.
- Performance or latency.
- Maintainability.
- Legacy migration.

Reject abstractions that do not correspond to a real variation or failure boundary.

### 4. Evaluate options

Provide at least two viable options when alternatives exist.

For each option evaluate:

- Responsibility clarity.
- State ownership.
- Coupling and dependency direction.
- Runtime call depth and traceability.
- Failure containment.
- Recovery complexity.
- Test strategy.
- Deployment and versioning impact.
- Cross-platform impact.
- Migration cost.
- Junior-engineer comprehension cost.
- AI-assisted maintenance implications, when relevant.

### 5. Recommend

Give:

- Preferred option.
- Why it fits the current constraints.
- What it intentionally does not solve.
- Risks and mitigations.
- Smallest practical migration sequence.
- Conditions that would justify revisiting the decision.

### 6. Validate

Define concrete validation:

- Architecture tests or dependency rules.
- Unit/integration/system tests.
- Failure-injection cases.
- Performance measurements.
- Operational logs and metrics.
- Acceptance criteria.

## Output Format

Use this structure:

1. Decision summary
2. Current architecture reconstruction
3. Key constraints and assumptions
4. Option comparison
5. Recommendation
6. Migration plan
7. Risks and validation
8. Open questions

## Review depth

Default to every step above. On an explicit, one-time user request for a lighter pass (a low-stakes or exploratory task), skip only the steps the user names and record which steps were skipped in the output header. Never reduce depth silently, by default, or for a safety-, authority-, or release-significant decision without the user's explicit override for that specific run.

## Non-Negotiable Review Rules

- Do not equate more layers with better architecture.
- Do not equate fewer files with simpler behavior.
- Do not recommend a pattern without naming the problem it solves.
- Do not hide failure recovery behind generic “exception handling.”
- Do not ignore state reconstruction after restart or communication loss.
- Do not assume a distributed design improves reliability.
- Treat framework reuse and project reuse as different goals.
