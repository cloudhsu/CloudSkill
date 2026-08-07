# CloudSkill evaluations

CloudSkill separates evaluation layers:

- `skill-routing-cases.csv`: positive, negative, and adjacent-skill routing cases.
- `behavior/`: recognition, application, counterexample, discipline, and reference behavior contracts.

Add or update a routing case whenever a skill fails to trigger, over-triggers, or selects the wrong adjacent skill.

For behavior changes, preserve RED baseline evidence before editing the skill, then run the same case with the candidate skill and regress adjacent cases. Case-schema validation is not a model execution.

Evaluate:

- correct skill selection,
- required workflow and decisions,
- required artifacts,
- prohibited actions and unsupported claims,
- evidence honesty,
- multi-skill ordering,
- reasonable scope and token/command efficiency.
