# Engineering Governance Overview

This document records cross-cutting rules. Detailed procedures, checklists, and templates live in the corresponding skills and are authoritative for execution.

## Documentation

- Every controlled document needs a purpose, audience, owner, status, version, and authoritative source.
- Separate facts, assumptions, requirements, decisions, risks, actions, and evidence.
- Prefer one source of truth and generated/audience-specific views over copied mutable facts.
- Link requirements, design decisions, implementation, verification, release, and field evidence when risk justifies traceability.
- Use `document-governance` for the detailed workflow.

## Product quality

- Use ISO/IEC 25010 as a classification model, not a generic checklist.
- Translate selected characteristics into scenarios, measurable criteria, verification, owners, and release gates.
- Do not average away critical safety, security, data-integrity, or authorization failures.
- Use `software-quality-iso25010` for the detailed workflow.

## Development lifecycle

- Tailor waterfall, iterative development, Agile, XP, and hybrid controls to requirement stability, uncertainty, hardware dependency, compliance, integration cost, and release cadence.
- Preserve entry/exit criteria, evidence, configuration control, rollback, and ownership regardless of method.
- Use `development-process-tailoring` for the detailed workflow.

## Coding-agent project governance

- Repository instructions must state invariants, source-of-truth code, build/test commands, risk routing, and evidence rules.
- Parallel agents require isolated ownership and an integrator.
- High-risk changes require independent review, migration/rollback evidence, and human approval where consequences are irreversible.
- Use `coding-agent-project-governance` for the detailed workflow.

## AI-agent product development

- Start from a task contract, autonomy boundary, tools, data, and risk—not from prompt tuning.
- Define evaluations before broad implementation.
- Treat instructions, context, tools, state, orchestration, validation, guardrails, and traces as one harness.
- Critical authorization and consequential-action cases are hard release gates.
- Use `agent-development-process` for the detailed workflow.
