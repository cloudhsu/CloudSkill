# Requirements and Specification Evolution

Use this reference when requirements and specifications change over time, especially when customer feedback, mockups, implementation notes, release plans, and field fixes coexist.

## 1. Define document roles

Keep these roles distinct:

This list matches SKILL.md Section 1's document-role enumeration exactly; keep
both in sync rather than letting either drift its own item names or count.

- **Request/input** - customer, operator, PM, field, regulation, or incident input.
- **Analysis** - problem interpretation, use cases, alternatives, feasibility, and risk.
- **Decision** - accepted choice, owner, date, rationale, and rejected alternatives.
- **Current specification** - authoritative current product/engineering intent.
- **Release baseline** - immutable approved scope/applicability for one release.
- **Plan** - dates, capacity, dependencies, risk, and execution state.
- **Test evidence** - test environment, result, limitation, and trace link.
- **Release notes** - verified user/operator-visible change and known limitation.
- **Field evidence** - actual environment, symptom, version, logs, resolution, and closure.
- **Product direction** - archetype, target user, promise, scope, non-goals,
  continuity, and stop condition; see SKILL.md Section 1 for the full rule.
- **Training view** - audience-adapted teaching material derived from, and
  never itself authoritative over, the roles above.

A request is not an accepted requirement. A mockup is not implemented behavior. An implementation is not released behavior.

## 2. Metadata contract

Each controlled specification or baseline should include:

- Stable document ID/title.
- Version/revision.
- Status: draft, proposed, reviewed, approved, superseded, obsolete.
- Owner and approvers.
- Product/variant/release applicability.
- Effective date.
- Supersedes/superseded-by.
- Source inputs and decision references.
- Confidentiality/classification.

Filename, cover title, revision table, document properties, and repository path must agree. Flag mismatches explicitly.

## 3. Current specification versus release baselines

Prefer:

- One editable current specification.
- A change log with structured deltas.
- Immutable release baselines/tags or approved exports.
- Links from releases to source/build/test evidence.

Do not maintain a chain of editable full-copy files as independent authorities. When old copies must be retained, mark them superseded and read-only.

## 4. Change record

For each material change record:

- Change ID and trigger/source.
- Problem/outcome.
- Requirement before and after.
- Added/changed/removed/deferred/rejected classification.
- Decision and approval.
- Affected architecture/interfaces/configuration/variants.
- Compatibility and migration impact.
- Verification and target release.
- Status and closure evidence.

## 5. Traceability model

Use the smallest useful chain:

`source/problem -> requirement -> decision/design -> implementation -> test -> release -> field evidence`

Trace at use-case/capability level when line-by-line traceability adds no value. Increase granularity for safety, compliance, protocol, data migration, firmware update, or high field-impact behavior.

## 6. Status model

Keep status dimensions separate:

- Requirement: proposed/accepted/deferred/rejected.
- Implementation: not started/in progress/implemented.
- Verification: untested/partially tested/verified/failed.
- Release: unreleased/candidate/released/withdrawn.
- Field: unobserved/monitoring/confirmed/closed/reopened.

A single “done” field hides important risk.

## 7. Customer and internal views

A customer presentation may emphasize workflow and screenshots. An internal specification must additionally capture authority, edge cases, failure behavior, privilege, compatibility, testability, and release impact.

Derive both from shared requirement/decision data. Do not copy mutable technical facts into multiple uncontrolled documents.

## 8. Review checks

- Does the latest named file contain the latest internal revision?
- Is there exactly one current authority?
- Are proposals and mockups clearly marked?
- Can each accepted requirement be connected to a decision and release target?
- Are removed/deferred requirements retained with reason?
- Are implementation, verification, and release status distinct?
- Are product/firmware/driver variants explicit?
- Are release notes based on verified changes?
- Are confidential customer/protocol details excluded from public evidence repositories?
