# CloudBox review assurance levels design

## Purpose

Replace the ambiguous assumption that every architecture, development, or
release review is a complete cross-family `2x2` panel with explicit assurance
levels. The recorded level
must describe the evidence actually obtained, while release policy separately
states the minimum level required by change risk.

This design applies after CloudBox 6.1.0. It does not rewrite the evidence or
release decision already published for 6.1.0.

## Considered approaches

1. Keep cross-family `2x2` as the only valid panel. This provides strong
   diversity but turns a provider quota or outage into an unconditional release
   stop even when the user accepts a bounded degraded review.
2. Count any four executions as equivalent. This is operationally simple but
   falsely equates repeated calls, aliases, and same-family agreement with
   independent cross-family evidence.
3. Use explicit assurance levels and risk-based minimums. This preserves
   evidence honesty, allows controlled degradation, and makes exceptional
   authorization visible. This is the selected approach.

## Assurance levels

| Level | Required composition | Meaning |
|---|---|---|
| `L1_CROSS_FAMILY_2X2` | Two independently identified models from each of two model families | Highest diversity; the standard gate for release-significant authority, safety, privacy, and automation changes |
| `L2_SINGLE_FAMILY_QUAD` | Four independently identified models from one family | Formal degraded panel when a second family is unavailable; not cross-family evidence |
| `L3_SINGLE_FAMILY_PAIR` | Two independently identified models from one family | Basic panel for bounded low-risk changes |
| `L0_SINGLE_REVIEW` | One independently identified model | Diagnostic review or post-fix recheck; not a panel |

The achieved level is determined from completed, contract-valid reviewer cells,
not requested cells. Multiple executions of one model do not increase model
independence. Aliases, endpoints, or names resolving to the same underlying
model count once. A blocked, timed-out, malformed, or quota-rejected cell does
not count toward composition.

## Risk-to-minimum-level policy

| Change class | Default minimum |
|---|---|
| Major release; security, authorization, privacy, credential/data transfer, irreversible publication, or autonomous release/evolution authority | `L1_CROSS_FAMILY_2X2` |
| Normal feature release; material Skill behavior, Router, Eval/grader, runtime contract, persistence, or recovery change | `L2_SINGLE_FAMILY_QUAD` |
| Patch release; bounded compatibility fix, low-risk tooling, or documentation with operational consequences | `L3_SINGLE_FAMILY_PAIR` |
| Investigation, RED discovery, or focused correction recheck | `L0_SINGLE_REVIEW` |

Risk classification happens before reviewer execution. A lower achieved level
does not silently lower the required level.

## Review scope

The assurance level is reusable across `architecture`, `code`, `migration`,
`skill`, `eval`, `document_governance`, `security`, and `release` review. Every record separates
`review_scope` from reviewer composition. Architecture review uses the same
level vocabulary but judges authority, lifecycle, state, failure/recovery,
migration, security, deployment, and operational evidence rather than code
style. Review assurance does not replace compilation, tests, fault injection,
device evidence, CI, or required human safety approval.

Document-governance review distinguishes a semantic baseline change from a
presentation-only edit:

| Document change | Default minimum |
|---|---|
| Authority source, approval status, regulatory/safety meaning, release baseline, or version lineage | `L1_CROSS_FAMILY_2X2` |
| Cross-document contract, need-design-test traceability, or audience-transformation rule | `L2_SINGLE_FAMILY_QUAD` |
| One engineering document's structure, terminology, ownership, or version correction | `L3_SINGLE_FAMILY_PAIR` |
| Spelling, formatting, generated index, or link repair with proven zero semantic change | Deterministic checks only |

Document review checks authoritative ownership, version and approval state,
scope, duplicated mutable facts, traceability, audience views, replacement and
retention rules, private-data exposure, and whether inference is mislabeled as
verified fact. It starts with link, schema, version, duplication, traceability,
and semantic-diff checks. Review packets contain only changed passages,
authoritative sources, and affected contracts; the whole document corpus is
not sent merely because it exists.

## Token-efficiency policy

Token conservation is a first-class constraint. The coordinator must use the
least expensive evidence path that can still satisfy the risk-selected gate:

1. Run deterministic contracts, schemas, tests, static analysis, and diff
   checks before any hosted reviewer.
2. Freeze one minimal review packet and reuse it across cells; do not send the
   repository or repeated background prose when a bounded diff and governing
   contracts are sufficient.
3. Start with the smallest required level for the classified risk. Do not run
   L1 merely because the mechanism exists.
