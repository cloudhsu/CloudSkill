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

## GREEN record

Use the same case after the change. Review against explicit required and forbidden behavior. Avoid scoring only by keyword presence; architecture quality often depends on ownership, failure semantics, and reasoning relationships.

## Regression set

Include at least:

- One recognition case.
- One application case.
- One counterexample or adjacent-skill case.

Discipline-enforcing skills also need pressure cases. Reference-heavy skills need retrieval and gap cases. Keep known production failures as permanent regression cases.

## Result states

- `PASS`: execution met the rubric.
- `FAIL`: execution violated or omitted a rubric item.
- `BLOCKED`: execution could not proceed because a required dependency failed.
- `NOT RUN`: no execution occurred.
- `MANUAL REQUIRED`: evidence exists but requires human judgment.

Do not convert `NOT RUN` or schema validation into `PASS`.
