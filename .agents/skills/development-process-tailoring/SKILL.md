---
name: development-process-tailoring
description: Use when delivery is constrained by unstable requirements, hardware dependencies, release trains, urgent work, field feedback, product variants, stage gates, or competing lifecycle models.
---

# Development Process Tailoring

Assume the user is already familiar with waterfall, iterative development, agile development, and XP. Focus on process fit, control points, evidence, product evolution, and trade-offs rather than introductory methodology explanations.

Own the lifecycle plan, execution-plan contract, and risk/evidence-driven
replanning. Default software development to iterative/incremental delivery and
Skill evolution to Eval-driven evolution, then compose stage-gated, agile,
spike, hybrid hardware/software, hotfix, brownfield, or lightweight profiles
when actual pressure requires them. A generic planning plugin may generate
detailed steps, but it does not become a second process authority.

Select the governing lifecycle profile before choosing planning depth; lifecycle
is always the highest planning authority and owns the complete dynamic feedback
loop. Project that lifecycle into a lightweight execution plan for small,
stable, low-risk work; delegate bounded implementation detail for medium work
only after its design is approved; and persist the lifecycle plan before
creating stage-specific detailed plans for uncertain, long-running, externally
coupled, or high-risk work. New risk or authority evidence creates a new plan
revision: invalidate affected detailed steps, preserve unaffected completed
evidence, and never continue a stale plugin-generated plan.

Resolve optimization trade-offs in this fixed order: preserve the complete
lifecycle and dynamic feedback loop first, preserve required evidence and
verification second, and reduce token/context cost third. A token saving that
weakens lifecycle control or proof is a failed optimization.

Long-running work must persist plan/work revisions, checkpoints, authority,
action identity, budgets, evidence lineage, and Review Assurance state. Resume
read-only: reconcile late external completion, reject stale plan/lease writers,
and continue from the first unproven step without expanding authority.

Read:

- `references/process-selection.md`
- `references/hybrid-lifecycle.md`
- `references/process-health.md`
- `references/product-evolution-and-release-flow.md` when reconstructing a long-lived product from specifications, Git history, tags, release notes, customer requests, field defects, variants, installers, or support evidence.

Use:

- `assets/PROCESS_TAILORING.template.md` for lifecycle tailoring.
- `assets/PRODUCT_EVOLUTION_MAP.template.md` for an existing product/repository evolution review.

## Workflow

### 0. Reconstruct the actual evolution

Before recommending a process for an existing product, build an evidence-based timeline from:

- Problem/context statements and customer requests.
- Requirement and specification versions.
- Architecture/design decisions and experiments.
- Git commits, branches, tags, and release notes.
- Test records, defects, crash/field logs, and support workarounds.
- Installer, configuration, migration, driver, and deployment changes.
- Product/customer variants and copied implementations.

Separate planned work, urgent insertion, experiment/spike, defect correction, operationalization, and deferred work. Do not infer completion from a specification or commit message alone.

### 1. Characterize the work

Assess:

- Requirement stability and rate of change.
- Technical and platform uncertainty.
- Hardware, firmware, driver, and OS dependency.
- External procurement, customer, certification, or release dependency.
- Contract, compliance, security, and licensing obligations.
- Safety and field-impact risk.
- Integration frequency and cost of late change.
- Test automation and device-lab maturity.
- Release cadence, supported versions, and upgrade/rollback needs.
- Team size, capacity, leave/availability, and ownership.
- Stakeholder availability and decision latency.
- Field validation and support constraints.
- Product-line/variant divergence.

### 2. Select the governing lifecycle

Choose among or combine:

- Waterfall/stage-gated.
- Iterative/incremental.
- Agile planning and delivery.
- XP engineering practices.
- Hybrid hardware/software/firmware lifecycle.
- Product maintenance and operations flow.
- Release train with urgent/hotfix lane.
- Discovery/spike flow for uncertain native or hardware mechanisms.

Explain which part of the work each process governs.

### 3. Define product and release horizons

Distinguish:

- Product vision and supported use contexts.
- Current release baseline.
- Next committed release scope.
- Discovery candidates and technical spikes.
- Deferred backlog.
- Customer/product variant scope.
- Defect/hotfix lane.
- End-of-support and migration work.

