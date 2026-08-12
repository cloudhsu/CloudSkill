# Resumable lifecycle orchestration

CloudBox uses a pressure-selected lifecycle graph rather than one mandatory waterfall. The default development profile is iterative/incremental; Skill evolution defaults to Eval-driven RED, minimum change, GREEN and adjacent regression.

The lifecycle planning owner is development-process-tailoring. It owns:

- selected profiles, stages, gates and feedback paths;
- versioned dependency-ordered execution plans;
- risk/evidence-triggered replanning;
- stage entry, exit and re-entry;
- durable checkpoint and resume classification.

Technical Skills still own architecture, domain, design, code, quality and document decisions. A generic planning plugin may produce detailed steps only through the CloudBox plan contract.

## Pre-qualified template projection

The three-template pilot can project the lifecycle into `lightweight-change`,
`bounded-feature`, or `skill-evolution` only through the authoritative
`config/lifecycle-templates.json` registry and the pure shared selector/
composer. `docs/LIFECYCLE_TEMPLATE_CATALOG.md` is an informative operator view,
not a second registry.

An exact applicability/exclusion match plus six literal all-false bounded
deltas returns `selected` and avoids a repeated full-risk calculation. It does
not remove lifecycle ownership, gates, evidence, verification, resume, or
reconciliation. A true/missing/unknown delta returns `escalation_required`;
unknown or deferred IDs return `unsupported`; incompatible or owner/gate/
completion-conflicting composition returns `conflict`. All three non-selected
statuses stop template-backed plan creation.

The current authoritative `bounded-feature + skill-evolution` pair fails closed
as `conflict` because its policy/action/evidence owners differ. Template
stage lists are deterministic partial-order constraints: composition uses a
topological merge and a cycle returns `conflict`. Template resolution evidence
binds work, source, task definitions, normalized task facts/risk, and complete
registry identity; it is sealed, independently matched, replayed against the
registry, and persisted in the lifecycle plan. Cross-context reuse and a
caller-resealed replay are rejected.

A source, authority-boundary, side-effect-scope, bound-fact/risk, or explicit
delta change that contradicts the selected all-false evidence automatically
invalidates its exact delta identity. Replan creates contiguous lineage and an
unresolved, full-risk-required current resolution unless a fresh authoritative
resolution is bound to the new context. This does not depend on a caller
supplying an invalidation list; unrelated valid evidence remains reusable.

A resumed task first reconciles durable state, authoritative plan revision, hashes, external effects and authority. It returns SAFE_TO_RESUME, ALREADY_COMPLETED, RETRY_REQUIRED, ATTEMPTS_EXHAUSTED, RECONCILIATION_REQUIRED, STALE_BASELINE or AUTHORITY_REQUIRED. Timeout alone never proves failure.

One coordinator owns state transitions through a lease/fencing token. Actions carry stable identity and deduplication keys. Resumed writes may attenuate authority; expansion requires an exact, persisted grant record bound to the plan revision and authorization source. Review evidence without the exact scope/source/contract/packet/rubric/risk context fails closed and is not reused. Risk changes produce a new plan revision, invalidate affected downstream work, preserve unrelated evidence and recalculate review assurance. Release, deployment, target verification and operational confirmation remain separate states.
