---
name: development-process-tailoring
description: Select, tailor, review, or improve a software development lifecycle using waterfall, iterative development, agile practices, Extreme Programming, or a hybrid process. Use for project governance, stage gates, work-product definition, release cadence, hardware/software coordination, and process diagnosis. Do not present one methodology as universally superior.
---

# Development Process Tailoring

Assume the user is already familiar with waterfall, iterative development, agile development, and XP. Focus on process fit, control points, evidence, and trade-offs rather than introductory methodology explanations.

Read:

- `references/process-selection.md`
- `references/hybrid-lifecycle.md`
- `references/process-health.md`

## Workflow

### 1. Characterize the work

Assess:

- Requirement stability.
- Technical uncertainty.
- Hardware dependency.
- External procurement.
- Contract and compliance obligations.
- Safety/security risk.
- Integration frequency.
- Cost of late change.
- Test automation maturity.
- Release cadence.
- Team size and ownership.
- Stakeholder availability.
- Field validation constraints.

### 2. Select the governing lifecycle

Choose among or combine:

- Waterfall/stage-gated.
- Iterative/incremental.
- Agile planning and delivery.
- XP engineering practices.
- Hybrid hardware/software lifecycle.
- Maintenance/operations flow.

Explain which part of the work each process governs.

### 3. Define invariant engineering controls

Regardless of process, define:

- Entry/exit criteria.
- Required work products.
- Traceability.
- Architecture decisions.
- Quality requirements.
- Test evidence.
- Change control.
- Release/rollback.
- Configuration and version control.
- Incident feedback.
- Ownership.

### 4. Tailor ceremonies and artifacts

Retain only mechanisms that reduce a real risk or coordination cost.

For each artifact or ceremony state:

- Purpose.
- Consumer.
- Frequency.
- Required evidence.
- Failure prevented.
- Removal condition if it stops providing value.

### 5. Define feedback loops

Specify:

- Requirement feedback.
- Architecture feedback.
- Code/test feedback.
- Integration feedback.
- Field/operations feedback.
- Management decision cadence.

### 6. Diagnose process problems

Distinguish:

- Method mismatch.
- Missing engineering discipline.
- Unclear ownership.
- Insufficient automation.
- Oversized batch.
- Weak acceptance criteria.
- Delayed integration.
- Hidden work.
- Excessive ceremony.
- Unmanaged dependency.

Do not prescribe Scrum ceremonies to solve an architecture or ownership problem.

## Output Format

1. Project/work characterization
2. Recommended lifecycle and rationale
3. Tailored phases/iterations
4. Mandatory artifacts and gates
5. Engineering practices
6. Roles and decision rights
7. Metrics and feedback loops
8. Risks and anti-patterns
9. Adoption plan
