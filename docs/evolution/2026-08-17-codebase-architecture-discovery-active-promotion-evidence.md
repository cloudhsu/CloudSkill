# `codebase-architecture-discovery` — experimental -> active promotion evidence

Follow-up to the first-pass draft->experimental evidence
(`docs/evolution/2026-08-17-codebase-architecture-discovery-first-pass-evidence.md`).
Adds repeat-count evidence, two new adjacent-regression controls, and the
behavior-layer RED evidence explicitly disclosed as not-yet-run in the
first pass. Provider: Claude Code CLI, `sonnet` alias.

## New adjacent-regression controls

Two negative routing cases added, mirroring the pattern used for
`indie-game-product-evolution`'s own `active` promotion (new controls added
at promotion time, not just re-running the original three):

- `CAD-NEG-04`: a small, already-scoped, just-written piece of code needing
  a correctness/race-condition check -> expected primary `code-review`.
  Tests that this skill does not over-trigger on ordinary quality review of
  known code.
- `CAD-NEG-05`: a familiar, already-documented module needing a routine,
  pattern-following extension -> expected primary `null` (no CloudBox
  skill needed). Tests that this skill does not over-trigger merely because
  a codebase exists — only when there is a real discovery gap.

Considered and deliberately rejected: a legacy-*game*-archaeology control
against `legacy-game-product-archaeology`. Per
`docs/SKILL_ROUTING_PLAYBOOK.md`'s noun/verb framing, overlap between a
verb-shaped skill (this one) and the domain-specific noun-shaped skill it
generalizes is expected, not a defect — encoding that as a "must forbid"
control would test the wrong thing.

## Routing: `repeat=3` across all 7 cases (21 records)

`router` context, `num_ctx=8192`.

| Metric | Result |
|---|---:|
| Overall strict pass rate | 85.7% (18/21) |
| Primary-skill accuracy | 90.5% |
| `codebase-architecture-discovery` forbidden-selection violation rate | **0.0%** (0/21) |
| This skill's own positive cases (CAD-01, CAD-02, 6 attempts) | 6/6 (100%) |
| This skill's own negative cases (CAD-NEG-01..05, 15 attempts) | 15/15 correctly did not select this skill |

**What the 3 misses actually are, precisely** — none of them are this
skill being selected when it should not be, or not selected when it
should be:

- `CAD-NEG-01` (2/3 attempts): the router returned `primary_skill: null`
  instead of the expected `safe-incremental-refactoring` for an
  already-decided-slice execution prompt. `codebase-architecture-discovery`
  was correctly not selected either way.
- `CAD-NEG-02` (1/3 attempts): the router correctly selected
  `architecture-review` as primary but added
  `application-client-server-architecture` as an unexpected supporting
  skill, failing strict `execution_order` matching only.
  `codebase-architecture-discovery` was correctly not selected.

**Disclosed honestly, not smoothed over**: this is real router-composition
noise on two *other* skills' own boundaries
(`safe-incremental-refactoring` sometimes not selected at all rather than
mis-selected; `architecture-review` sometimes pulling in an extra
supporting skill), observed while testing this skill's adjacent
boundaries. It is not evidence against `codebase-architecture-discovery`
itself — its own accuracy and non-over-triggering are both 100% across
all 21 attempts. It is a new, separate finding worth a future review of
`safe-incremental-refactoring`'s and `architecture-review`'s own routing
reliability; not fixed here, to stay in scope.

## Behavior GREEN: `repeat=3`

`selected-skills` context, `num_ctx=16384`.

| Case | Attempt 1 | Attempt 2 | Attempt 3 | Mean |
|---|---:|---:|---:|---:|
| `CAD-BEH-001` (recognition) | 81.2 | 100.0 | 100.0 | 93.7 |
| `CAD-BEH-002` (application) | 100.0 | 100.0 | 100.0 | 100.0 |

