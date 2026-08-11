# Developing Skills token-refactor evidence

Status: post-6.3 candidate; version, push, merge, and release not authorized.

## Default-context measurement

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Physical lines | 246 | 156 | -36.6% |
| Whitespace words | 2,014 | 961 | -52.3% |
| UTF-8 bytes | 15,062 | 7,662 | -49.1% |
| Approximate tokens (`ceil(bytes / 4)`) | 3,766 | 1,916 | -49.1% |

The token values are comparative estimates, not tokenizer output or provider
billing measurements. Conditional references are loaded only when their named
workflow requires them, so this table measures default Skill text rather than a
complete task's context.

## RED/GREEN chain

- Structural RED at `8e9fe67`: the original 15,062-byte main file exceeded the
  new 10,500-byte default-context budget.
- Initial refactor GREEN: context validator passed at 7,278 bytes.
- Complete-suite regression 1: lifecycle validation failed because the shared
  `draft -> experimental -> active -> stable -> deprecated` markers had been
  moved out of default context. Commit `ba19638` restored the compact invariant.
- Complete-suite regression 2: interaction validation failed because the exact
  `manual-review` and `raw or complete transcript` invariants were no longer in
  default context. Commit `e0c03b2` restored them without duplicating the full
  capture procedure.
- Final deterministic context result: 7,662 bytes, inside budget.
- Final complete deterministic repository suite: PASS.

These failures were useful information-loss tests: mandatory universal
safeguards remained in the main Skill, while conditional mechanics stayed in
direct references.

## Semantic forward tests

- `DEVSK-BEH-011` through `DEVSK-BEH-016`: 6/6 PASS using only the main Skill
  and the direct reference selected for each prompt.
- Correct reference selection: interaction capture for 011–014, conversation
  optimization for 015, lifecycle standard for 016.
- Hidden mandatory safeguard/information loss: none found.
- `PROC-BEH-008`: PASS after the user's priority correction for lifecycle-first
  ownership, evidence-driven transitions, proportional planning, bounded
  detail, risk replan, stale-step invalidation, and evidence preservation.
- High/Medium semantic findings: none.
- Provider-backed Runtime Eval corpus: NOT RUN.

## Planning authority result

Fixed priority: lifecycle and the complete dynamic feedback loop first;
evidence and verification second; token/context savings third. The two detected
information-loss regressions were corrected instead of accepting a lower token
count with weaker lifecycle or capture evidence.

`development-process-tailoring` remains the sole and highest lifecycle/plan
authority. Every planned increment selects its lifecycle profile first so the
dynamic feedback loop remains intact. Small stable work projects that lifecycle
into a lightweight execution plan; medium work with an approved design may
delegate bounded implementation detail; uncertain, long-running, externally
coupled, or high-risk work persists the lifecycle plan before stage-specific
detail. New risk creates a plan revision and invalidates only affected steps.

## Scope retained

The Skill name, description, lifecycle stage, privacy boundary, manual ZIP,
unsupported retention, legacy recovery, RED/GREEN discipline, and release-truth
boundary remain unchanged. No other large Skill was structurally refactored.
