---
name: document-governance
description: Use when engineering documents disagree on authority, version lineage, audience, approval state, traceability, terminology, source data, or release baseline.
---

# Document Governance

Create documents that support a specific decision, implementation, verification, operation, maintenance, training, release, or audit purpose.

Read:

- `references/document-rules.md`
- `references/document-types.md`
- `references/traceability.md`
- `references/requirements-spec-evolution.md` for requirement/specification chains, customer feedback, release baselines, and supersession control.

Use the templates in `assets/` when applicable.

## Workflow

### 0. Locate the authoritative source and lineage

Before creating or revising a document:

- Search for an existing document with the same concern, audience, and lifecycle.
- Identify the current authoritative document, immutable release baselines, proposals, customer inputs, and obsolete/superseded copies.
- Update the existing owner when appropriate.
- Create a new view only when audience, approval status, release baseline, or lifecycle differs.
- Link to mutable facts rather than copying them.
- Record the authoritative owner and supersession relationship in the project documentation map.

Do not infer authority from the highest filename version alone. Check title, internal revision history, status, approval, content, and release linkage.

### 1. Classify the document

Identify:

- Purpose.
- Audience.
- Decision or action enabled.
- Normative versus informative status.
- Document role: input/request, analysis, decision, current specification, release baseline, plan, test evidence, release notes, field evidence, or training view.
- Owner and reviewers.
- Authoritative data/source.
- Required lifecycle, version, approval, and supersession status.
- Product/release applicability.
- Sensitivity or confidentiality.

Do not begin by choosing a visual format.

### 2. Establish the information model

Separate:

- Facts and observed evidence.
- Assumptions.
- Requests and candidate requirements.
- Accepted requirements.
- Decisions and rejected alternatives.
- Risks, issues, dependencies, and actions.
- Implementation and verification status.
- Release/baseline status.
- Open questions.

Use stable identifiers for requirements, decisions, risks, interfaces, tests, releases, and field issues where traceability matters.

### 3. Select the audience view

Choose one or more:

- Raw evidence/customer-input view.
- Executive/management view.
- Product/requirements view.
- Engineering implementation view.
- Operator/field-service view.
- Training/learning view.
- Release/audit/compliance view.

Multiple views should be derived from the same authoritative evidence where practical. A customer presentation, current engineering specification, and release notes may describe the same capability but have different authority and lifecycle.

### 4. Structure the document

A controlled engineering document normally includes:

1. Metadata, version, status, owner, and applicability.
2. Purpose and scope.
3. Audience.
4. Definitions and terminology.
5. Context and constraints.
6. Main content.
7. Decisions or accepted requirements.
8. Risks, dependencies, and unresolved items.
9. Verification/evidence and release linkage.
10. Change history and supersession.
11. References.

Remove sections that do not serve the document purpose.

### 5. Control evolving specifications

For each material revision:

- State why it changed and who/what triggered it.
- Distinguish new, changed, removed, deferred, and rejected requirements.
- Identify affected architecture, interfaces, product variants, compatibility, tests, and releases.
- Record decision and approval status.
- Link implementation and verification evidence when available.
- Identify what it supersedes.

Prefer one current specification with a controlled change log plus immutable release baselines. Avoid maintaining many editable full copies unless contractual or audit constraints require them.

### 6. Enforce precision

- Keep filename, cover title, internal revision history, status, and release reference consistent.
- Replace vague quality claims with measurable criteria.
- State units, date range, time zone, version scope, product/firmware/driver applicability, data exclusions, and confidence.
- Mark examples, mockups, and proposals as such.
- Identify the source of tables and figures.
- Do not invent missing evidence.
- Do not silently normalize conflicting source data.
- Use consistent domain vocabulary.
- Keep planned, implemented, verified, and released status separate.

### 7. Review

Check:

- Accuracy.
- Internal and cross-document consistency.
- Authority and supersession.
- Traceability.
- Audience suitability.
- Decision usefulness.
- Source-of-truth integrity.
- Version, baseline, and change control.
- Action ownership.
- Testability of normative statements.
- Release and field-evidence linkage.
- Confidentiality and suitability for the target repository.

## Skill composition

- Use `$development-process-tailoring` to govern how requirements, plans, releases, variants, and feedback evolve.
- Use `$architecture-review` when the document must reconstruct architectural decisions.
- Use `$software-quality-iso25010` for measurable quality requirements and release gates.

## Output

Provide:

1. Document classification and authority
2. Lineage/supersession map
3. Proposed structure
4. Completed or revised content
5. Assumptions and unresolved questions
6. Traceability and release-linkage gaps
7. Review checklist result

When creating multiple audience documents, explicitly identify shared source data and explain which sections are transformed views rather than independent facts.
