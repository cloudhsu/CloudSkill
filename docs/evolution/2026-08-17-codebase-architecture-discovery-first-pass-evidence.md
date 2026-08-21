# `codebase-architecture-discovery` — first-pass RED/GREEN evidence

Draft -> experimental promotion evidence. Single-attempt (repeat=1), not yet
release-grade repeat evidence. Provider: Claude Code CLI, `sonnet` alias.
`num_ctx=8192` (routing), `num_ctx=16384` (behavior).

## Routing

Cases: `evals/runtime/cases/cad-routing.json` (CAD-01, CAD-02, CAD-NEG-01,
CAD-NEG-02, CAD-NEG-03), mirroring `evals/skill-routing-cases.csv`.

| Run | overall_pass_rate | primary_skill_accuracy |
|---|---:|---:|
| GREEN (skill present, `router` context) | 1.0 (5/5) | 1.0 |
| RED (skill removed from `SKILL_MANIFEST.json`, restored + diff-verified byte-identical after) | 0.2 (1/5) | 0.4 |

### The real finding: CAD-01

Without the skill, the router selected `safe-incremental-refactoring` for a
prompt describing an unfamiliar 60-file subsystem about to be extended, with
no specific slice or decision yet identified:

> "The deliverable is how to safely begin adding a new feature into an
> unread, brownfield 60-file subsystem without breaking existing behavior,
> contracts, or recovery paths — this is exactly the decision boundary
> safe-incremental-refactoring governs..."

This is a genuine, non-fabricated gap: the baseline model recognized the
brownfield/legacy quality of the request but reasoned straight into an
*execution*-shaped skill instead of recognizing that no slice was defined
yet — precisely the premature-execution failure mode
`codebase-architecture-discovery` exists to intercept. With the skill
present, GREEN correctly selected `codebase-architecture-discovery` for the
same prompt.

### CAD-02: infrastructure failure, not a semantic finding

The RED attempt for CAD-02 failed with `ClaudeCLIError`:
`terminal_reason: "error_max_structured_output_retries"`,
`"Failed to provide valid structured output after 5 attempts"`. This is an
infrastructure/provider-layer failure (the routing schema constraint was not
satisfied after retries), not evidence about the skill's necessity. Not
retried — the RED gap was already established by CAD-01, and a single
transient failure does not by itself justify more model calls per this
repo's own "first verify... repetitions show a stable pattern" discipline.
Disclosed as `BLOCKED`, counted against the RED pass rate honestly (a
routing decision that did not complete is a failure to route, regardless of
cause) rather than excluded from the denominator.

### CAD-NEG-01/02/03: unaffected either way

All three negative/adjacent-boundary cases produced the same correct result
with or without the skill present (`safe-incremental-refactoring` correctly
not selected for an already-decided slice in one baseline attempt though
the model actually returned `primary_skill: null` reasoning it was "trivial
mechanical relocation"; `architecture-review` correctly selected for a
single-decision comparison; no skill correctly selected for a translation
request). Consistent with these being adjacent-boundary controls, not this
skill's own territory — a baseline already handling them correctly is
expected, not a sign the controls are uninformative.

## Behavior

Cases: `CAD-BEH-001` (recognition), `CAD-BEH-002` (application). `CAD-BEH-003`
is routing-only (counterexample) and is not graded against a rubric.
Rubrics: `evals/runtime/cases/behavior-rubrics.json`.

| Case | Score | All criteria |
|---|---:|---|
| `CAD-BEH-001` | 100.0 / 100 | 4/4 passed (staged batches, durable checkpoint, deferred conclusion, map-shaped output) |
| `CAD-BEH-002` | 100.0 / 100 | 4/4 passed (empirical verification, divergence testing, transitive-name search, preserved distinction) |

Behavior RED (without the skill) was not run this pass — routing-layer RED
already established the real baseline gap, and the additional cost of two
more live model calls was judged not to add proportional new information
for a first-pass draft->experimental promotion. Disclosed as a deliberate
scope limit; a materially larger revision to this skill should include it.

## What this evidence does and does not support

- Supports: `codebase-architecture-discovery` closes a real, observed
  routing gap (premature execution-skill selection on an undefined-slice,
  unfamiliar-codebase prompt) and, when selected, produces output meeting
  every stated required behavior in both graded scenarios.
- Does not support: release-grade repeat-count evidence (this is
  single-attempt), an adjacent-regression sweep beyond the 3 NEG cases
  already included, or promotion to `active` (needs GREEN repeated across
  attempts and a broader regression set, per `skill-lifecycle-standard.md`).
- Does not support: any claim about real-world duplication-detection
  outcomes on an actual codebase — the rubric measures deterministic
  evidence-coverage in the written answer, not whether a real refactor
  recommendation was correct.

Release judgment: evidence supports promoting `codebase-architecture-discovery`
from `draft` to `experimental`; it does not by itself support `active`.
