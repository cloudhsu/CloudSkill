# Coding-agent Project Development Standard

## Purpose

This standard governs how Codex and other coding agents analyze, modify, test, document, and release software repositories.

It is different from `AGENT_DEVELOPMENT_STANDARD.md`, which governs building an AI-agent product.

## Core Rules

1. Repository code and tests are evidence; documentation expresses intent but is not proof of implementation.
2. Domain invariants, authority, transactions, historical meaning, and deployment topology must be identified before consequential changes.
3. Preserve unrelated working-tree changes.
4. Use risk classification to decide agent count, reasoning depth, review, and approval.
5. Parallelize only isolated work.
6. Keep changes small, testable, and reversible.
7. Never fabricate Git history, test results, device validation, deployment, or external actions.
8. Synchronize controlled documentation when behavior, contracts, schema, deployment, or release changes.
9. Use an ExecPlan for complex or multi-session work.
10. A human retains final approval for production deployment, destructive migration, irreversible external action, and physical-process control unless a formal approved policy states otherwise.

## Recommended Repository Set

```text
00_START_HERE.md
AGENTS.md
PROJECT_CONTEXT.md
DOMAIN_INVARIANTS.md
ARCHITECTURE_AND_FILE_MAP.md
DEVELOPMENT_STANDARDS.md
API.md
DECISION_LOG.md
TEST_REPORT.md
OPERATIONS_RUNBOOK.md
RELEASE_CHECKLIST.md
PLANS.md
```

Tailor this set; do not create unused documents.

## Risk Routing

### Low

Documentation, formatting, isolated non-behavioral changes.

### Medium

Compatible API/query/UI extensions with bounded state impact.

### High

Money, authorization, personal data, schema, migration, historical records, transactions, production deployment, security, broad refactoring, irreversible side effects, or physical equipment behavior.

## Handoff Contract

Report:

- Outcome.
- Files changed.
- Invariants preserved.
- Tests executed and exact results.
- Tests not executed.
- Data/migration impact.
- Deployment/rollback impact.
- Remaining risks and decisions.
