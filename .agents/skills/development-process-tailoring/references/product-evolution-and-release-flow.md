# Product Evolution and Release Flow

Use this reference when a repository contains a meaningful history of changing specifications, customer requests, experiments, defects, tags, installers, product variants, and field support work.

## 1. Reconstruct evidence before judging the process

Create one ordered timeline using:

- Product/context changes.
- Requirement/specification revisions.
- Architecture and design decisions.
- Technical spikes and prototypes.
- Git commits and release tags.
- Test and defect evidence.
- Installer/configuration/driver changes.
- Customer/field feedback.
- Product variants and forks.

Classify each event as:

- Context/problem change.
- Accepted requirement.
- Decision/architecture change.
- Experiment or uncertainty reduction.
- Implementation increment.
- Defect/risk correction.
- Operationalization/deployment work.
- Release/baseline.
- Variant/product-line change.
- Deferred or rejected work.

A high commit count demonstrates activity, not process quality. A tag demonstrates a named point, not release readiness. A specification demonstrates intent, not implementation.

## 2. Build the trace chain

For each material capability or change, seek:

`problem/source -> requirement -> decision -> implementation -> verification -> release -> field evidence`

Record missing links rather than inventing them. The chain may be many-to-many; use stable identifiers when the product warrants them.

## 3. Distinguish document roles

Do not treat all documents as the same artifact:

- Customer request/feedback: input, not automatically an approved requirement.
- Product/problem statement: context and desired outcome.
- Current specification: authoritative current intent.
- Release baseline: immutable approved scope for a specific release.
- Architecture/decision record: why and trade-offs.
- Project/release plan: timing, dependency, capacity, risk, and status.
- Test/verification evidence: what was actually checked.
- Release notes: verified user/operator-visible change.
- Field issue record: observed failure and closure evidence.

## 4. Use multiple planning horizons

Maintain four horizons:

1. **Committed release** - accepted scope with owner, acceptance evidence, dependencies, and rollback.
2. **Discovery** - uncertain mechanisms or customer questions addressed by time-boxed spikes.
3. **Candidate backlog** - prioritized but not committed.
4. **Deferred/rejected** - decision and reason retained.

Urgent work should state what is displaced, what risk is accepted, and how normal flow resumes.

## 5. Technical spike contract

A spike must state:

- Question being answered.
- Time/cost limit.
- Environment/device/OS constraints.
- Evidence to collect.
- Decision options.
- Output: conclusion, sample/prototype, risks, and recommended next action.

A prototype is not production completion. Decide explicitly whether it is discarded, hardened, or isolated as test tooling.

## 6. Release baseline

A release baseline should identify:

- Source commit/tag and branch.
- Build toolchain and dependency versions.
- Product/feature flags or variant.
- Firmware/protocol/driver compatibility.
- Configuration defaults and migration.
- Installer/package identity and signing.
- Verification evidence and known limitations.
- Rollback/uninstall/recovery.
- Support/log collection procedure.

Release notes should be generated from accepted, verified changes rather than copied from raw commit messages.

## 7. Product-line and variant evolution

For each variant record:

- Shared core/capabilities.
- Different workflow, policy, UI, branding, hardware, or deployment.
- Owner and release cadence.
- Configuration/feature mechanism.
- Compatibility and test matrix.
- Divergence and merge policy.

Use a shared core when authority, lifecycle, and contracts are common. Split a product/module when ownership, release, safety, or deployment differs materially. Avoid unmanaged copy-paste forks.

## 8. Field feedback loop

For every meaningful field issue:

1. Capture environment, product version, firmware/driver, configuration, and evidence.
2. Reproduce or classify uncertainty.
3. Identify requirement/architecture/test gap.
4. Add regression or fault-injection evidence where practical.
5. Fix and verify.
6. Release through a controlled baseline.
7. Confirm field closure and feed the lesson into the process.

## 9. Management controls that add value

For a small team, prefer concise, decision-oriented controls:

- Scope and release horizon board.
- Decision/risk/dependency log.
- Requirement/spec change log.
- Variant/capability matrix.
- Release readiness checklist.
- Field issue and regression linkage.
- Capacity and external-dependency review.

Measure lead time to decision, unplanned work, escaped defects, reopen rate, release rollback, variant divergence, and traceability gaps only when they inform action.

## 10. Common failure modes

- File version increases but title/revision/status does not.
- Full specification copies diverge without a declared authoritative current version.
- Customer suggestion is treated as committed scope before analysis and approval.
- Commit messages replace requirements, decisions, tests, and release notes.
- Installer/config/driver work is omitted from completion criteria.
- Urgent requests silently displace planned scope.
- Variants fork without an explicit core/difference model.
- Field fixes do not create regression evidence.
