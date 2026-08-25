# CloudSkill evolution handoff

> Standing implementation boundary (2026-08-19): source products may already
> be refactored. Distillation does not authorize rewriting them. Discover the
> current architecture and behavior first, preserve compatibility, and use the
> smallest coherent slice; whole rewrites require explicit user authorization.

## Current increment — 7.7.0 release cut: unified hook logging, Windows-native directly-wired hooks, technical-case-content-generation Skill, equipment-porting candidate merge, routing-cue fix (2026-08-25)

PRs #99–105 plus one directly-pushed hook-logging commit (`36b611f`,
CI-verified). Full detail: `CHANGELOG.md`'s 7.7.0 entry; validation
evidence: `docs/releases/7.7.0-pre-release-evidence.md`. Minor bump
(`7.6.39` -> `7.7.0`): 6 public Skills (`framework-design`,
`equipment-control-architecture`, `equipment-domain-modeling`,
`codebase-architecture-discovery`, `code-review`,
`safe-incremental-refactoring`) each gained a new behavior case from
9 real equipment-porting candidates; the bundled-hook mechanism gained
Windows-native coverage for the 3 hooks this repository wires directly
(not through `install_skill_hooks.py`'s manifest); `using-cloudbox-skills`
gained a real routing-defect fix (closes `cloudbox-skills` #15). A new
private-tier Skill, `technical-case-content-generation`, closes the
content-generation gap next to `game-marketing-and-monetization` but does
not itself justify the public-facing minor classification -- the public
Skill extensions above do, independently. `python3 scripts/
run_all_checks.py` PASS at the release tip.

**Known gap, tracked not hidden**: 6 of the 9 new equipment-porting cases
and the 3 new hook-logging Eval cases (`CAG-BEH-017`, `DEVSK-BEH-027`,
`CAGD-BEH-004`) have no durable/repeatable formal-pipeline grading yet --
ad hoc `codex exec`/`claude -p` spot checks only. `technical-case-
content-generation` ships case/contract-layer RED evidence only; live
Skill/behavior execution is `NOT RUN`.

**Next**: public-side push to the `CloudSkill` mirror is a separate,
explicit step -- see below for whether it happened this increment.

## Previous increment — 7.6.39 release cut: deep-read duplicate/overlap scan, verified before acting (2026-08-23)

PRs #94–98. Full detail: `CHANGELOG.md`'s 7.6.39 entry; validation
evidence: `docs/releases/7.6.39-pre-release-evidence.md`. Key decision:
a deep-read overlap scan's detailed report file was lost (subagent
worktree torn down before retrieval, only its inline summary survived) --
rather than acting on the summary at face value, each of its top findings
was independently re-verified via direct grep/Read (or a properly-
redispatched, inline-reporting subagent) before any fix was made. 6 of 7
findings confirmed and fixed; 1 confirmed accurate but deliberately left
alone (its natural owner sits at a frozen budget ceiling, and forcing the
consolidation would have cost each Skill's standalone readability for
low value). `python3 scripts/run_all_checks.py` PASS at the release tip.

The report-loss incident itself was root-caused and closed:
`coding-agent-project-governance` gained a rule (new case `CAG-BEH-016`)
requiring read-only investigation subagents to report full findings
inline in their final message, never solely to a worktree-local file --
applied successfully to the retry that produced this release's own
evidence.

**Known gap, tracked not hidden**: the 3 new Eval cases this cycle
(`CAG-BEH-016`, `DOC-BEH-013`, `PROC-BEH-017`) are schema-validated only,
zero real model-behavior execution -- tracked in the standing Vikunja
`cloudbox-skills #7` statistical-rigor backlog, not a new item. 3 of the
5 merged PRs changed only citations/cross-references, no new
required/forbidden-behavior fields, so no case was needed for those.

**Next**: public-side push to the `CloudSkill` mirror is a separate,
explicit step -- see below for whether it happened this increment.

## Previous increment — 7.6.38 release cut: 2 new hooks, session self-audit, coding-agent-project-governance architecture split (2026-08-23)

PRs #80–90. Full detail: `CHANGELOG.md`'s 7.6.38 entry; validation
evidence: `docs/releases/7.6.38-pre-release-evidence.md`. Key decision:
resolved a 3-way "should governance split by domain (product/art/code)"
discussion by rejecting a shared governance-content core (product/art/code
risk taxonomies are genuinely different, not accidental duplication) in
favor of (1) physically splitting only the self-contained, low-routing-risk
git-mechanics content into a new skill `coding-agent-git-discipline`, and
(2) a structural-only template (`developing-skills/references/agent-governance-section-template.md`)
for the parts that stay in place. A real `export_public_bundle.py` bug
(CSV comma-quoting) was found and fixed by actually running the export,
not by the standard check suite -- confirmed working with a clean dry run.
`python3 scripts/run_all_checks.py` PASS at the release tip.

**Known gap, tracked not hidden**: `coding-agent-git-discipline` ships
`experimental` with zero real execution evidence (both its new eval cases
and the session-self-audit cases in `developing-skills` are structural-only
so far). Behavior-depth coverage overall is unchanged at 10/41 Skills.

**Next**: public-side push to the `CloudSkill` mirror is a separate,
explicit step -- see below for whether it happened this increment.

## Previous increment — 7.6.37 release cut: runtime-execution tooling, router/identity defect closure, Eval Inbox batch review, Skill-bundled hook mechanism (2026-08-22 to 2026-08-23)

Two-day continuous session, PRs #34–79 (90 commits). Full detail:
`CHANGELOG.md`'s 7.6.37 entry; validation evidence:
`docs/releases/7.6.37-pre-release-evidence.md`. Four workstreams: (1) real
runtime-execution analysis tooling (Bayesian confidence report, priority
ranker, learning-curve tracker, ablation-study runner) against a new
committed `evals/runtime/execution-ledger.json`; (2) a router "feels
trivial" trap and a cross-Skill fabricated-identity leak found via ablation
runs, closed with a deterministic scan+redact mechanism after two content-
only fixes were defeated; (3) ~20 Eval Inbox candidates converted into real
Skill content across game/architecture/governance Skills; (4) a new
optional Skill-bundled hook mechanism (`scripts/install_skill_hooks.py`)
with 7 real hooks, each tested against multiple real scenarios, verified
against each provider's own hook docs across Claude Code/Codex CLI/Gemini
CLI (not assumed).
`python3 scripts/run_all_checks.py` PASS at the release tip.

**Known gap, tracked not hidden**: behavior-depth real execution still
covers only 10/40 Skills; `using-cloudbox-skills` (the router itself) is
the statistically weakest Skill per the priority ranker's pessimistic LCB
(0.0%). The deterministic rubric grader covers 7/303 behavior cases and a
different pipeline than the one that produced this cycle's real ledger
entries — those were graded by direct model judgment, no independent
cross-check yet.

**Next**: `using-cloudbox-skills`, `document-governance`,
`game-quality-and-release-gates` are the LCB-ranked priorities. A commits-
since-last-tag advisory hook is planned immediately after this release so
the next version-bump gap doesn't reach 90 commits again.

## Previous increment — 7.6.32 private-equipment candidate (2026-08-19, shipped as part of 7.6.32–7.6.36)

Three de-identified equipment-family Skills and a generic WPH refactor are
under full lifecycle validation. The new family Skills are held in
`private-equipment`; WPH keeps its pre-existing core status. Evidence and
inference boundaries:
`docs/evolution/2026-08-19-public-equipment-evidence-distillation.md`.
Standing semantic-review transport is now managed model-selected sub-agents:
Codex Luna/Sol; Claude Code Sonnet 5/Opus 5, with 4.8 only as an availability
fallback. Policy and observed process RED:
`docs/evolution/2026-08-19-managed-subagent-skill-review-policy.md`.
Do not append raw panel output here; keep this section as a status pointer and
replace/archive it at release. Equipment behavior is Luna/Sol 19/19 GREEN.
Bounded final review ended Luna PASS / Sol FAIL on process-layer lifecycle and
meta-Skill evidence; those defects were corrected and DEVSK-BEH-022/023 now
pass case/contract execution. The repository owner accepted the frozen manual
evidence packet after the two-round model review limit was reached, then
superseded public release with a private-distribution hold before any push,
tag, or GitHub Release succeeded. Manual disposition:
`docs/evolution/2026-08-19-manual-review-disposition.md`. Claude-family review
is `NOT RUN` in this Codex host. After this private equipment candidate, process the
quality/architecture-fitness candidate together with the game-skill increment;
leave marketing skills until last.
An empty-directory public export confirmed that the three new Skill trees and
private plugin are excluded. Its full suite cannot stand in for publication CI:
the exporter expects destination-owned catalogs and a Git checkout. Before any
future public promotion, run the complete suite in the real public mirror.

## Current increment — 7.6.31 release cut: split private tier into `private-meta`/`private-game`/`private-operation`/`private-art` (2026-08-18)

Grew out of an architecture discussion: a queued marketing-strategy
candidate (spokesmodel/influencer promotional pattern, mined from a past
game project) had no existing skill owner, prompting the user to ask about
building a dedicated marketing-operations skill family. Rather than a new
repo (would duplicate the evolution/eval tooling — flagged and rejected),
landed on: same repo, new private sub-tiers, reused tooling unchanged.
`config/skill-distribution.json`: replaced the flat `evolution-pack` tier
with `private-meta` (self-referential skill/eval tooling), `private-game` (7
existing skills, reclassified 1:1), `private-operation`/`private-art` (new,
reserved, empty). Every script checking `tier == "evolution-pack"` now
checks `tier != "core"`, so future private sub-tiers need no script edits.
`config/skill-domain-catalog.json`'s per-domain `default_distribution`
updated to match; confirmed it already anticipated both new directions
(`planned_skills` already named `game-art-pipeline` and
`game-marketing-and-monetization` before this session). Live docs updated;
historical release/evolution documents deliberately left unchanged. No
skill's behavior, routing, or actual public/private visibility changed.
Version bumped `7.6.30` -> `7.6.31` (patch — internal reorganization only).
`scripts/run_all_checks.py`, `scripts/validate_plugins.py`, and
`scripts/manage_skill.py audit --check` all PASS at the release tip. Full
summary: `docs/releases/7.6.31-pre-release-evidence.md`.

**Next**:
- A dedicated router skill (analogous to `using-cloudbox-skills` but for the
  marketing/operations family) and a tier-scoped `SKILL_MANIFEST.json`
  generator are still needed before `private-operation` gets its first real
  skill — deferred until there is enough mined evidence (3-5 candidates) to
  define real trigger/non-trigger boundaries, not built on 1 thin candidate.
- `agent-development-process`, `document-governance`, and
  `teach-while-building` have not been reviewed since `7.5.0` — still
  blocking a clean minor bump, now for 3 consecutive releases. Tracked as
  Vikunja task 22 in the `cloudbox-skills` project since `7.6.29`; still
  open and should be prioritized before a fourth release hits the same
  wall.
- 11 mined interaction-Eval candidates (10 + 1 new marketing candidate from
  this increment) remain queued in `.local/eval-inbox/candidates/` awaiting
  an explicit batch-review instruction from the user, tracked in the
  `cloudbox-skills` Vikunja project.

> **Older increments archived 2026-08-25** (previously 2026-08-18): this
> file kept growing past its 20,000-byte living-document budget. Increments
> `7.6.27` through `7.6.30`, and everything archived 2026-08-18 before them
> (a large stale `v6.x`-era "current repository state" snapshot that had
> never been updated past CloudBox 6.4.0), live in
> `docs/history/AGENT_HANDOFF_ARCHIVE.md` — read it only when actually
> reconstructing history from that period, not by default.

## Read order

1. `AGENTS.md`
2. This file
3. `docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md`
4. `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`
5. `.agents/skills/developing-skills/SKILL.md`
6. `.agents/skills/runtime-evaluation-engineering/SKILL.md`
7. `.agents/skills/local-runtime-eval-debugging/SKILL.md`
8. `evals/runtime/contracts/behavior-output-contract.json`

## Standard continuation commands

Static/status only:

```bash
./cloudbox-skills-resume --status
python3 scripts/run_all_checks.py
```

Fresh Ollama evidence:

```bash
./cloudbox-skills-resume --provider ollama --force-eval
```

Release-grade Ollama R07 Behavior evidence (repeat>=3, ~25+ minutes, costs
3x the usual Behavior model calls; routing already defaults to repeat=3):

```bash
./cloudbox-skills-resume --behavior-repeat 3
```

Fresh Codex evidence:

```bash
codex login status
./cloudbox-skills-resume --provider codex --force-eval
```

Fresh Claude evidence:

```bash
claude auth status
./cloudbox-skills-resume --provider claude --force-eval
```

Resume after interruption without forcing a second completed run:

```bash
./cloudbox-skills-resume --provider ollama
# or
./cloudbox-skills-resume --provider codex
# or
./cloudbox-skills-resume --provider claude
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

## Eval Inbox import path

`.local/eval-inbox/` in this repository is initialized (via
`scripts/install.sh --config-only`, self-referential: `.cloudbox-skills/config.local.json`
points `cloudbox_skills_repository` and `eval_inbox` at this repository itself).
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
`.agents/skills/developing-eval/assets/export_eval_candidate.py` — see
`.agents/skills/developing-eval/references/interaction-eval-capture.md` and
`INSTALL.md` section 8b. This did not add a new Skill: it extends
`developing-skills`' existing `整理成正向/負向案例` capture flow with a
config-free fallback, per the "do not create a new Skill until an existing
owner is ruled out" rule.

Importing into `candidates/`/`manual-review/` is still only evidence
staging. Converting Inbox candidates into formal `evals/` cases remains a
separate, explicit `developing-skills` batch-review step (INSTALL.md section
9) that this import tool does not perform.
