# Case and grader design

## Case design checklist

A good case states:

- the requested deliverable,
- the decision boundary,
- the expected owner,
- required and forbidden companions,
- whether alternative execution orders are allowed,
- evidence that distinguishes adjacent skills,
- one counterexample.

Split a case when two deliverables can be requested and graded independently.

## Metric design

Keep these dimensions separate:

1. contract validity,
2. primary-owner accuracy,
3. required supporting recall,
4. additional-skill precision,
5. selected-set consistency,
6. execution-order validity,
7. final-answer discipline,
8. behavior evidence coverage,
9. safety penalties.

## Final-answer evidence boundary

Prefer structured output:

```json
{
  "final_answer": "...",
  "assumptions": [],
  "verification_scenarios": []
}
```

or explicit `<final>...</final>` delimiters.

Only the final-deliverable field or segment may satisfy behavior criteria. Internal planning can trigger a discipline penalty but cannot earn engineering evidence points.

## Repetition policy

- Deterministic mechanical tests: one run.
- Local small-model routing: at least three repetitions.
- Disputed expected answer: second model or human review.
- Release gate: retain raw records, prompt hashes, and grader version.

## Refinement policy

A refinement pass is a separate derived artifact. It must:

- preserve the raw output,
- state that refinement occurred,
- pass a minimum-content and no-planning validation,
- be rejected rather than replacing raw evidence when it collapses or truncates,
- be graded separately.

## Multi-model judge protocol

Treat semantic judging as a calibrated experiment, not a popularity contest.

- Freeze and hash one evidence packet before judging. Preserve candidate order
  randomization and the label map outside judge prompts.
- Require each judge to return dimension-level findings, cited evidence,
  confidence, blocking safety findings, and one release state.
- Keep extraction, patch generation, judging, and adjudication as separate
  roles. If the same model family performs more than one role, disclose it.
- Compare inter-judge agreement per dimension and inspect every unique safety or
  authority objection. Do not use a mean score to hide disagreement.
- Calibrate judges with positive and negative controls, including a fluent but
  unsafe answer. A judge that rewards keyword coverage while missing the unsafe
  mechanism is not release evidence.
- Persist model/version, judge prompt hash, source-output hash, rubric hash,
  latency/token usage when available, and the independent raw verdict.
- Use a human or designated adjudicator for veto findings and unresolved
  equivalence. The adjudicator may not silently rewrite a verdict.

For Skill changes, judge the same RED case before and after the minimal patch,
plus adjacent negative controls. Do not tell judges which candidate is the new
version until their verdicts are frozen.
