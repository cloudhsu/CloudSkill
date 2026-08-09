# CloudSkill evolution handoff

This is the operational entry point for a new conversation or coding agent that must continue CloudSkill evolution without reconstructing the project from chat history.

## Read order

1. `AGENTS.md`
2. This file
3. `docs/CLOUDSKILL_DESIGN_AND_FLOW.md`
4. `docs/CLOUDSKILL_CHANGE_HISTORY.md`
5. `.agents/skills/developing-skills/SKILL.md`
6. `.agents/skills/runtime-evaluation-engineering/SKILL.md`
7. `.agents/skills/local-runtime-eval-debugging/SKILL.md`
8. `evals/runtime/contracts/behavior-output-contract.json`

## Current repository state

- Repository: `cloudhsu/CloudSkill`
- Active review branch: `fix/skill-lifecycle-and-ci-20260809-013048`
- Pull request: `#1`
- Current baseline commit for this increment: `a910b76` (already includes the
  Behavior contract consumer-registry closure; the grader-precision hotfix
  below is uncommitted working-tree state on top of it).
- PR remains Draft until local Runtime Eval evidence is interpreted and accepted.
- Local diagnostic bundles live under `.local/runtime-evals/` and must not be committed.

## Latest verified evidence before this increment

Bundle: `CloudSkill-local-eval-review-local-review-20260809-113507.zip`

- Pipeline: SUCCESS
- Evaluation gate: PASS
- Provider/model: Ollama `qwen3:4b`
- Routing strict pass: 100%, contract validity: 100%, primary accuracy: 100%
- R02 routing: 3/3 — the prior displacement by `equipment-control-architecture`
  is resolved; `equipment-domain-modeling` now returns correctly.
- R05A/R05B/R05C/R07 routing: 3/3 each
- Raw R07 Behavior: 74/100 (gate FAIL at n=1)
- Refined R07 Behavior: 88/100, accepted, no planning-leak
- Re-graded offline (no new model call) after the grader-precision hotfix
  below: raw 74→78 (now passes standalone), refined 88→100. See
  `docs/CLOUDSKILL_CHANGE_HISTORY.md` 2026-08-09 "R07 Behavior grader
  precision hotfix" for full evidence and the regression fixture added to
  `scripts/validate_behavior_runtime_evals.py`.

## Open evolution items

1. ~~Restore the R02 `code-review` plus `equipment-domain-modeling` boundary~~ — resolved, confirmed 3/3 in the 20260809-113507 bundle.
2. ~~Use a structured `{ "final": "..." }` Behavior output contract~~ — resolved; contract ID/fingerprint confirmed consistent across environment.json and both raw/refined JSONL records.
3. ~~Reject unstructured refinement candidates~~ — resolved; the accepted refined R07 answer passes `final-answer-discipline` (no planning leak) in the latest bundle.
4. Run a fresh Ollama Runtime Eval (`--force-eval`) to get ≥3 repeat behavior evidence for R07 under the corrected rubric. Deferred at the user's explicit request for this increment — do not run Ollama until asked.
5. Investigate whether the Refiner Prompt should be strengthened to preserve raw's concrete authority identifiers (`ChamberStateAuthority`, `WaferCustodyAuthority`, `FencingToken`, exact `wafer location`/`occupancy` phrasing) instead of paraphrasing them away. Currently n=1 evidence only — do not change the Refiner Prompt until repeat evidence confirms this is systematic, not one sample's variance.
6. Run the quota-conscious Codex comparison after Codex access is available.
7. Keep provider results separate; do not average Ollama, Codex, and Claude scores.
8. A `claude` Runtime Eval provider (Claude Code CLI headless, see
   `scripts/claude_eval_adapter.py`) was added but has not yet been exercised
   against a live `claude` process in this repository. Its first real
   `./cloudskill-eval-claude` smoke run is the point where the `--output-format
   json` parsing assumption in `_extract_result_text()` is actually confirmed,
   not assumed. Run it deliberately (it spends Claude usage/quota) before
   trusting any `claude`-provider evidence.
