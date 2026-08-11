# Lifecycle template catalog

| Field | Value |
|---|---|
| Status | Candidate human-readable view |
| Audience | Plan owners, implementers, reviewers, and maintainers |
| Normative authority | `config/lifecycle-templates.json` |
| Executable interpretation | `scripts/lifecycle_template_contract.py` |
| Durable plan integration | `scripts/lifecycle_plan_contract.py` |

This catalog explains how to use the lifecycle-template pilot. It is not a
second template registry. Template versions, applicability, exclusions,
stages, gates, owners, evidence, compatibility, review levels, resume rules,
and invalidation rules come only from `config/lifecycle-templates.json`. If
this document and the registry differ, stop and correct this view; do not infer
or override registry behavior from this document.

## Available templates

The pilot implements three IDs. The descriptions below are navigation aids,
not complete selection criteria.

| Template ID | Informative use summary |
|---|---|
| `lightweight-change` | A small, local, reversible change inside a verified low-risk envelope. |
| `bounded-feature` | A bounded increment with approved design, known owners, reversible implementation, and automated verification. |
| `skill-evolution` | Evidence-gated Skill evolution with privacy, RED/GREEN, adjacent regression, review, and release-boundary controls. |

Selection must replay through the registry-backed contract. An ID or prose
resemblance is not enough.

## Deferred boundary

The following IDs are registered as `deferred` and have no shipped template
mechanics:

- `iterative-discovery`
- `architecture-change`
- `brownfield-refactor`
- `hotfix`
- `release`
- `hardware-integration`
- `incident-recovery`

Requesting one of these IDs returns `unsupported`. Unknown IDs also return
`unsupported`. Neither case may silently fall back to an implemented template.
Each deferred ID needs its own RED evidence, complete contract, validator, and
behavior evidence before its registry status can change.

## Selection and delta evidence

For an implemented candidate, supply exact typed applicability and exclusion
facts plus literal booleans for all six bounded-delta fields:

| Field | Decision question |
|---|---|
| `external_side_effect` | Does the task add an external side effect? |
| `authority_or_state` | Does it change authority, authoritative state, a transaction, or durable ownership? |
| `sensitive_or_privileged` | Does it add sensitive data, credentials, privilege, or authorization scope? |
| `platform_or_compatibility` | Does it add hardware, platform, deployment, protocol, schema, or compatibility variation? |
| `irreversible_or_unreconciled` | Does it add an irreversible action or an outcome that cannot be deterministically reconciled? |
| `outside_verified_envelope` | Is any known condition outside the template's verified envelope? |

All applicability and exclusion facts must match and all six delta answers must
be literal `false` for `selected`. That result records
`full_risk_calculation_required: false`; it removes only the repeated full-risk
calculation, not the lifecycle, gates, evidence, verification, resume, or
reconciliation obligations.

A selected composition that can enter a lifecycle plan also requires a
normalized selection context: work identity, source hash, full task
definitions, task facts, risk context, and the SHA-256 identity of the complete
authoritative registry. The delta-evidence and selected-resolution seals cover
that context. Omitting it returns `escalation_required`; replay under another
work item, source, task definition, fact/risk context, or registry is rejected.

A true, missing, non-boolean, or unknown delta returns
`escalation_required` and requires a full risk calculation. Missing or malformed
applicability/exclusion evidence also escalates. The Plan Owner may then select
another qualified template, add a compatible overlay, or create a new plan
revision.

## Statuses

| Status | Meaning and permitted next action |
|---|---|
| `selected` | Exact registry match; a template-backed plan may be created with the sealed resolution. |
| `escalation_required` | Evidence is outside or insufficient for the fast path; stop and return to the Plan Owner for full risk assessment/replanning. |
| `unsupported` | The requested base or overlay is unknown or deferred; no fallback is permitted. |
| `conflict` | Composition violates compatibility, ownership, gate, or completion semantics; Plan Owner adjudication is required. |

## Composition

Composition is one base plus zero or more unique overlays, resolved by the
shared contract in base-first order. The base must explicitly declare every
overlay compatible. The result preserves every required gate and evidence item
and the strongest Review Assurance level. Stage constraints are merged as one
deterministic topological order that preserves each template's partial order;
a cycle returns `conflict`. Owner, gate-transition, stage-order, or completion
semantic conflicts fail closed.

The current registry declares `skill-evolution` as an allowed overlay for
`bounded-feature`, but their current policy, action, and evidence owners differ.
The authoritative result is therefore `conflict`, not `selected`. The validator
proves successful strongest-gate composition only with a synthetic registry in
which those owners are deliberately aligned; that fixture does not change the
shipped registry.

## Examples

These are usage examples, not alternate definitions:

- Exact `lightweight-change` facts plus all-false exclusions and deltas return
  `selected`; focused verification and reconciliation remain required.
- Exact `skill-evolution` facts plus all-false exclusions and deltas return
  `selected`; sanitization, RED/GREEN, adjacent regression, and release truth
  remain required by the registry.
- A missing `outside_verified_envelope` answer returns
  `escalation_required`; the caller may not assume false.
- Requesting `release` returns `unsupported` because it is deferred.
- Composing the current authoritative `bounded-feature` and `skill-evolution`
  entries returns `conflict` because their owners do not align.

## Plan persistence, replan, and stop conditions

A selected resolution persists template IDs and versions, composition order,
the normalized selection context and its identity, delta-evidence identity,
review level, provenance, integrity, and plan revision. Admission independently
matches work/source/tasks/facts/risk and replays the resolution against the
authoritative registry; a caller-recomputed seal is not sufficient. Legacy
plans created without a template resolution retain their existing contract.

When changed evidence invalidates the delta identity, create a new plan
revision, retain the prior resolution in ordered lineage, mark the current
resolution unresolved, require full risk calculation, and preserve unrelated
hash-valid evidence. Authority-boundary and side-effect-scope changes, a source
change, a changed bound fact/risk context, or any trigger that contradicts an
all-literal-false delta do this automatically; callers do not opt in by naming
the old evidence hash. Only a fresh registry replay bound to the new context
may restore `selected`.

Stop template-backed plan creation when any of these applies:

- result status is `escalation_required`, `unsupported`, or `conflict`;
- owner or authority is ambiguous;
- composition would weaken a gate, evidence obligation, or review level;
- evidence identity, provenance, or integrity cannot be replayed;
- resume/reconciliation is undefined;
- selection is not deterministic;
- token reduction would remove lifecycle or verification evidence.

Verification and current limitations are recorded in
`docs/evolution/2026-08-11-lifecycle-template-pilot-evidence.md`.
