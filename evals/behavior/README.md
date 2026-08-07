# Behavior evaluation contracts

These files define repeatable prompts and review rubrics. They do **not** execute a model by themselves.

Every skill must have at least:

- one `recognition` case,
- one `application` case,
- one `counterexample` case.

A behavior claim requires two execution records:

1. RED baseline without the proposed change;
2. GREEN candidate with the proposed change.

Record actual runtime/model, available skills, output or trace, rubric result, and status. Valid statuses are `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, and `MANUAL REQUIRED`.

`python scripts/validate_behavior_evals.py` validates case structure and coverage only. It must never be reported as a completed model behavior test.
