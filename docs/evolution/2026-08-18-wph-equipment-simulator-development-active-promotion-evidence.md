# `wph-equipment-simulator-development` active-promotion evidence

## Context

`wph-equipment-simulator-development` was imported and structurally onboarded
in v7.6.28 as `stage: experimental`, `evolution-pack` (private) distribution
tier. That release explicitly disclosed live routing and behavior model
evaluation as `NOT RUN` and said not to promote past `experimental` without
it. This document records that evidence, gathered the same day.

## Routing evidence

`evals/runtime/cases/wph-equipment-simulator-development-routing.json`,
`--provider claude --context-mode router --repeat 3`:

| Case | Type | Result |
|---|---|---|
| `WPH-SIM-REC-001` | positive | 3/3 routed to `wph-equipment-simulator-development` |
| `WPH-SIM-CTR-001` | negative | 3/3 correctly did not route to it |

Deterministic grader (`scripts/grade_runtime_evals.py`): 6/6 (100%), gate
`passed: true`. Raw run: `.local/runtime-evals/wph-routing-r3.jsonl`; summary:
`.local/runtime-evals/wph-routing-r3-summary.json`; report:
`.local/runtime-evals/wph-routing-r3-report.md`.

## Behavior evidence

`evals/behavior/cases/wph-equipment-simulator-development.json`,
`--eval-kind behavior --context-mode selected-skills --repeat 3`. The
`WPH-SIM-REC-001`/`WPH-SIM-CTR-001` pair ran through the committed routing
suite; `WPH-SIM-APP-001` (application type) required an ad-hoc, non-committed
routing-suite stub to drive it through the tool (the same shape gap that
already exists for `codebase-architecture-discovery`'s own `CAD-BEH-002`,
whose ID also does not appear in its committed routing suite).

| Case | Type | Result (3/3 attempts) |
|---|---|---|
| `WPH-SIM-REC-001` | recognition | `completed`, 3/3 |
| `WPH-SIM-APP-001` | application | `completed`, 3/3 |
| `WPH-SIM-CTR-001` | counterexample | `no-skill`, 3/3 (correct decline) |

No automated numeric behavior rubric exists for this skill yet (unlike, for
example, `equipment-control-architecture`'s `R07` rubric or
`codebase-architecture-discovery`'s scored evidence). This pass instead
manually read the full transcript of each completed attempt and checked it
against the case's own `required_behaviors`/`forbidden_behaviors` list:

- **`WPH-SIM-REC-001`**: correctly named the applicable workflow, separated
  event authority from GUI projection, cited the actual non-negotiable
  invariants (no unconfirmed Load Lock/VCE, no early PM entry, no Tray ID
  reuse, no stale T1/T2, no W IDs on PM views, elapsed-time/GUI-ack is not
  physical evidence) rather than paraphrasing them generically, and marked
  unresolved items explicitly instead of inventing facts.
- **`WPH-SIM-APP-001`**: produced a change package that reserved CT/EFEM
  resources without overlap, added the previously-undocumented A-in/B-out
  priority rule the skill's own invariants require, separated confirmed vs.
  provisional timing parameters, and — notably — explicitly disclosed "Build/
  SelfTest evidence: Not executed" rather than fabricating a pass, consistent
  with this repository's evidence-honesty discipline.
- **`WPH-SIM-CTR-001`**: declined to select the skill with an explicit,
  correctly-reasoned rejection referencing the absence of any equipment/WPH
  domain cue, and did not inject semiconductor-specific vocabulary into the
  generic dashboard task.

This is disclosed as a lighter evidence class than a scored rubric — it
satisfies `skill-lifecycle-standard.md`'s stated minimum for `active`
("Local or CI execution evidence, release limitations") but not the heavier
bar some other active skills happen to also clear. Raw run:
`.local/runtime-evals/wph-behavior-r3.jsonl` (REC/CTR) and
`.local/runtime-evals/wph-behavior-app-r3.jsonl` (APP).

## Adjacent-regression evidence

Adding a new skill changes `SKILL_MANIFEST.json` and the router's skill
catalog, which every routing decision loads — the same reasoning that
required a canary regression check for the 2026-08-18 router-fix earlier
this session. Ran the full 10-case canary suite at `repeat=3`
(`evals/runtime/cases/canary.json`, `--context-mode router`):

- 28/30 attempts passed the strict grader outright.
- 2/30 attempts (`R05C-component-and-recovery-composition` attempt 2,
  `R08-historical-interaction-optimization` attempt 2) returned a Claude CLI
  `structured_output_retry_exhausted` error — a Runner/Context-layer failure
  per `skill-lifecycle-standard.md`'s own failure-layer classification, not a
  routing-content defect. Both cases were re-run immediately afterward
  (`--repeat 2` targeted at just those two case IDs) and both succeeded with
  the correct `primary_skill`/`execution_order` on every attempt, confirming
  the original failures were transient rather than reproducible.
- The two closest semantic neighbors to the new skill —
  `equipment-control-architecture` (`R05B`, `R07`) and
  `equipment-domain-modeling` (`R05A`, `R05C`) — showed zero drift across
  every attempt.

Deterministic grader on the original run reported `gate.passed: false`
(93.3%, driven entirely by the 2 transient errors above); the retry
confirms 30/30 semantic correctness. Raw run:
`.local/runtime-evals/wph-canary-adjacent-r3.jsonl`; retry:
`.local/runtime-evals/wph-canary-retry.jsonl`; summary:
`.local/runtime-evals/wph-canary-adjacent-r3-summary.json`; report:
`.local/runtime-evals/wph-canary-adjacent-r3-report.md`.

## Promotion decision

`lifecycle.json`: `stage` `experimental` -> `active`.

Reasoning: `skill-lifecycle-standard.md`'s table requires, for `active`,
"repeatable GREEN evidence and adjacent regressions" with minimum evidence
"Local or CI execution evidence, release limitations." Routing (100%,
repeat=3), behavior (9/9 completed and manually verified across all 3 case
shapes, repeat=3), and adjacent regression (30/30 semantically correct,
repeat=3 with one transient-error retry) together satisfy that stated bar.

**Explicitly not resolved by this promotion**: the `evolution-pack`
(private) distribution-tier classification recorded in
`config/skill-distribution.json` at import time was Claude's own judgment,
not yet confirmed by the user (tracked separately, outside this file, not
blocking stage promotion — stage and distribution tier are independent
axes). A numeric behavior rubric was not authored this pass; if one is
written later and produces a materially different picture than this pass's
manual review, that is itself a `next_review_triggers` condition.

Claude Code CLI 2.1.233, `sonnet` alias.
