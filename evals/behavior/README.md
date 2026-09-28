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

The "rubric result" above is stored as a structured verdict, not only as free text in a ledger note. Append one record per graded answer with `python3 scripts/verdicts.py record --evidence <result file> --case <ID> --attempt <n> --grader-kind self|cross-family|rubric|human --model <name> --required met,miss,... --forbidden ok,violated,...`. Records go to `evals/runtime/results/verdicts/<result file>.verdicts.jsonl` (a sidecar; the raw result file and its `evidence-manifest.json` pin are never edited), and the tool rejects a verdict that disagrees with the per-behavior judgements or a record whose behavior counts differ from the case contract. A `self` verdict is the executing agent grading its own answer; report it separately from `cross-family` or `human` verdicts.

`record` accepts only `met|miss` for `--required` and `ok|violated` for
`--forbidden`, ignoring case and surrounding whitespace. Unknown values or
empty comma-separated items exit nonzero with the option and 1-based item
position, before any sidecar write. An entirely empty list is allowed only
when the case has zero behaviors of that kind; omission of `--forbidden`
means an empty list. Counts must still match the case contract.

Required metadata (`evidence_file`, `case_id`, `method`, `graded_at`) must
be non-blank strings. A supplied grader model must also be a non-blank
string; `self`/`cross-family` require it, while `human`/`rubric` may use null.
The shared validator applies these rules to both recording and reporting.
Expected record-validation failures (including counts, missing model and
non-positive attempt) exit with a readable error rather than a traceback,
before writing. Programmatic `append` callers still receive `ValueError`.

`python3 scripts/verdicts.py report` audits distinct `(case_id, evidence_file)`
pairs against local standard sidecars. Both identifiers must match; sharing
a basename or a result file with another case does not establish coverage.
Repeated ledger rows and multiple graders do not inflate the pair count.
The report reuses `evidence_integrity.tokenize` for comma-separated references
and annotations; patterns and n/a pointers remain unresolved.

Use `python3 scripts/verdicts.py report --format json` for per-pair status,
1-based ledger row indices, declared grader kinds, sidecar attempt values,
unresolved references and malformed-sidecar diagnostics. Invalid records
are excluded; an unreadable JSONL sidecar is excluded as a whole. Reporting
does not modify ledger entries, sidecars, raw answers or manifest pins.

This is identifier association, not execution-attempt coverage or a quality
score. It does not verify raw-answer hashes, current case contracts, attempt
linkage or whether a declared cross-family grader is actually independent.
Missing local sidecars do not imply that no grading exists in other archives.

Behaviors about which skill was selected are judged from the recorded routing (`actual.primary_skill`), not from the answer text; a grader that only sees the answer cannot tell.