9. The Eval Inbox import path (`scripts/import_eval_candidates.py` +
   `.agents/skills/developing-skills/assets/export_eval_candidate.py`) has
   only been exercised with synthetic smoke-test candidates, never a real
   exported-from-an-external-session zip. Its first real use is the point
   that gets confirmed, not this increment.

## Standard continuation commands

Static/status only:

```bash
./cloudskill-resume --status
python3 scripts/run_all_checks.py
```

Fresh Ollama evidence:

```bash
./cloudskill-resume --provider ollama --force-eval
```

Fresh Codex evidence:

```bash
codex login status
./cloudskill-resume --provider codex --force-eval
```

Fresh Claude evidence:

```bash
claude auth status
./cloudskill-resume --provider claude --force-eval
```

Resume after interruption without forcing a second completed run:

```bash
./cloudskill-resume --provider ollama
# or
./cloudskill-resume --provider codex
# or
./cloudskill-resume --provider claude
```

## Evidence handoff contract

The normal handoff artifact is the newest:

```text
.local/runtime-evals/CloudSkill-local-eval-review-local-review-*.zip
```

Review in this order:

1. `STATUS.json`
2. `REVIEW_SUMMARY.md`
3. `routing-summary.json` and `routing-report.md`
4. `behavior-raw-summary.json` and raw JSONL
5. `behavior-refined-summary.json` and refinement metadata
6. `source-inventory.json`
7. `environment.json`
8. `run.log`

Do not infer Skill quality from a downstream score when an earlier parser, prompt, context, provider, or refinement-contract defect invalidates that evidence.

## Safety constraints

- Never commit `.local/`, credentials, auth output, raw private transcripts, or local machine secrets.
- Never apply or drop an existing stash automatically.
- Preserve raw model output before extraction or refinement.
- Run deterministic validation before spending model quota.
- A pipeline success and an evaluation-gate success are different states.
- Do not weaken a grader merely to turn a known failure green.
- Do not create a new Skill until an existing owner and composition rule have been ruled out.

## Behavior output contract authority

Read these before modifying Behavior or refinement output handling:

1. `evals/runtime/contracts/behavior-output-contract.json`
2. `scripts/behavior_output_contract.py`
3. `scripts/validate_behavior_contract.py`

The JSON contract is authoritative. Do not add a new prompt-marker list to
another Validator. Runtime and Refiner prompts, schemas, extraction, minimum
lengths, planning-leak detection, contract ID, and fingerprint must use the
shared adapter.

The Review ZIP should contain the same contract ID and fingerprint in its
environment and Behavior/refinement records. A mismatch is a harness defect,
not a model-quality result.

### Consumer registry

The authoritative contract field `required_consumer_paths` lists every module
that must import the shared adapter. Before changing Behavior output handling,
confirm that the target module is registered or intentionally outside the
contract boundary.

Do not validate a contract consumer by searching it for a contract ID, legacy
label, Prompt sentence, or function name. Validate imported constants and
executable behavior through `scripts/validate_behavior_contract.py`.

When adding a new consumer:

1. register its repository-relative path in
   `evals/runtime/contracts/behavior-output-contract.json`;
2. import from `behavior_output_contract`;
3. add an executable integration assertion to the dedicated Validator;
4. run the positive propagation and negative injected-drift tests.

## New-conversation bootstrap

Copy this into a new conversation or agent task:

```text
Continue CloudSkill evolution from the repository state described in CLOUDSKILL_AGENT_HANDOFF.md.
Read AGENTS.md, docs/CLOUDSKILL_DESIGN_AND_FLOW.md, docs/CLOUDSKILL_CHANGE_HISTORY.md,
and the developing-skills/runtime-evaluation-engineering/local-runtime-eval-debugging Skills.
Treat the newest local Runtime Eval ZIP as evidence, classify the earliest failing layer,
preserve raw outputs and local stashes, make the smallest evidence-driven change,
run deterministic checks first, and produce an interruption-safe increment plus updated handoff history.
Do not merge PR #1 or mark it ready until the current release criteria are explicitly satisfied.
```