Do not let every new request immediately become committed release scope.

### 4. Define invariant engineering controls

Regardless of process, define:

- Entry/exit criteria.
- Required work products and authoritative owner.
- Traceability from need to release and field evidence.
- Architecture and decision records.
- Quality requirements and acceptance criteria.
- Test evidence and unsupported test gaps.
- Change/scope control.
- Configuration, version, baseline, and dependency control.
- Release, installer/config migration, rollback, and support readiness.
- Incident/field feedback.
- Ownership and decision rights.

### 5. Control requirement and specification evolution

For each material change record:

- Trigger and source.
- User/operational problem.
- Requirement or constraint changed.
- Decision and alternatives.
- Affected architecture, product variants, and compatibility.
- Verification and release target.
- Status: proposed, accepted, implemented, verified, released, deferred, or rejected.
- Superseded document/baseline.

A file with a higher version name is not evidence of a new approved baseline. Check title, revision history, content, approval, and release linkage.

### 6. Tailor ceremonies and artifacts

Retain only mechanisms that reduce a real risk or coordination cost.

For each artifact or ceremony state:

- Purpose.
- Consumer.
- Frequency or trigger.
- Required evidence.
- Decision authority.
- Failure prevented.
- Removal condition if it stops providing value.

Useful lightweight controls for a small native/device team often include:

- Weekly scope/decision/risk review.
- Release readiness review tied to device/OS/installer evidence.
- Short technical spikes with a written conclusion.
- Current specification plus change log and immutable release baselines.
- Variant/capability matrix.
- Field issue to regression-test loop.

### 7. Define feedback loops

Specify:

- Customer/problem feedback.
- Requirement and UX feedback.
- Architecture/technical-spike feedback.
- Code/test/integration feedback.
- Device/firmware/OS compatibility feedback.
- Installer/deployment feedback.
- Field/support/incident feedback.
- Management decision cadence.

Classify feedback at the earliest failed layer: verification-system defects
return to the test/Eval owner; implementation defects to development; component
interface/data/algorithm defects to design; authority, persistence, deployment,
or recovery defects to architecture; acceptance defects to analysis; and wrong
problem context to exploration. Replan only affected downstream work and
preserve hash-valid unrelated evidence.

### 8. Manage release and product-line evolution

Define:

- Version and tag policy.
- Baseline source, build inputs, dependency versions, firmware/driver compatibility, and release artifact identity.
- Release notes derived from accepted changes and verified evidence.
- Installer/configuration/data migration and rollback.
- Supported product variants and divergence limits.
- Hotfix merge-forward/backport rules.
- Field telemetry/log/support evidence and closure criteria.

Do not use copied project trees as the only record of product variation.

### 9. Diagnose process problems

Distinguish:

- Method mismatch.
- Missing engineering discipline.
- Unclear product/state/document ownership.
- Insufficient automation or test environment.
- Oversized batch.
- Weak acceptance criteria.
- Delayed integration or release evidence.
- Hidden/urgent work.
- Excessive ceremony.
- Unmanaged dependency or customer decision.
- Version/spec/release drift.
- Product-variant divergence.

Do not prescribe Scrum ceremonies to solve an architecture, ownership, specification, or release-control problem.

## Skill composition

- Use `$document-governance` for authoritative specifications, revision lineage, decisions, release notes, and traceability.
- Use `$architecture-review` to reconstruct architectural decisions and rejected alternatives.
- Use `$cross-platform-native-architecture` for Qt/device/OS/driver/installer mechanisms.
- Use `$framework-design` for shared core versus product-variant boundaries.
- Use `$software-quality-iso25010` for measurable quality and release gates.
- Use `$coding-agent-project-governance` only for how coding agents work inside the repository, not for the product lifecycle itself.

## Output Format

1. Evidence and current product-evolution timeline
2. Project/product characterization
3. Recommended lifecycle and rationale
4. Product/release horizons and scope-control model
5. Tailored phases/iterations and discovery spikes
6. Mandatory artifacts, baselines, and gates
7. Engineering practices and release controls
8. Roles and decision rights
9. Metrics and feedback loops
10. Variant, dependency, and field-support risks
11. Adoption plan and next review point
