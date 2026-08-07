---
name: document-governance
description: Create, restructure, review, or standardize engineering documents, specifications, reports, management summaries, training material, release notes, and evidence packs. Use when document purpose, audience, traceability, versioning, terminology, or source-of-truth control matters. Do not use for casual prose with no engineering governance need.
---

# Document Governance

Create documents that support a specific decision, implementation, verification, operation, maintenance, training, or audit purpose.

Read:

- `references/document-rules.md`
- `references/document-types.md`
- `references/traceability.md`

Use the templates in `assets/` when applicable.

## Workflow

### 0. Locate the authoritative source

Before creating a document:

- Search for an existing document with the same concern, audience, and lifecycle.
- Update the existing owner when appropriate.
- Create a new view only when audience, approval status, or lifecycle differs.
- Link to mutable facts rather than copying them.
- Record the authoritative owner in the project documentation map.

### 1. Classify the document

Identify:

- Purpose.
- Audience.
- Decision or action enabled.
- Normative versus informative status.
- Owner and reviewers.
- Authoritative data/source.
- Required lifecycle and approval status.
- Sensitivity or confidentiality.

Do not begin by choosing a visual format.

### 2. Establish the information model

Separate:

- Facts.
- Assumptions.
- Requirements.
- Decisions.
- Risks.
- Issues.
- Actions.
- Evidence.
- Open questions.

Use stable identifiers for requirements, decisions, risks, interfaces, and tests where traceability matters.

### 3. Select the audience view

Choose one or more:

- Raw evidence view.
- Executive/management view.
- Engineering implementation view.
- Operator/field-service view.
- Training/learning view.
- Audit/compliance view.

Multiple views should be derived from the same authoritative evidence where practical.

### 4. Structure the document

A controlled engineering document normally includes:

1. Metadata and status.
2. Purpose and scope.
3. Audience.
4. Definitions and terminology.
5. Context and constraints.
6. Main content.
7. Decisions or requirements.
8. Risks and unresolved items.
9. Verification/evidence.
10. Change history.
11. References.

Remove sections that do not serve the document purpose.

### 5. Enforce precision

- Replace vague quality claims with measurable criteria.
- State units, date range, time zone, version scope, data exclusions, and confidence.
- Mark examples as examples.
- Identify the source of tables and figures.
- Do not invent missing evidence.
- Do not silently normalize conflicting source data.
- Use consistent domain vocabulary.

### 6. Review

Check:

- Accuracy.
- Internal consistency.
- Traceability.
- Audience suitability.
- Decision usefulness.
- Source-of-truth integrity.
- Version and change control.
- Action ownership.
- Testability of normative statements.

## Output

Provide:

1. Document classification.
2. Proposed structure.
3. Completed or revised content.
4. Assumptions and unresolved questions.
5. Traceability gaps.
6. Review checklist result.

When creating multiple audience documents, explicitly identify shared source data and explain which sections are transformed views rather than independent facts.
