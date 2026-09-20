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

## Recording who graded, and how

The "rubric result" above is stored as a structured verdict, not only as free text in a ledger note. Append one record per graded answer with `python3 scripts/verdicts.py record --evidence <result file> --case <ID> --attempt <n> --grader-kind self|cross-family|rubric|human --model <name> --required met,miss,... --forbidden ok,violated,...`. Records go to `evals/runtime/results/verdicts/<result file>.verdicts.jsonl` (a sidecar; the raw result file and its `evidence-manifest.json` pin are never edited), and the tool rejects a verdict that disagrees with the per-behavior judgements or a record whose behavior counts differ from the case contract. `python3 scripts/verdicts.py report` shows how many ledger rows have a verdict from each kind of grader. A `self` verdict is the executing agent grading its own answer; report it separately from `cross-family` or `human` verdicts.

Behaviors about which skill was selected are judged from the recorded routing (`actual.primary_skill`), not from the answer text; a grader that only sees the answer cannot tell.
