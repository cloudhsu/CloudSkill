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

## Sub-agent evaluation containment

Before dispatching sub-agents to compare behavior for a real-target
evaluation (not a synthetic sandbox task), decide whether the goal is a
described plan/answer or a real, comparable artifact:

- For a real artifact, real tool access and a first-person action-phrased
  prompt are appropriate and often preferable — a hypothetical framing only
  elicits a description of hypothetical work, not the genuine work product
  needed for comparison.
- For a described plan or decision, a hypothetical framing (explicit
  "answer with a written explanation only, do not use file-editing or
  code-execution tools") is the right choice, since no real artifact is
  needed.

Regardless of which framing applies, two safeguards are load-bearing and
prompt phrasing is not a substitute for either:

- Run each sub-agent against its own disposable, isolated copy of the
  target system (a throwaway git worktree or sandboxed clone pinned to a
  fixed starting commit) — never against the live, shared system.
- Restrict each sub-agent's tool access to only what the task genuinely
  requires (file write scoped to one target path, no arbitrary shell exec,
  no network/push access where not needed).

After any such exercise, explicitly check the target system's own
change-tracking state — including the live, untouched system, not only the
isolated copies — for unintended mutations before treating the exercise as
side-effect-free. When a mutation is found despite these safeguards, revert
it and disclose that it happened, rather than silently cleaning up without
mention.

Counterexample: assuming a hypothetical prompt framing is a sufficient or
necessary safeguard on its own is wrong in both directions — it is
unnecessary when isolation and tool-scoping are already correct, and
insufficient on its own if they are not. If it is unclear whether a given
evaluation sub-agent will have real tool access, assume it does and design
isolation and tool scope accordingly.

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
