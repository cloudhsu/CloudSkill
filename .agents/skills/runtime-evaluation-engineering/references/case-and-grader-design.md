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
