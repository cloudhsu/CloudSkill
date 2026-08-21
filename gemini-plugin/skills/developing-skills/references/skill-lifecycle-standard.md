# CloudSkill lifecycle standard

Use this standard for every new skill and every material change to an existing skill.

## Lifecycle stages

| Stage | Meaning | Minimum evidence |
|---|---|---|
| `draft` | Scope and ownership are still being defined. | Proposal, overlap review, non-trigger boundary |
| `experimental` | The skill is routable but not yet release-proven. | RED baseline, routing cases, recognition/application/counterexample cases |
| `active` | The skill has repeatable GREEN evidence and adjacent regressions. | Local or CI execution evidence, release limitations |
| `stable` | The skill has survived multiple releases without material ambiguity. | Historical regressions, context-cost review, maintenance review |
| `deprecated` | New routing should move elsewhere. | Replacement, migration guidance, negative routing evidence |

Do not promote a skill because Markdown validates. Promotion requires behavior evidence.

## Standard creation sequence

1. Classify the observed failure layer:
   - skill instructions,
   - router or retrieval,
   - Eval case,
   - grader,
   - Runner/runtime,
   - local environment,
   - packaging or release.
2. Search existing owners before creating a new skill.
3. Record a RED baseline before editing.
4. Define:
   - trigger,
   - non-trigger,
   - authoritative scope,
   - required behavior,
   - forbidden behavior,
   - required output,
   - companion boundaries,
   - stop/escalation conditions.
5. Create positive, adjacent, and counterexample routing evidence.
6. Create recognition, application, and counterexample behavior cases.
7. Make the smallest responsible change.
8. Run the same RED case, adjacent regressions, structural checks, and executable Runtime Evals where applicable.
9. Freeze one candidate packet and run the policy-declared managed sub-agent
   review. Codex uses Luna/Sol; Claude Code prefers Sonnet 5/Opus 5 and may use
   the corresponding 4.8 generation only when 5 is unavailable. Reviewers are
   read-only and independent, use the same packet, and record exact model and
   run identity. A missing required review or a `FAIL`, `BLOCKED` or
   `MANUAL_REQUIRED` disposition blocks promotion and release.
   Bind behavior execution to a candidate packet ID, then bind final semantic
   review to a second packet containing that candidate manifest plus execution
   evidence. Use `scripts/freeze_skill_review_packet.py`; do not hash an
   evidence file into a packet whose own ID it must contain.
10. Refresh lifecycle evidence with:

   ```bash
   python scripts/manage_skill.py refresh --all
   ```

11. Audit before commit:

   ```bash
   python scripts/manage_skill.py audit --check
   ```

## Brownfield implementation guard

Skill distillation or optimization does not authorize rewriting the product that
supplied its evidence. When the target program already exists or has previously
been refactored, first map its current responsibilities, public and operational
contracts, compatibility seams, state ownership, known defects and executable
baseline. Extend the existing architecture through the smallest coherent slice
and preserve behavior unless a separately authorized change says otherwise.

A whole rewrite is forbidden unless the user explicitly authorizes that scope.
Do not infer rewrite authority from old code, missing tests, a cleaner proposed
architecture, or creation of a new Skill. If current structure cannot be safely
established, stop at analysis or characterization tests instead of replacing it.
Use `safe-incremental-refactoring` for the implementation plan and evidence.

## Continuous evolution rules

A single small-model failure is not enough to rewrite a skill. First verify:

- required context was actually loaded,
- the output contract was valid,
- the case has one clear deliverable owner,
- repetitions show a stable pattern,
- the grader did not count internal planning as final evidence,
- an adjacent skill is not equally plausible.

Use the lifecycle `review_triggers` to decide when a skill must be reviewed.

## Artifact ownership

| Need | Authoritative artifact |
|---|---|
| Semantic judgment and workflow | `SKILL.md` |
| Heavy reusable knowledge | `references/` |
| Reusable output form | `assets/` |
| Mechanical consistency | script or validator |
| Route selection | description, routing map, routing cases |
| Behavior expectation | behavior cases and rubric |
| Stage and evidence inventory | `lifecycle.json` |
| Machine-local execution evidence | ignored `.local/` bundle |

Do not duplicate mutable rules across all of these artifacts.

## Release truth

Report each evidence class separately:

- structural validation,
- routing execution,
- behavior execution,
- local environment validation,
- CI validation,
- install smoke test,
- release/tag/push status.

A generated scaffold is not an active skill. A passing static validator is not a behavior pass.
Runtime Eval provider calls and CLI model overrides do not replace the managed
model-selected sub-agent semantic review gate when that interface is available.
Record exact selected or returned model and agent/run identity so later handoff
does not have to infer who performed the review.
The review packet must also identify whether the target is an existing or
previously refactored implementation. For brownfield targets, a proposal that
replaces the implementation without explicit rewrite authorization is blocking.

A `release:` commit is not a release. Tag and GitHub Release creation are part of
the same release step, not a follow-up: after pushing a `release:` commit, in the
same turn, create the matching `git tag`, push it, then `gh release create`, then
confirm both with `gh release list` before reporting the release as done. In a
session that ships several releases back-to-back, re-run that confirmation for
every version shipped in the run, not just the latest -- an omitted tag/Release
repeats identically each time rather than surfacing on its own (2026-08-15: 5
consecutive versions across 2 repos shipped commits with no tag or Release,
undetected for a whole session until the user separately noticed).
