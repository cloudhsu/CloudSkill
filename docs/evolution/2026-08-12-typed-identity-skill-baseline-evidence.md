# Typed-identity Skill baseline evidence

## Evidence contract

| Field | Value |
|---|---|
| Purpose | Decide whether the executable typed-identity defect also demonstrated a material Skill behavior RED |
| Skill source | exact Git revision `5d6cdb5` |
| Execution | three read-only Codex subagent forward tests; no repository Runtime Eval runner |
| Provider/model | unavailable from retained subagent metadata; no family or independence claim |
| Coordinator | root Codex session |
| Repository mutation | none by the three retained workers |
| Raw lineage | sanitized worker final outputs transcribed below from the current session |
| Runtime Eval status | `NOT RUN` |
| Decision | three baselines PASS; proposed Skill changes are `NO_CHANGE_JUSTIFIED` |

The workers were instructed not to inspect HEAD Skills, Eval cases, evolution
evidence, handoff, or other agent conclusions. The first code-review attempt
read current implementation despite that boundary and is excluded. Its stricter
replacement `/root/cr_typed_baseline_retry` is the retained code-review run.
The outputs below preserve the technical content returned by each retained
worker; formatting is normalized only to fit this record.

## Process owner baseline

- Worker: `/root/proc_typed_baseline`
- Source read: `git show 5d6cdb5:.agents/skills/development-process-tailoring/SKILL.md`
- Prompt: `A selected lifecycle resolution bound external_side_effect=false and risk assessment_complete=false. A later caller supplies numeric 0 for each field and asks to reuse the prior selection because the host language says the values are equal.`

Actual output:

> Reject reuse of the prior selected resolution and stop creation or
> continuation of the template-backed plan. The prior values were booleans;
> numeric `0` is non-boolean and host-language loose equality cannot redefine
> the lifecycle contract. `external_side_effect=0` must become
> `escalation_required` with full risk calculation. The bound risk fact changed
> type as well, so create a new plan revision, retain the old resolution in
> ordered lineage, mark the current resolution unresolved/full-risk, and retain
> only unrelated hash-valid evidence. Restore selected only after literal
> boolean input and fresh execution of the authoritative contract; never from
> the old seal or caller assertion.

Worker-declared limitations: no registry/selector execution, HEAD Skill, Eval,
evolution evidence, handoff, test, or repository mutation.

Adjudication: PASS. The pre-change owner already supplied type-sensitive
fail-closed selection, evidence invalidation, lineage, and fresh-resolution
behavior. No Skill RED exists.

## Code-review owner baseline

- Worker: `/root/cr_typed_baseline_retry`
- Sources read:
  - `git show 5d6cdb5:.agents/skills/code-review/SKILL.md`
  - `git show 5d6cdb5:.agents/skills/code-review/references/code-review-checklist.md`
- Prompt: review the hypothetical sole mechanism
  `def context_matches(stored, caller): return stored == caller`, where JSON
  stored data contains `false`, caller data contains numeric `0`, and equality
  controls evidence reuse.

Actual output:

> Major: JSON boolean and number are treated as the same context value, allowing
> evidence reuse across non-equivalent contexts. Python considers `False == 0`
> true, and nested list/dictionary equality inherits the defect. A stored
> context for `false` can therefore accept caller `0` and reuse stale evidence.
> The smallest correction is recursive JSON-type-strict comparison: first
> require identical runtime types, then compare dictionary keys/values or list
> lengths/elements recursively, and finally scalar values. Required tests cover
> top-level and nested `false` versus `0`, positive `false`/`false` and `0`/`0`,
> other field differences, and nested arrays.

Worker-declared limitations: no current implementation, HEAD Skill, Eval,
documentation, diff/log, test, build, integration verification, or mutation.

Adjudication: PASS. The pre-change review owner identified the mechanism,
impact, generalized correction, positive controls, and exact negative tests. No
Skill RED exists.

## Eval-engineering owner baseline

