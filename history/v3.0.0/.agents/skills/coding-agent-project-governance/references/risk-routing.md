# Coding-agent Risk Routing

## Low Risk

Examples:

- Documentation wording.
- Formatting.
- isolated UI polish with no behavior change.
- test-only clarification.

Default:

- One main agent.
- Focused checks.
- No unnecessary subagent overhead.

## Medium Risk

Examples:

- Read-only API.
- Query/read model.
- Isolated component.
- Small compatible behavior extension.

Default:

- Main/Development.
- Independent test or review angle.
- Focused and regression tests.

## High Risk

Examples:

- Money/balance.
- authentication/RBAC.
- personal data.
- schema/migration.
- historical records.
- transaction.
- production deployment.
- security.
- irreversible external action.
- physical equipment control.
- broad refactor crossing ownership boundaries.

Default:

1. Architecture/risk analysis.
2. Approved acceptance criteria.
3. Isolated implementation.
4. Independent adversarial testing.
5. Integrator review.
6. Human approval for deployment/data conversion.

## Escalation

Escalate when:

- Requirements conflict.
- Data could be lost.
- Recovery is undefined.
- Existing tests disagree with documents.
- A change alters public contracts or historical meaning.
