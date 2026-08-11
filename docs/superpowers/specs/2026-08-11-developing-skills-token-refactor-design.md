# Developing Skills Token Refactor Design

Status: approved design; implementation not started.

## Goal

Reduce the default context cost of `developing-skills` without changing its
routing contract, lifecycle stage, required behavior, privacy boundary, or
release truthfulness.

## Scope

This increment is a single-Skill pilot. It may reorganize
`.agents/skills/developing-skills/SKILL.md` and its existing direct references,
plus Behavior cases, lifecycle evidence, validators, manifest, and handoff
records required to prove the refactor. It does not refactor other large Skills,
change the manual ZIP/legacy workflow, version the product, push, or release.

## Content boundary

Keep in `SKILL.md`:

- the routing contract and core success criterion;
- the lifecycle and RED/GREEN discipline;
- the authoritative-owner and smallest-change decision flow;
- privacy, evidence-truth, stop, and release boundaries that apply on every run;
- a direct reference map that states exactly when each supporting file is read.

Move or consolidate in direct `references/` files:

- interaction-capture and disconnected export/import detail;
- multi-interaction and project-history mining detail;
- lifecycle promotion and release-checklist detail;
- templates, examples, and format-specific mechanics already owned by assets or
  references.

Do not duplicate a mutable rule in both the main file and a reference. A short
main-file invariant may point to a detailed procedure, but the authority must be
clear.

## Behavioral contract

The refactor must preserve:

1. routing for creation, modification, evaluation, mining, import review, and
   release of CloudSkill Skills;
2. explicit interaction-capture shorthand and private/manual-review behavior;
3. deterministic clustering before model synthesis;
4. RED-before-change and truthful GREEN/NOT-RUN reporting;
5. smallest authoritative owner selection and adjacent-Skill regression;
6. manual ZIP, unsupported retention, and legacy recovery while the exchange
   format remains unstable;
7. explicit stop or conservative fallback when privacy/config ownership cannot
   be proved.

## Measurement

Record the pre- and post-refactor physical line count, UTF-8 byte count, word
count, and an explicitly labeled approximate token estimate for `SKILL.md`.
The estimate is comparative evidence, not a provider billing measurement.

Success requires a material reduction in default-loaded text with no loss in
the focused Behavior cases. No fixed percentage is imposed: correctness takes
priority, and a negligible reduction is grounds to stop rather than force a
harmful split.

## Verification

1. Establish a pre-change semantic baseline for representative direct and
   conditional workflows.
2. Add a failing structural/reference-loading check before moving content.
3. Refactor only enough to make that check pass.
4. Run the same semantic cases against the refactored Skill, including adjacent
   routing controls.
5. Run lifecycle, Behavior-contract, packaging, install, documentation, and
   complete deterministic repository checks.
6. Obtain an independent exact-tip review of information loss, misleading
   reference routing, duplication, privacy, and token claims.

Provider-backed Runtime Eval execution must be reported as `NOT RUN` unless it
is actually executed.

## Stop conditions

Stop and retain the current structure if the split requires routine loading of
all references, makes a required safeguard discoverable only by guesswork,
changes routing, weakens privacy or evidence rules, or saves negligible context
at disproportionate maintenance cost.

## Delivery

Commit the pilot as an independently reviewable candidate on the existing
feature branch. Present evidence before any version, push, merge, or release.
Other Skills over 200 lines remain future candidates and require their own
evidence before applying this pattern.