## Eval Inbox import path

`.local/eval-inbox/` in this repository is initialized (via
`scripts/install.sh --config-only`, self-referential: `.cloudskill/config.local.json`
points `cloudskill_repository` and `eval_inbox` at this repository itself).
Structure: `candidates/`, `manual-review/`, `processed/`, `rejected/`,
`imports/` (drop zips exported from a disconnected/external session here),
`imports/processed/` (already-merged zips, kept for audit).

To merge zips dropped in `imports/`:

```bash
python3 scripts/import_eval_candidates.py
# or, to preview without writing:
python3 scripts/import_eval_candidates.py --dry-run
```

The counterpart export tool for a disconnected/external session (no
reachable CloudSkill repository on that machine) is
`.agents/skills/developing-skills/assets/export_eval_candidate.py` — see
`.agents/skills/developing-skills/references/interaction-eval-capture.md` and
`INSTALL.md` section 8b. This did not add a new Skill: it extends
`developing-skills`' existing `整理成正向/負向案例` capture flow with a
config-free fallback, per the "do not create a new Skill until an existing
owner is ruled out" rule.

Importing into `candidates/`/`manual-review/` is still only evidence
staging. Converting Inbox candidates into formal `evals/` cases remains a
separate, explicit `developing-skills` batch-review step (INSTALL.md section
9) that this import tool does not perform.

## Release / merge-to-main criteria

Do not merge PR #1 (or mark it ready for review) until ALL of the following
hold at the same time. Treat this as the concrete definition of "the current
release criteria are explicitly satisfied" referenced elsewhere in this
document.

1. `python3 scripts/run_all_checks.py` passes on the PR branch tip.
2. GitHub Actions `validate` checks are green on the PR branch tip (`gh pr
   checks 1`).
3. The R02/R05A/R05B/R05C/R07 routing suite is 3/3 (100%) on the most
   recently accepted Ollama Runtime Eval bundle.
4. R07 Behavior has **at least 3 repeat attempts** on Ollama (not the current
   n=1) with a stable pass, per the repetition policy in
   `runtime-evaluation-engineering/references/case-and-grader-design.md`
   ("Local small-model routing: at least three repetitions"). A single
   sample passing is diagnostic evidence, not release evidence.
5. At least one Codex comparison run (`./cloudskill-eval-codex`) has been
   executed and interpreted, OR an explicit, dated reason is recorded here
   for why it was deferred (for example, quota unavailable).
6. If a `claude` provider run was added in this increment, its first live
   smoke run (`./cloudskill-eval-claude`) has been executed at least once and
   the `--output-format json` parsing assumption in
   `scripts/claude_eval_adapter.py` is confirmed against real output, OR an
   explicit, dated reason is recorded here for why it was deferred.
7. Ollama, Codex, and Claude results are reported separately in the
   accepted evidence — never averaged into one provider-independent score.
8. `docs/CLOUDSKILL_DESIGN_AND_FLOW.md`, `docs/CLOUDSKILL_CHANGE_HISTORY.md`,
   and this handoff reflect the final accepted state — no "Unresolved" bullet
   that was actually resolved should remain unresolved in the text.
9. The user has reviewed the PR diff and raised no open objection.

When all nine hold, mark the PR ready for review and merge — do not do
either step silently; confirm with the user first even if the criteria
above are met, since merging to `main` is not easily reversible.

## Completion criteria for an evolution round

An evolution round is complete only when it provides:

- the code or Skill change;
- deterministic validation;
- one current Runtime Eval bundle or an explicit reason it was not run;
- an interpretation separating harness defects from model/Skill defects;
- updated design/history/handoff documentation;
- a safe commit/push path through `cloudskill-resume`.