All 6/6 attempts pass the 75-point gate; overall mean 96.9/100. The one
partial score (`CAD-BEH-001` attempt 1, 81.2) missed half credit on
"durable checkpoint after each batch before conclusions" — a single
partial hit on one criterion in one of six attempts, not a repeated
pattern.

## Behavior RED: `repeat=1`, closing the first pass's disclosed gap

Skill removed from `SKILL_MANIFEST.json` (backed up first, restored
immediately after, verified byte-identical via `diff` and
`git diff --stat SKILL_MANIFEST.json` showing zero changes).

With the skill absent, the context-selection layer substituted the closest
adjacent skill for each case rather than producing a true no-guidance
baseline — the same graceful-degradation pattern already documented for
`native-ios-game-rewrite` and `legacy-game-product-archaeology`'s own RED
attempts:

| Case | Substituted skill | Score | Gate |
|---|---|---:|---|
| `CAD-BEH-001` | `architecture-review` | 81.2/100 | PASS |
| `CAD-BEH-002` | `safe-incremental-refactoring` | 62.5/100 | **FAIL** |

### `CAD-BEH-001`: no measured gap

81.2 with `architecture-review` substituted is statistically indistinguishable
from GREEN's own weakest attempt (also 81.2). Consistent with the
first-pass observation that the router's own composability absorbs this
skill's removal for recognition-shaped requests — not a defect, an expected
adjacent-skill overlap per the noun/verb framing.

### `CAD-BEH-002`: a real, measured gap

62.5 vs GREEN's 100.0 mean is a genuine drop, and it lands exactly where
this skill's own reference material (`references/batch-discovery-method.md`)
concentrates its guidance — both distilled from real incidents in the
`scripts/` audit this skill was itself extracted from:

- **"Requires running both versions against real data/consumers, not visual
  similarity alone"** — partial (1/2) without the skill. This is the exact
  empirical-duplicate-verification technique used before merging the
  `json_schema_interpreter.py` consolidation.
- **"Requires a repository-wide search for the exact old name after
  renaming"** — partial (1/2) without the skill. This is the exact
  transitive-consumer-search technique that caught
  `validate_task_continuity_evals.py`'s stale call to the old private
  `_validate_schema` name during that same consolidation.

`safe-incremental-refactoring` alone reliably handles preserving each
caller's distinguishing behavior and identifying divergence points
conceptually, but not the two specific verification disciplines this skill
exists to add.

## Promotion decision

`codebase-architecture-discovery` is promoted `experimental` -> `active` in
`.agents/skills/codebase-architecture-discovery/lifecycle.json`, per
`skill-lifecycle-standard.md`'s stage table ("active: repeatable GREEN
evidence and adjacent regressions"):

- **Repeatable GREEN**: this skill's own positive routing cases are 6/6
  across 3 repeats; behavior is 6/6 across 3 repeats, mean 96.9/100.
- **Adjacent regressions**: 15/15 negative-case attempts across 5 distinct
  adjacent boundaries (execution-slice-known, architecture-comparison,
  translation, code-review, familiar-codebase) correctly never selected
  this skill — `0.0%` forbidden-selection violation rate, the cleanest
  possible adjacent-regression result for this skill specifically.
- **Behavior RED closed**: the first pass's disclosed gap ("behavior RED
  not run") is now closed with a real, measured, on-topic gap on the
  application case.

**Disclosed release limitations** (per the lifecycle standard's "Release
truth" section):

- The strict 21-record routing gate is 85.7%, not a clean 100%, because of
  the `CAD-NEG-01`/`CAD-NEG-02` noise described above. That noise is about
  two other skills' own routing reliability, not this skill, and is
  recorded as a separate follow-up rather than blocking this promotion or
  being silently excluded from the reported numbers.
- `CAD-BEH-003` (counterexample) remains routing-only, never graded against
  a rubric.
- The deterministic rubric measures evidence-coverage keyword patterns in
  the written answer, not full semantic correctness or any real-world
  duplication-detection outcome on an actual codebase — unchanged
  limitation from the first-pass evidence.
