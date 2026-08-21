# Behavior-driven Skill Development

## Evaluation layers

CloudSkill uses separate layers because each detects a different failure:

| Layer | Question | Typical evidence |
|---|---|---|
| Structural | Is the skill package valid? | Frontmatter, files, manifest, links |
| Description | Can the skill be discovered without leaking its workflow? | Trigger-only description checks |
| Routing | Is the correct skill selected? | Positive, negative, adjacent cases |
| Behavioral | Does the loaded skill change analysis or action? | Baseline and candidate outputs against a rubric |
| Composition | Do multiple skills execute in the correct order? | Process/domain/change/quality/handoff cases |
| Installation | Are canonical skills copied consistently to each runtime? | Hash-equivalent smoke installation |

Passing one layer does not imply another layer passed.

## RED record

For every new or materially changed skill record:

- Case ID and prompt.
- Runtime and model when known.
- Skills available during baseline.
- Actual baseline output or trace.
- Exact failure, omission, wrong route, or rationalization.
- Expected behavior and why it matters.

If a live model run is unavailable, mark behavioral execution `NOT RUN`; case-schema validation alone is not GREEN evidence.

## Fixed model-selected sub-agent review

For a new or materially changed Skill, use the managed model-selected sub-agent
policy in `config/skill-lifecycle-policy.json` as the default semantic review:

1. finish deterministic checks and freeze one packet containing the candidate
   diff, Skills/references, cases, RED/GREEN evidence, lifecycle and
   privacy/source notes, plus the target implementation's brownfield/refactored
   status and rewrite authorization state;
2. in Codex, spawn GPT-5.6 Luna and GPT-5.6 Sol as read-only independent
   reviewers with the same packet, in parallel;
3. in Claude Code, use managed sub-agents with Sonnet 5 and Opus 5; only when
   that host does not offer generation 5 may the matching 4.8 generation be
   used as a recorded fallback;
4. retain the requested model, exact selected or provider-returned model,
   agent/run identity, packet identity, verdict, findings and per-case result;
5. block promotion or release on `FAIL`, `BLOCKED`, `MANUAL_REQUIRED`, missing
   identity, or fewer than two completed reviews for an available model family;
   and
6. after a correction, freeze a new packet and repeat at most the bounded
   revision count; a reviewer stays read-only and never edits what it judges.

Use two packet identities to avoid self-referential evidence hashes. First
freeze the candidate inputs (base HEAD plus every changed/untracked input,
excluding the output evidence files) with
`scripts/freeze_skill_review_packet.py`; every behavior executor records that
candidate packet ID. After execution, freeze a review packet containing the
candidate manifest and execution evidence; every final reviewer records that
review packet ID. Final reviewer reports are outputs of, not members of, the
packet they judge. Any later semantic-input change invalidates both packets and
requires a new bounded run; appending the resulting review report does not.

For an existing or previously refactored program, reviewers must reject a
candidate that treats Skill creation as permission to replace the product.
Require architecture discovery, characterization evidence, compatibility
preservation and the smallest coherent implementation slice. A whole rewrite
is acceptable only when the user explicitly authorized that separate scope.

Do not substitute `codex exec`, a Claude CLI one-shot, the Runtime Eval provider
adapter or a local Ollama model when managed model-selected sub-agents are
available. Those paths may execute routing/behavior cases or diagnose provider
integration, but they do not satisfy the independent sub-agent review gate. If
a host cannot expose the requested sub-agent models or exact model identity,
record that family as `BLOCKED` or `NOT RUN` according to whether it is required
in that environment; never infer a pass. A higher-risk release may run both
families as a 2x2 panel, while a host exposing only one family records the other
family honestly as unavailable.

A local model stays appropriate for cheap structural/routing sanity checks, not
as the primary GREEN signal for a discipline or behavior change.

## GREEN record

Use the same case after the change. Review against explicit required and forbidden behavior. Avoid scoring only by keyword presence; architecture quality often depends on ownership, failure semantics, and reasoning relationships.

## Regression set

Include at least:

- One recognition case.
- One application case.
- One counterexample or adjacent-skill case.

Discipline-enforcing skills also need pressure cases. Reference-heavy skills need retrieval and gap cases. Keep known production failures as permanent regression cases.

## Eval-loop comparisons as RED evidence about a candidate's own wording

A baseline-vs-candidate comparison run does not only decide promote/reject —
it can also surface that a candidate's own wording is overgeneralized,
underspecified, or internally self-contradicted (for example, the candidate
argues for a mechanism its own required behaviors then override). Treat
that finding as RED evidence at the wording layer, not as an inconclusive or
wasted run.

When a comparison surfaces a real gap in the candidate's own wording:

1. Revise the wording to close the specific gap the comparison exposed —
   do not rewrite unrelated parts of the candidate.
2. Re-run the identical scenario that surfaced the gap as the GREEN check
   for that revision.
3. Cap revision-and-retest at two rounds total per candidate before
   escalating to manual review. Most real gaps close in one round; a second
   round exists for genuine residual ambiguity, not as a standing budget.

When a comparison instead shows no behavioral delta between baseline and
candidate (the baseline already does the right thing without the rule), do
not conclude low marginal value from that single comparison. Try one harder
or more adversarial variant of the same scenario first — added pressure,
a countervailing instruction, a case with a genuine complicating factor the
first scenario lacked. Only conclude low incremental value for a
general-purpose skill after a no-delta result on both the original and the
harder scenario; a single easy comparison showing no delta is not sufficient
evidence that the rule never matters.

## Result states

- `PASS`: execution met the rubric.
- `FAIL`: execution violated or omitted a rubric item.
- `BLOCKED`: execution could not proceed because a required dependency failed.
- `NOT RUN`: no execution occurred.
- `MANUAL REQUIRED`: evidence exists but requires human judgment.

Do not convert `NOT RUN` or schema validation into `PASS`.
