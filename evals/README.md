# CloudSkill evaluations

CloudSkill separates evaluation layers:

- `skill-routing-cases.csv`: positive, negative, and adjacent-skill routing cases.
- `behavior/`: recognition, application, counterexample, discipline, and reference behavior contracts.
- Additional behavior files may target an existing skill when a distinct evidence source, such as conversation-derived optimization, needs independently reviewable cases.

Add or update a routing case whenever a skill fails to trigger, over-triggers, or selects the wrong adjacent skill.

For behavior changes, preserve RED baseline evidence before editing the skill, then run the same case with the candidate skill and regress adjacent cases. Case-schema validation is not a model execution.

When cases are mined from conversations:

- record which conversation context or export was actually available,
- sanitize identifying and operational details before committing,
- preserve the user's correction as required/forbidden behavior,
- deduplicate semantically equivalent cases,
- do not treat a generated case file as a GREEN result.

Evaluate:

- correct skill selection,
- required workflow and decisions,
- required artifacts,
- prohibited actions and unsupported claims,
- evidence honesty,
- multi-skill ordering,
- reasonable scope and token/command efficiency.

## Reading a regression result

- **Use a same-period control.** To check whether a Skill change regressed adjacent cases, re-run the *unchanged* text in the same period (same cases, models, grader and repeat count) and compare against that control, not against an older baseline. Observed once (2026-10-04, `game-art-pipeline`): 14 cases x 3 models x n=2 scored 44/79, 39/82 and 39/82 on the same unchanged text, about 5 answers of 80 of run-to-run noise. That is an observation for that configuration, not a general threshold; each configuration needs its own control.
- **Check routing and loading first.** A case whose owner skill was not loaded in a run is not a RED for that skill's text. Record the routed skill per run before writing a rule.
- **Check plan-only reachability.** A case that needs file inspection, tool execution or facts the prompt does not supply cannot be met in a plan-only run; repair the case contract (a commitment to check, or supply the facts) instead of changing the skill.
- **Score refusals separately.** Provider refusals, no-skill selections and timeouts are unscored: list them per model, keep the denominator, and do not count them as content failures.
- **Pin the text under test.** A run reads the live working tree; `--candidate-packet-id` is only a label. Run baselines and controls from a clean worktree of the unchanged commit.
- **Word evidence honestly.** A GREEN on a plan-only case is rule-following evidence, not behavior improvement.