4. Use efficient models for routine cells and reserve frontier models for
   material ambiguity, safety, authority, unresolved disagreement, or the
   explicitly required L1 composition.
5. Stop early on a valid release-blocking veto or High finding, correct it,
   rerun deterministic checks, and recheck only affected cells unless lineage
   or scope changed materially.
6. A no-change deterministic result performs zero model calls. Cached or
   previously frozen evidence may be reused only when source, contract, and
   lineage hashes prove it remains applicable.
7. Record per-cell input/output tokens, cached tokens when exposed, attempts,
   latency, and provider cost without combining providers into a misleading
   average.

Token savings may reduce unnecessary execution, context, repetition, or model
cost. They may not mislabel the achieved assurance level, omit a risk-required
cell, conceal degraded evidence, or automatically authorize an exception.

## Evidence validity and reviewer drift

Completed review evidence is reusable only while the reviewed source,
governing contract, review packet, rubric, and relevant risk classification
remain hash-equivalent. Provider aliases do not prove stable model identity.
A materially changed canonical model, retired model, changed rubric, newly
discovered risk, or expired organizational policy triggers reassessment even
when the source diff is unchanged.

The coordinator records evidence age and validity reason but does not impose a
universal time expiry. Safety, security, privacy, dependency, and deployment
reviews may define shorter validity windows than ordinary design review. Stop
review expansion when findings saturate and the required level is complete;
additional reviewers are not collected merely to increase a count.

## Degradation and exceptional authorization

A release record must persist:

- `required_level`;
- `achieved_level`;
- requested and canonical returned model identities;
- family identity and independence evidence;
- incomplete cells and their `BLOCKED`, `FAIL`, or invalid reason;
- unresolved findings and safety vetoes;
- degradation reason;
- explicit exceptional authorization when achieved is below required.

Automatic degradation may select the next executable composition, but it may
not authorize publication. When `achieved_level < required_level`, release is
blocked unless the user explicitly authorizes that exact exception with the
remaining risk visible. An exception changes release authority, not evidence:
the achieved level remains unchanged.

No vote can override an unresolved safety veto, authority violation, privacy
leak, or High finding. Model agreement is corroboration, not proof of
correctness.

## Evidence contract and ownership

The multi-model panel contract is the authoritative mechanical owner for level
calculation and model-cell validity. Release policy owns risk classification
and minimum-level selection. Release evidence owns the achieved-versus-required
comparison and any exception authorization. Skill prose explains judgment but
must not duplicate the level algorithm.

The contract must reject:

- an L1 claim without two valid families and two independent models per family;
- an L2 claim assembled from fewer than four independent same-family models;
- an L3 claim assembled from fewer than two independent same-family models;
- repeated calls or aliases counted as independent models;
- a blocked cell counted as complete;
- an exception represented as if the required assurance level passed.

## RED and GREEN evidence

Implementation must first preserve RED fixtures for at least:

1. Four calls to one model incorrectly reported as L2.
2. Two GPT and two blocked Claude cells incorrectly reported as L1.
3. Four independent GPT models incorrectly labeled cross-family.
4. An L0 result below an L1 requirement published without explicit exception.
5. Explicit exception authorization incorrectly upgrading `achieved_level`.

GREEN requires the same fixtures to produce the truthful level and release
decision, plus regression of the existing complete cross-family panel.
Structural schema validation alone is not behavioral or release-policy PASS.

## CloudBox 6.1.0 historical classification

The 6.1.0 final evidence is classified retrospectively as:

- required level under this new policy: `L1_CROSS_FAMILY_2X2`;
- achieved level: `L0_SINGLE_REVIEW`;
- unavailable evidence: Claude provider quota blocked;
- authority: explicit user-approved degraded release;
- claim limit: GPT-only PASS, with no cross-family agreement claim.

This classification adds vocabulary for future records; it does not mutate the
immutable 6.1.0 tag or pretend the missing reviewer cells executed.

## Scope boundaries

Included in the future implementation:

- authoritative assurance-level contract;
- deterministic calculation and anti-drift validation;
- risk/minimum policy and exception state;
- architecture, development, document-governance, and release scope profiles;
- migration of future panel and release records;
- documentation of truthful degraded outcomes.
- evidence-validity, model-drift, saturation-stop, and review-budget rules;

Excluded:

- changing provider credentials or quotas;
- treating model repetition as model diversity;
- retroactively modifying the 6.1.0 tag;
- automatically authorizing a release exception;
- requiring L1 for every documentation-only change.
