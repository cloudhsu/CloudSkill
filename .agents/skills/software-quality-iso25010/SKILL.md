---
name: software-quality-iso25010
description: Use when software quality must be translated into measurable scenarios, acceptance criteria, metrics, evidence, dashboards, release gates, or defect analysis using ISO/IEC 25010.
---

# Software Quality Using ISO/IEC 25010

Default to ISO/IEC 25010:2023 unless the project explicitly declares ISO/IEC 25010:2011.

Read:

- `references/quality-model.md`
- `references/quality-scenarios.md`
- `references/release-gates.md`

Do not reproduce copyrighted standard text. Use the quality model as a classification framework and translate it into system-specific, measurable requirements.

## Workflow

### 1. Confirm edition and scope

Identify:

- ISO/IEC 25010 edition.
- Product/system boundary.
- Stakeholders.
- Context of use.
- Lifecycle phase.
- Release or decision scope.
- Safety, security, regulatory, and field-service constraints.

Do not silently combine 2011 and 2023 terminology.

### 2. Select relevant quality characteristics

For ISO/IEC 25010:2023, consider:

- Functional suitability.
- Performance efficiency.
- Compatibility.
- Interaction capability.
- Reliability.
- Security.
- Maintainability.
- Flexibility.
- Safety.

Not every project needs equal weighting. Explain why a characteristic is selected, deprioritized, or excluded.

### 3. Convert characteristics into quality scenarios

For each selected characteristic define:

- Source/stakeholder.
- Stimulus.
- Environment.
- Affected artifact or system.
- Expected response.
- Measurable response criterion.
- Verification method.
- Owner. When the task supplied no owner fact, mark it unresolved -- never
  fill it from ambient session identity (see
  `../coding-agent-project-governance/references/no-fabricated-identity.md`).
- Evidence location.

### 4. Connect quality to architecture

Determine:

- Which architecture decision enables the target.
- Which component owns the behavior.
- Which failure modes threaten it.
- Which trade-offs are introduced.
- Which technical debt reduces confidence.
- Which operational controls compensate for residual risk.

### 5. Define measurement and gates

For each quality requirement specify:

- Metric.
- Calculation.
- Sample/population.
- Environment.
- Threshold.
- Warning threshold.
- Hard gate versus monitored target.
- Test or monitoring source.
- Frequency.
- Owner.

Do not use a score without preserving the underlying measurement and evidence.

### 6. Evaluate and report

Separate:

- Requirement compliance.
- Measured result.
- Confidence and limitations.
- Known exclusions.
- Residual risk.
- Corrective action.
- Release decision.

## Output Format

1. Scope and ISO edition
2. Stakeholders and product boundary
3. Selected quality characteristics
4. Quality scenarios and metrics
5. Architecture implications
6. Verification plan
7. Release gates
8. Current gaps and risks
9. Evidence/traceability matrix

## Rules

- Quality characteristics are not acceptance criteria by themselves.
- “High reliability” and similar phrases are invalid without operational definition.
- Security and safety failures may be hard gates even if aggregate quality scores are high.
- Do not average away critical failures.
- Distinguish product quality from development-process compliance.
- Preserve field data, failure denominators, excluded records, and version scope.
