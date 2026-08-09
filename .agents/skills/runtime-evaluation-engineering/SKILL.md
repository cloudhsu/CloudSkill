---
name: runtime-evaluation-engineering
description: Use when designing, reviewing, or debugging an executable AI, agent, model, router, or skill evaluation system involving case validity, context evidence, reproducibility, structured outputs, deterministic grading, semantic judging, score interpretation, regression gates, or release decisions.
---

# Runtime Evaluation Engineering

## Core principle

An Eval result is trustworthy only when the case, context, execution, grader, and release interpretation are independently valid. A low score does not automatically prove a Skill defect.

Read:

- `references/evaluation-failure-taxonomy.md`
- `references/case-and-grader-design.md`

Use:

- `assets/EVAL_SYSTEM_REVIEW.template.md`

## Trigger conditions

Use this skill when the task asks to:

- design an executable routing, behavior, tool-call, RAG, prompt, or agent Eval;
- determine whether a failure belongs to the case, prompt, Router, Skill, model, Runner, grader, or local runtime;
- define deterministic hard gates and semantic review;
- investigate repeated but plausible alternative routes;
- prevent internal planning from being counted as final-answer evidence;
- set score thresholds, release gates, model comparisons, or regression policy;
- decide whether one model run is sufficient evidence for a Skill change.

## Non-trigger conditions

Do not use this skill for:

- merely starting Ollama, finding Python, locating JSONL, or packaging a local run; use `local-runtime-eval-debugging`;
- creating or editing Skill instructions after the Eval defect is already established; use `developing-skills`;
- designing the domain system being evaluated;
- ordinary test automation where no model or agent judgment is involved.

## Required workflow

### 1. Classify the earliest failed layer

Classify the result as one or more of:

1. infrastructure or local runtime,
2. context assembly or retrieval,
3. output-contract adherence,
4. case ambiguity or invalid expected answer,
5. model discrimination,
6. Skill or Router rule,
7. deterministic grader,
8. semantic judge,
9. release-gate interpretation.

Do not diagnose a later layer when an earlier layer never executed.

### 2. Validate the case before changing the Skill

Check:

- Is there one clear deliverable owner?
- Does the prompt accidentally combine independent deliverables?
- Are alternative execution orders valid?
- Are required and forbidden skills justified by decision boundaries?
- Does the expected answer encode a preference rather than a contract?
- Are positive, adjacent, and counterexample cases present?

When repeated contract-valid outputs choose the same plausible alternative, review the expected answer before rewriting the Skill.

### 3. Verify context and reproducibility

Record:

- model and exact version,
- temperature, seed, repetition count,
- prompt/context hashes,
- loaded and dropped files,
- context budget and reserve,
- raw output before repair,
- deterministic repairs,
- latency and token usage.

A result without verified context is diagnostic evidence, not a Skill regression.

### 4. Separate metric dimensions

Report separately:

- output-contract validity,
- primary-owner accuracy,
- supporting-skill recall,
- extra-skill precision,
- execution-order validity,
- final-answer discipline,
- required behavior evidence,
- prohibited behavior,
- safety penalties,
- no-skill accuracy.

Do not collapse every failure into one strict pass rate.

### 5. Design the grader in layers

Use deterministic grading for:

- schema and set relations,
- exact IDs,
- required fields,
- explicit prohibited phrases,
- file and artifact existence,
- reproducible mechanical constraints.

Use semantic or human review for:

- architectural completeness,
- justified assumptions,
- case ambiguity,
- equivalent terminology,
- whether the proposed decision is materially safe.

A keyword hit from internal planning must not count as final-deliverable evidence.

### 6. Establish RED and GREEN

Preserve the exact failing case and raw output. Make the smallest change to the authoritative owner, then rerun:

- the same case,
- adjacent routes,
- negative controls,
- at least three repetitions for unstable local models,
- a second model or human review when the expected answer is disputed.

### 7. Set a truthful release decision

Use:

- `PASS`: case, context, execution, and grader are valid and the gate passes;
- `FAIL`: execution is valid and a real regression remains;
- `BLOCKED`: infrastructure or context prevents judgment;
- `AMBIGUOUS`: the case or expected answer lacks a unique contract;
- `MANUAL_REQUIRED`: semantic equivalence or safety cannot be resolved deterministically.

## Required output

1. Earliest failed layer
2. Case-validity assessment
3. Context and reproducibility evidence
4. Metric-by-metric result
5. Grader-validity assessment
6. RED baseline and repetitions
7. Minimal authoritative change
8. GREEN and adjacent regressions
9. Release decision
10. Remaining limitations and next review trigger

## Common mistakes

- Editing a Skill because one small model scored poorly.
- Treating a stable alternative route as random noise.
- Counting planning text as final-answer evidence.
- Letting contract invalidity erase otherwise correct field-level metrics.
- Using static validation as proof of model behavior.
- Requiring one unique execution order where several orders preserve the same selected set.
- Refining an output and overwriting the raw evidence.
- Treating an Eval gate failure as a Runner crash.
