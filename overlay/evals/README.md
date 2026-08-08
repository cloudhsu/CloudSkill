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