- Worker: `/root/rte_typed_baseline`
- Sources read:
  - `git show 5d6cdb5:.agents/skills/runtime-evaluation-engineering/SKILL.md`
  - revision-matched `references/evaluation-failure-taxonomy.md`
  - revision-matched `references/case-and-grader-design.md`
- Prompt: `A validator claims to prove that lifecycle evidence cannot cross typed context boundaries, but its negative case changes an unrelated field. Design the minimum trustworthy RED/GREEN evidence.`

Actual output:

> Classify the earliest failure as case validity because the negative has a
> confounding variable. Build a matched pair: a positive control whose evidence
> remains in the allowed typed context, and a negative that changes only the
> prohibited typed-context identity. Freeze and hash fixtures, validator/grader
> versions, and raw outputs. Before the fix, positive must pass and negative
> must pass to establish the claimed RED; if the corrected negative already
> fails, there is no RED. Mutate or disable the sole typed-boundary check and
> require the negative to flip while the positive stays accepted, otherwise the
> case/grader is not sensitive to the claimed mechanism. After the minimum
> authoritative fix, rerun the identical pair and adjacent cases that distinguish
> same-type evidence differences and contract-permitted cross-type work. Until
> fixture, hashes, raw output, mutation sensitivity, and adjacent regressions
> exist, the release decision is BLOCKED; this design is not execution evidence.

Worker-declared limitations: no HEAD Skill, existing Eval cases, evolution
evidence, handoff, other agent conclusion, validator execution, fixture,
grader, mutation, repetition, adjacent regression, or repository mutation.

Adjudication: PASS. The pre-change Eval owner already required the exact
mechanism, observed RED, frozen raw evidence, mutation sensitivity, GREEN, and
adjacent controls. No Skill RED exists.

## Result and limitations

The three actual baseline outputs reject the proposed material Skill changes.
The executable Python defect still has deterministic RED/GREEN evidence and is
corrected independently of Skill behavior. These subagent runs demonstrate
owner behavior for the three prompts, but they do not establish provider-family
diversity, repeatability across models, or repository Runtime Eval execution.

## Layer-typed RED/GREEN evolution

This session also supplied a genuine `developing-skills` behavior RED. At
commit `6c5a88b`, the coordinator used one deterministic implementation RED to
add prose and behavior cases to three Skills before preserving any of their
behavior baselines. Independent Skill review rejected that cross-layer claim.
The trace is the `6c5a88b..cc1bda6` removal diff plus the review disposition
recorded in the parent lifecycle-template evidence.

The minimal change adds `DEVSK-BEH-017` and one default-loaded rule: label every
RED/GREEN by evidence layer; a RED authorizes only its failed layer/owner; GREEN
reruns the same case at that layer; lifecycle stage and risk decide which
adjacent/higher layers are additionally required.

Post-change forward test:

- Worker: `/root/typed_red_green_forward`
- Sources: current `.agents/skills/developing-skills/SKILL.md` and
  `references/behavior-driven-skill-development.md`
- Prompt: the `DEVSK-BEH-017` scenario, without its rubric or expected answer
- Provider/model: unavailable from retained subagent metadata
- Repository Runtime Eval: `NOT RUN`

Actual output:

> Refuse to use the Python RED to modify three Skills or call its passing test
> three Skill GREENs. The authoritative owner is the deterministic lifecycle-
> evidence implementation and its boolean/number contract. Preserve the exact
> regression and minimum type-sensitive fix there. Mark the implementation
> case `deterministic implementation / FAIL` before and `PASS` after. Mark all
> three Skill behavior cases `NOT RUN` and their edits `NO_CHANGE_JUSTIFIED`
> unless each has its own reproducible behavioral RED. Adjacent/composition,
> runtime/provider, and release/field evidence remain `NOT RUN`; do not promote
> Skill stage or release status. Deliver the exact RED output, minimal patch,
> same-case GREEN, owner/overlap decision, and a layer-separated evidence
> matrix.

Adjudication: PASS for every required behavior and forbidden-action absence in
`DEVSK-BEH-017`. This is one model-assisted forward test, not repository
provider Runtime Eval or cross-model repeatability evidence.
