# Changelog

## 7.7.2

Packaging patch for private local marketplaces. The public `cloudbox-skills`
plugin now uses a generated core-only `public-plugin/` source boundary, while
`cloudbox-skills-private` continues to use the private-only projection. This
prevents Codex or Claude plugin managers from copying private repository files
into the public plugin cache when the private repository is used as a local
marketplace. Existing Skill IDs and standalone installer behavior are
unchanged. The portable disconnected-session Eval exporter now lives under its
owning `developing-eval/scripts/` directory instead of `assets/`. Both Codex
and Claude plugin projections therefore install the executable with the Skill;
Claude instructions use `${CLAUDE_SKILL_DIR}`, while other hosts resolve the
installed directory containing `developing-eval/SKILL.md`.

Validation: `python3 scripts/run_all_checks.py` passes for the 7.7.2 package.
Codex and Claude public/private reinstalls pass; an isolated Codex test using
only the exporter installed in the plugin cache produces a valid bundle-format
2.0 ZIP. Claude execution was not run by operator request.

## 7.7.0

Covers PRs #99–105 plus one directly-pushed hook-logging commit
(`36b611f`, CI-verified, no PR): unified hook logging, Windows-native
PowerShell hooks for the 3 hooks this repository wires directly (not
through the bundled-hook manifest mechanism), a new private
`technical-case-content-generation` Skill, 9 manual-review
equipment-porting candidates merged one-owner-each across 6 public
Skills, and a routing-cue fix for `using-cloudbox-skills`.
`python3 scripts/run_all_checks.py` passes clean at the release tip.

### Minor: cross-platform hook coverage and behavior extensions to 6 public Skills

- **Unified hook logging** (`36b611f`): every hook that can print an
  error or advisory message (6 directly-wired + 4 bundled-only optional)
  now also appends it to a gitignored `.cloudskill-hooks-state/hooks.log`,
  so a noisy environment can be triaged from one file instead of session
  scrollback. Purely additive -- no hook's exit code or block/allow
  condition changed. Added 3 new behavior Eval cases (`CAG-BEH-017`,
  `DEVSK-BEH-027`, `CAGD-BEH-004`), ad hoc `claude -p` checked only.
- **Windows-native hooks** (#100, completed by #104): the 3 hooks this
  repository wires directly into its own provider configs
  (`validate-push-readiness`, `block-push-auth-loop`,
  `record-push-outcome`) gained native PowerShell equivalents, closing
  the gap the bundled-hook manifest mechanism's own Windows coverage
  didn't reach. Also raised the Skill context-budget gate to 20,000
  bytes after inventorying all 41 Skills and retiring the historical
  grandfathered ceilings.
- **9 equipment-porting candidates merged** (#103): real defects from a
  legacy-equipment-view-to-portable-engine porting session, distributed
  one primary owner each (deduped against every owner's existing cases,
  no overlap found) across `wph-equipment-simulator-development`,
  `framework-design`, `cross-platform-engine-architecture`,
  `equipment-control-architecture`, `equipment-domain-modeling`,
  `codebase-architecture-discovery`, `code-review`, and
  `safe-incremental-refactoring` -- new cases `WPH-SIM-DIS-001`,
  `FW-BEH-011`, `ENG-BEH-019`, `ENG-BEH-020`, `ECA-BEH-008`,
  `EDM-BEH-008`, `CAD-BEH-004`, `CR-BEH-010`, `REF-BEH-026`. 3 of the 9
  spot-verified via ad hoc `codex exec` (Luna/Sol), not exhaustive.

### New private Skill and a routing fix

- **`technical-case-content-generation`** (#101, #102): new
  `private-operation`-tier Skill turning one real technical case into
  audience-matched draft content (short-video script, social post,
  long-form article) with a hard evidence-honesty constraint -- every
  draft keeps at least one named limitation, never self-certifies, and
  always hands off to `game-marketing-and-monetization` for readiness/
  evidence sign-off. A follow-up PR merged 3 Luna-distilled candidates:
  per-case folder discipline for mixed-case packages, image/diagram
  provenance deferring to `game-art-pipeline`'s draft catalog, and one
  explicit publish-lifecycle state model (draft -> internal_review ->
  public-safe-candidate -> ready-to-publish -> published) applied
  consistently across every media type in `game-marketing-and-
  monetization`. Not part of the public plugin; case/contract-layer RED
  evidence only, live Skill/behavior execution `NOT RUN`.
- **Routing-cue fix** (#105, closes `cloudbox-skills` #15): root cause of
  `CAG-BEH-015`'s residual failure -- `using-cloudbox-skills`'s
  conversation-routing-map never mentioned checkpoint/roadmap tracking,
  while the adjacent `document-governance` cue superficially matched and
  pulled routing the wrong way. Added one cue row with an explicit
  disambiguation note. Re-verified 2/2 clean via ad hoc `codex exec`
  (Luna/Sol), not a durable/repeatable formal grade.

### Doc-only

- (#99) Recorded 4 real gaps hit this session for future reference: a
  per-provider hook launch-cwd precondition (Claude Code reads
  `.claude/settings.json` only from the literal launch directory; Codex
  CLI walks up from cwd to find `.git`), the structural-vs-live-execution
  split between the ~320-case behavior corpus and the 7-case runtime
  ledger, `--case-id` resolution scope, and calibration data confirming
  the existing eval-inbox dedup-score judgment call. No behavior change.

### Limits

- `technical-case-content-generation` and its merged candidates are
  `private-operation` tier only -- not part of the public plugin.
- The 9 equipment-porting cases and the routing-cue fix were verified via
  ad hoc `codex exec`/`claude -p` sampling, not the formal rubric-graded
  pipeline -- durable/repeatable grading still owed as a follow-up, per
  each case's `review_notes`.
- No hardware, device, platform-install, or production-deployment claims.

## 7.6.39

Covers PRs #94–98: a deep-read duplicate/overlap scan across the full
Skill portfolio, verified item-by-item before acting (not taken on faith),
plus the process fix for a real data-loss incident hit while producing
that scan. `python3 scripts/run_all_checks.py` passes clean at the
release tip.

### Fork report-loss incident, root-caused and closed

A worktree-isolated subagent's full findings file, written inside its own
worktree's `.local/`, was permanently lost when that worktree was torn
down before the dispatching session retrieved it -- only the short inline
summary survived. Redispatched twice (the first retry was separately
killed by an unrelated tool-use mistake in the dispatching session, not a
sandbox/security issue) until a properly-completed run (57 real tool
uses, full citations returned inline) produced trustworthy evidence.
Root-caused and closed: `coding-agent-project-governance` gained a rule
requiring any read-only investigation subagent to report full findings in
its own final message, never solely to a worktree-local file (new case
`CAG-BEH-016`).

### 6 of 7 findings verified and fixed; 1 verified and deliberately left alone

- **Equipment cardinality taxonomy drift** (PR #94): `cluster-tool-
  simulator-development` restated `wph-equipment-simulator-development`'s
  owning cardinality taxonomy under different names, missing its 4th
  category entirely -- fixed by cross-referencing instead of restating.
- **Status-model contradiction** (PR #95): `development-process-
  tailoring`'s own change-record template collapsed `document-
  governance`'s explicit five-dimension status model into one flat
  field -- the exact anti-pattern that model's own rule ("a single done
  field hides important risk") names. Fixed by citing instead of
  restating; also closed two smaller internal drifts inside
  `document-governance` itself (a combined status field, a document-role
  list that had drifted between `SKILL.md` and its own reference file).
- **Evidence-tier vocabulary** (PR #96): `game-audio-design`,
  `game-narrative-design`, and `game-marketing-and-monetization` each
  independently invented an incompatible evidence-tier vocabulary for
  grading how authoritative a cited external domain fact is. Consolidated
  into a new canonical scale, `developing-skills/references/domain-fact-
  evidence-tiers.md`, explicitly distinguished from the pre-existing
  observed/inferred confidence axis (a different question).
- **Skill-eval-dev cluster overlaps** (PR #97): a near-verbatim
  sanitization-detail list duplicated between `developing-skills` and
  `developing-eval` (despite the former's own text already saying the
  latter owns it); `local-runtime-eval-debugging`'s own two internal
  failure-classification lists didn't map onto each other; `developing-
  skills` and `runtime-evaluation-engineering` independently classify
  related-but-different failure/evidence-layer axes with no
  cross-reference either direction. All three cross-referenced/reconciled.
- **Self-contradicting verdict vocabulary** (PR #98): `game-quality-and-
  release-gates`' own Core principle used a different 5-value status
  vocabulary than its own Output Format item 4, in the same file --
  reconciled. `runtime-evaluation-engineering`'s AMBIGUOUS-for-NOT-RUN
  swap was confirmed as legitimate domain variation, not drift, and
  documented as such rather than forced to match.
- **Left alone, deliberately**: the equipment "GUI/animation is a
  projection" principle is worded 4 different ways across
  `tray-descum-simulator-development`, `equipment-control-architecture`,
  `wph-equipment-simulator-development`, and `cluster-tool-simulator-
  development` -- verified consistent in meaning (no real drift), and
  its natural owner (`equipment-control-architecture`) sits at a frozen,
  zero-growth budget ceiling. Judged the lowest-value item in the scan
  and not worth the resulting loss of each Skill's standalone
  readability; documented, not forced.

### Evidence discipline

Every fix in this release changed only citations/cross-references, not
required/forbidden behavior fields -- no new Eval case was authored for
PRs #96–98, disclosed explicitly in each affected Skill's `lifecycle.json`
notes. The 3 new cases from PR #94 (`CAG-BEH-016`) and PR #95
(`DOC-BEH-013`, `PROC-BEH-017`) are schema-validated only; none has real
model-behavior execution yet (tracked in the standing Vikunja `cloudbox-
skills #7` statistical-rigor backlog, not a new item).

## 7.6.38

Covers PRs #80–90: two new hooks, a session self-audit that produced real
process fixes, and a 3-way architecture split of
`coding-agent-project-governance` reached through real discussion (rejected
a "shared governance core" in favor of respecting that product/art/code
risk taxonomies are genuinely different, not accidental duplication).
`python3 scripts/run_all_checks.py` passes clean; a real dry-run of
`scripts/export_public_bundle.py` also verified clean (see below).

### 2 new hooks

- `coding-agent-project-governance/release-cut-reminder`: advisory,
  commits-since-last-tag threshold (default 6) -- direct response to this
  repository's own version tags falling 90 commits behind before 7.6.37.
- `coding-agent-project-governance/shared-checkout-guard`: advisory,
  warns at commit time when unstaged/untracked content exists that isn't
  part of the commit -- response to a real pattern hit 3+ times this
  session (editing in a checkout another concurrent agent was also
  working in, caught only reactively).

### Session self-audit (real mistakes, not hypothetical)

- `developing-skills`: candidate-capture-status discipline (answer from
  the capture tool's actual output, not chat memory) and parallel-dispatch
  case-ID range coordination (this session's own real `DOC-BEH-009`
  collision between two forks).
- `coding-agent-project-governance/references/git-commit-and-branch-hygiene.md`
  (new): a commit-message backtick/shell-quoting bug and a wrong-guessed-
  PR-branch-name incident, both hit and fixed this session.

### Architecture split: `coding-agent-git-discipline` (new skill)

Git-mechanics content physically extracted from
`coding-agent-project-governance` into a new skill: branch/worktree
control, push-auth recovery, commit/branch hygiene, plus 4 hooks
(`record-push-outcome`, `block-push-auth-loop`, `release-cut-reminder`,
`shared-checkout-guard`). `coding-agent-project-governance` freed real
byte budget (10476 -> 9542/10500). `vikunja-sync-reminder` ownership also
corrected to `project-management-sync`.

`developing-skills` gained `references/agent-governance-section-template.md`
-- explicitly a structural checklist (risk taxonomy / evidence definition
/ stop-condition / release-safety slots), not shared content: product,
art, and code governance are expected to fill those slots differently,
not converge on one shared prose core. `document-governance`'s product-
direction section and `game-art-pipeline`'s Draft Governance step were
deliberately NOT physically moved or forced to cite it -- zero routing
risk, zero eval-case migration.

Registry gaps found and fixed while landing the split (none introduced
today, some pre-existing): the new skill wasn't registered in
`SKILL_TAXONOMY.md`, `skill-domain-catalog.json`, `skill-distribution.json`,
or the Claude/Codex plugin manifests; separately, `game-design-systems` and
`game-narrative-design` were found never registered in
`skill-domain-catalog.json`'s `skill_classification` at all.

### Public-export bug found and fixed

Actually running `scripts/export_public_bundle.py` (not just
`run_all_checks.py`, which doesn't cover this path) surfaced a real crash:
two new routing-case rows had an unescaped comma in their `notes` field,
same bug class already fixed once for 5 rows in 7.6.36. Fixed and
re-verified with a full dry-run export to a scratch destination: exit 0,
new skill correctly included, private-tier skills correctly excluded.

### Docs

`docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md` refreshed from a 2026-08-17/
v7.6.24 snapshot (90+ commits stale) to current: skill counts, a full
rewrite of the Hooks section (from "not yet built" to "9 real hooks,
cross-3-provider" with a full table), roadmap milestones marked done,
unresolved-items table updated with evidence.

`docs/index.html` (new): a local, git-tracked, human-readable registry
view of all 41 skills by capability layer, the hooks table, and the
known-gaps list -- committed as a real file, same
`html-view-sync-reminder` convention already applied to `product/`/`art/`
domains, not an external link.

## 7.6.37

Covers PRs #34–79 (2026-08-22 to 2026-08-23): a two-day continuous session
spanning real runtime-execution analysis tooling, a router/identity defect
found and closed via ablation testing, a full behavior-execution coverage
pass, a large Eval Inbox batch review, and a new optional Skill-bundled hook
mechanism with 7 real hooks. `python3 scripts/run_all_checks.py` passes
clean (exit 0) at the release tip.

### Runtime-execution analysis tooling

- `scripts/eval_confidence_report_bayesian.py`: Beta-Binomial credible
  interval over real outcomes recorded in a new, committed, append-only
  `evals/runtime/execution-ledger.json` (pure-Python incomplete-beta
  implementation, no scipy; verified against a closed-form check).
- `scripts/eval_priority_ranker.py`: pessimistic lower-confidence-bound
  ranking across all 40 Skills (tested or not); validated itself in real use
  by correctly surfacing `using-cloudbox-skills` as top priority after the
  routing-trap fix below.
- `scripts/learning_curve_report.py`: Wright's-Law-style cost curve fit over
  `evals/runtime/learning-curve-log.json`, with its single-session/
  confounded-batch limitations disclosed rather than oversold.
- `scripts/run_ablation_study.py`: bypasses the router with a fixed
  primary/supporting-Skill decision, reusing the same real context-assembly
  and CLI-invocation path as the main harness to measure supporting-Skill
  cost/benefit directly.

### Router routing-trap fix and fabricated-identity defect

Closed a real router "feels trivial" trap where 3 independent Skills
repeated the same failure mode, and a general, cross-Skill fabricated-
identity defect (a model tendency to fill an unrequested attribution field
from ambient session identity, discovered via ablation runs) — two content-
only fixes were defeated by the model inventing a differently-named field to
carry the same fact, so this was closed with a deterministic scan+redact
mechanism (`scan_fabricated_identity`/`redact_fabricated_identity` in
`runtime_eval_common.py`) instead, plus a canonical shared reference
(`coding-agent-project-governance/references/no-fabricated-identity.md`).

### Full behavior-execution coverage pass

Completed the 52-case execution pass (surviving a real session usage-limit
reset mid-run) across routing and behavior cases for the touched Skills,
recording every real outcome to the new execution ledger — the actual
current coverage numbers (10/40 Skills with real behavior-depth evidence,
30/40 routing-only) are tracked going forward via the priority ranker rather
than restated here as a point-in-time claim.

### Eval Inbox batch review (PRs #66–73, #76–79)

Reviewed and converted roughly 20 Eval Inbox candidates into real Skill
content across `cloudbox-game-migration`, `native-ios-game-rewrite`,
`cross-platform-native-architecture`, `safe-incremental-refactoring`,
`gameplay-core-modernization`, `game-asset-resolution-audit`,
`game-art-pipeline` (draft governance, AI-art-generation-governance
reference, final-delivery product/variant/platform hierarchy, batch-
generation matrix planning), `document-governance` (product-direction role,
HTML overview-view convention), `agent-development-process` (session/agent
continuity), and `coding-agent-project-governance` (bounded GitHub push-
auth recovery, stale-workspace-authority pointer). One candidate found
redundant with already-merged content and archived without new Skill
changes rather than force-fit.

### Skill-bundled hook mechanism (new)

`scripts/install_skill_hooks.py`: a Skill may now optionally bundle one or
more deterministic hooks under `hooks/<name>/{script.sh,manifest.json}`;
this script discovers them and safely merges the wiring into a consumer
project's Claude Code / Codex CLI / Gemini CLI config (never overwrites the
whole file), always opt-in, never installs non-interactively without
`--yes`. Verified working across all 3 providers' real hook systems (event
names, matcher requirements, and blocking mechanisms confirmed via each
provider's own docs, not assumed).

7 real hooks shipped, each independently tested against multiple real
scenarios before merge:

- `game-art-pipeline/art-draft-catalog` — blocks a commit adding/modifying a
  generated concept image without its catalog file.
- `coding-agent-project-governance/identity-leak-backstop` — blocks a
  commit whose staged diff adds the checkout's own git identity into a
  document-field-shaped line (real backstop for the defect above).
- `coding-agent-project-governance/lifecycle-evidence-reminder` — advisory
  reminder when a Skill's content changed without its `lifecycle.json`.
- `coding-agent-project-governance/record-push-outcome` +
  `block-push-auth-loop` — generalized from this repository's own
  directly-installed pair into a reusable bundle; installed into
  lotto/cloudbox-engine/WphApp/cloudbox-skills.
- `coding-agent-project-governance/vikunja-sync-reminder` — mandatory
  (blocking, loop-safe via `stop_hook_active`) reminder using Claude Code's
  `Stop`, Codex CLI's `Stop`, and Gemini CLI's `AfterAgent` events.
- `document-governance/html-view-sync-reminder` — advisory reminder when a
  governed domain's Markdown changed without its adopted `index.html`
  overview.

Also fixed a real, reproduced bug this mechanism surfaced: `.gitignore`
covered the top-level `.worktrees/` pattern but not `.claude/worktrees/`
(where fork-agent isolated worktrees actually land), which broke
`freeze_skill_review_packet.py`'s `changed_paths()` whenever a fork agent's
worktree existed during a checks run.

### Project-management-sync formalization

Formalized the standing Vikunja/task-tracker sync habit (fixed field
format, append-only progress-in-task-not-chat for open long-running work)
into `project-management-sync/SKILL.md`'s Human-Readable Description Format
section, so any session working in this repository picks it up from the
Skill itself, not only from personal memory.

## 7.6.36

### Eval Inbox batch review: 31 candidates, 8 owner Skills

Full batch review of all remaining Eval Inbox candidates (27 equipment-dev
candidates imported from an external mining session, plus 4 long-pending
`indie-game-product-evolution` candidates), dispatched as 5 parallel
clusters:

- `indie-game-product-evolution`: consolidated 4 candidates into one new
  "revisit scope/risk/milestone decisions on a recurring cadence during
  production" workflow step (was previously a one-time-only decision).
- `wph-equipment-simulator-development`: report-only/policy-selection input
  authority safeguards, dispatch-vs-hardware-capacity attribution, baseline-
  drift disclosure, fixed-flow-to-declarative-timing migration discipline,
  plus (from a second cluster) the authoritative-simulation-state-vs-
  projection contract -- visualization/animation/GUI layers as a read-only
  projection, one-location-per-material custody, label-collision handling.
- `cross-platform-engine-architecture`, `framework-design`: reusable
  visualization DLL/component boundary and projection-test/host-adoption
  verification safeguards.
- `coding-agent-project-governance`, `architecture-review`: process-lock/
  force-close safety during iterative development; don't retire a validated
  baseline on visual parity alone, stage independently-scoped migrations.
- `equipment-domain-modeling`, `developing-eval`: capability-declaration-
  over-fixed-geometry modeling pattern (ports, aligners, LoadLocks, robot
  motion profiles); SME-correction distillation authority ranking.

All source candidates project-history/web-research-mined, `inferred`
confidence, case/contract-layer evidence only -- live Skill/behavior
execution NOT RUN. Every consumed candidate archived to
`.local/eval-inbox/processed/` with a `review_decision` record (gitignored,
not part of this diff).

### Public-export portability fixes

Found and fixed while running the public `CloudSkill` export for the first
time since v7.6.19 (2026-08-15) -- a class of drift bugs between the export
filter and its own consuming validators:

- Quoted 5 CSV `notes` fields containing unescaped commas that broke strict
  parsing.
- `validate_pack.py` now imports `PRIVATE_INFRASTRUCTURE_PATHS` from
  `export_public_bundle.py` instead of a hand-maintained duplicate that had
  drifted (missing several already-excluded paths).
- `validate_behavior_evals.py` and its `ENG-BEH-004` elicitation-contract
  check now tolerate a private-tier consumer/case missing from a filtered
  public checkout, instead of crashing.
- The staleness-checker regression test now runs against an isolated
  synthetic git fixture instead of this repository's own live tag history,
  making it portable to any checkout.
- `scripts/sync_private_codex_plugin.py` excluded from the public export
  (both source and destination are private-only, so it was a no-op there).

### Confidence-bound reporting + append-only lifecycle enforcement

At the user's request, following a discussion connecting Eval-mining
practice to discrete-math (lattice/CRDT monotonicity) and statistical
(Hoeffding bound) frameworks for "does a change provably not make things
worse":

- `scripts/eval_confidence_report.py` (new, public): advisory CLI computing
  the statistical confidence margin a Skill's current authored case count
  actually supports, via Hoeffding's inequality. Referenced from
  `developing-skills`' release-report step.
- `scripts/validate_lifecycle_monotonicity.py` (new, public, wired into
  `run_all_checks.py`): structural check enforcing that every
  `lifecycle.json` `notes` field is only ever appended to, never
  overwritten or shortened.

### Install scripts ask about local config

`install.sh`/`install.ps1` now ask once (interactive terminals only,
default yes) whether to create a local Eval-capture config, instead of
silently defaulting. `INSTALL.md` explicitly instructs a coding agent
running an install on the user's behalf to ask the same question in the
conversation itself -- covering both Plugin-mode and Standalone-mode
installs -- since the script's own stdin prompt cannot fire through an
agent-invoked subprocess.

## 7.6.35

### New Skill: game-art-pipeline (experimental, private-art)

- Added `game-art-pipeline`, the first `art-dev` Skill distinct from
  `game-asset-resolution-audit`: governs the art *production* pipeline
  (style-authority/art-bible gating, spec traceability, aesthetic-vs-technical
  conflict escalation, outsourcing partition/scope-of-work, vertical-slice
  production throughput gating, legibility/accessibility validation, and
  code-cross-reference asset inventory audits) rather than measured pixel
  readiness of assets that already exist.
- Synthesized from 7 sanitized project-history candidates, consolidated into
  5 independently-routable mechanisms; no third-party source involved.
- Lifecycle stage `experimental`: case/contract-layer RED evidence only (5
  routing rows, 4 behavior cases). Live behavior execution and managed
  sub-agent review are NOT RUN -- see the Skill's `lifecycle.json` notes.
- Distribution tier `private-art` (new `art-dev` current Skill; never
  public/core), matching the domain catalog's already-documented default.

### New Skill: game-narrative-design (experimental, private-art)

- Added `game-narrative-design`, the first `narrative-dev` Skill: premise,
  world lore, character dialogue, ambient NPC barks, and narrative-beat
  content, plus checking a story beat against the gameplay mechanic that
  ships with it.
- Honestly the lowest-confidence Skill added in this roadmap so far: 6 of 7
  source candidates were `inferred` confidence and one workflow step rests
  on a single tier-C secondhand source; see `references/evidence-lineage.md`.
- Lifecycle stage `experimental`: case/contract-layer RED evidence only.
  Live behavior execution and managed sub-agent review are NOT RUN.
- Distribution tier `private-art`, per the `narrative-dev` category's own
  documented default.

### New Skill: game-audio-design (experimental, private-art)

- Added `game-audio-design`: composer licensing/budget structure, SFX asset
  naming and loudness/format specification, adaptive-music technique choice,
  mix/priority hierarchy, and audio accessibility captions/runtime settings.
- Synthesized from 6 eval-inbox candidates; source lineage (one third-party
  MIT-licensed repository, one official platform accessibility standard, one
  GDC talk, one self-selecting industry survey) recorded in
  `references/evidence-sourcing.md`.
- Lifecycle stage `experimental`: case/contract-layer RED evidence only.
  Live behavior execution and managed sub-agent review are NOT RUN.
- Distribution tier `private-art`, per the `audio-dev` category's own
  documented default.

### Add game-design-systems Skill (experimental, private-game)

Adds `game-design-systems`, the first `design-dev` product-domain Skill:
mechanic/formula documentation, balance-knob verification-method
classification and domain-specific post-change audits (combat, economy,
progression, probabilistic reward), behavioral-observation playtest
protocol design, a cross-document fact/constant registry, staged
paper/digital/playtest core-loop validation gates, and scope-tiered design
documentation with explicit escalation triggers.

- Lifecycle stage `experimental` (not `active`, not `stable`): case/contract
  layer evidence only -- 1 positive + 5 negative routing cases and 4
  behavior cases (recognition/application/counterexample/discipline) added,
  satisfying the `draft_to_experimental` promotion gate. Live model
  behavior execution and managed sub-agent review remain `NOT RUN`.
- Distribution tier `private-game` (never public), per the `design-dev`
  category's own documented `default_distribution` and the standing
  private-by-default policy for game-related Skills.
- `SKILL.md` kept to 8.2 KB (well under the 10,500-byte context budget)
  with conditional detail split into three `references/*.md` files.
- Synthesized from 6 of 8 sanitized case/contract-layer candidates from
  project-history mining; the other 2 were deliberately excluded as
  near-verbatim duplicates of `indie-game-product-evolution`'s existing
  scope-lock/audience-fit territory.

## 7.6.34

### Remove unconfigured Git evolution-source synchronization

- Removed the scheduled Git source-sync workflow, source registry, schema,
  controller, and validator after repeated secret-preflight failures with no
  configured remote source.
- Removed obsolete live CI, packaging, and instruction references while
  preserving the separate manual Eval Exchange push/pull path.
- Archived the historical source-sync design guide for context; the commands
  described there are no longer supported.
- This is an internal patch update; no new public Skill behavior was added.

## 7.6.32

### Private equipment-family candidates and governed semantic review

- Added de-identified `tray-descum-simulator-development`,
  `cluster-tool-simulator-development`, and
  `wafer-bonder-debonder-development` Skills to the new
  `private-equipment` distribution tier. Public distribution is deferred until
  the quality-plus-game increment and a later explicit publication review.
- Refactored `wph-equipment-simulator-development` into the cross-equipment
  discrete-event capacity owner; family Skills retain topology, material,
  custody and process semantics.
- Added 19 equipment behavior cases and adjacent routing controls. Luna and Sol
  each passed all 19 packet-bound cases; hardware, field, approved recipe,
  calibration and numeric WPH evidence remain NOT RUN.
- Required unique Behavior Eval `suite` IDs, repaired the new-Skill scaffold,
  and added a real scaffold regression.
- Added immutable candidate/review packet manifests, managed reviewer policy
  (Codex Luna/Sol; Claude Sonnet 5/Opus 5 with matching 4.8 availability
  fallback), exact identity records, and a brownfield no-unapproved-rewrite
  gate.
- Bounded model review ended Luna PASS / Sol FAIL on process evidence. The
  process defects were corrected, DEVSK-BEH-022/023 passed Luna/Sol, and the
  repository owner approved the final manual evidence packet. A later owner
  instruction retained the Skills privately before any push, tag, or release.
- Added equipment closure, Luna High distillation and semantic architecture/
  pattern-fitness assessment documents. The latter remains a candidate, not a
  released Skill rule.
- Version 7.6.32 remains an internal candidate; no public tag or GitHub Release
  is authorized by this entry.

## 7.6.31

### Split the flat `evolution-pack` private tier into `private-meta`/`private-game`/`private-operation`/`private-art`

- `config/skill-distribution.json`: replaced the single `evolution-pack` tier
  with 4 sub-tiers, split by content kind rather than one flat bucket:
  `private-meta` (self-referential skill/eval tooling: `developing-eval`,
  `local-runtime-eval-debugging`, `runtime-evaluation-engineering`),
  `private-game` (the 7 existing game-product skills, reclassified 1:1),
  `private-operation` and `private-art` (new, reserved, currently empty —
  motivated by 3 queued interaction-Eval candidates from this session's game/
  engine mining passes that have no existing skill owner: a spokesmodel/
  influencer marketing pattern, design-doc-to-art-asset-manifest extraction,
  and style-specification/drift-check).
- Every script that previously checked `tier == "evolution-pack"` now checks
  `tier != "core"` instead (`scripts/export_public_bundle.py`,
  `scripts/validate_pack.py`, `scripts/validate_plugins.py`,
  `scripts/validate_skill_portability.py`,
  `scripts/sync_private_codex_plugin.py`) — any future private sub-tier is
  automatically picked up everywhere without another script edit.
- `config/skill-domain-catalog.json`: each product-domain category now names
  its own `default_distribution` (`art-dev` -> `private-art`, `marketing-dev`
  -> `private-operation`, the rest -> `private-game`) instead of one flat
  fallback. Confirmed this catalog already anticipated both new directions
  before this session: `marketing-dev`'s `planned_skills` already listed
  `game-marketing-and-monetization`, `art-dev`'s already listed
  `game-art-pipeline`.
- Updated all live documentation referencing the old flat tier name:
  `README.md`, `INSTALL.md`, `docs/SKILL_TAXONOMY.md`,
  `docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md`, `private-plugin/README.md`
  (also fixed a stale "21 skills" count to the correct 31). Historical
  release/evolution documents under `docs/releases/` and `docs/evolution/`
  were deliberately left unchanged — they are point-in-time records, not
  live state.
- No skill's actual behavior, routing, or public/private status changed:
  `wph-equipment-simulator-development` stays `core`; the reclassified
  skills' effective visibility is identical to before (still fully private,
  still excluded from the public bundle) — this is purely an internal
  organizational relabeling plus a script generalization.
- Version bump classified **patch**: purely internal reorganization, no new
  public capability, no behavior change for any skill.

Claude Code CLI 2.1.233, `sonnet` alias.

## 7.6.30

### Reclassify `wph-equipment-simulator-development` `evolution-pack` -> `core` (public), at the user's request

- Sanitization review, checked against the exact bar already used for
  `semiconductor-equipment-domain-knowledge`/`equipment-control-architecture`/
  `equipment-domain-modeling` (no company/project/customer/recipe/safety-limit
  identifiers), found and fixed two real gaps:
  - `references/implementation-map.md` named literal source-file paths from
    one specific C# codebase (`WphSimulator.Rewrite/*.cs` and friends) —
    rewritten to describe module responsibilities generically.
  - `references/domain-baseline.md` and `SKILL.md` step 6 stated concrete
    calibrated machine timing values (specific CT Z-motion seconds, specific
    slot/cassette/PM-time counts) as "confirmed machine input" — rewritten to
    keep the identical classification-table shape and confirmed/provisional
    discipline (the actual reusable content) while replacing every literal
    measured value with an explicit placeholder, matching the fact that the
    existing core-tier equipment Skills carry zero concrete numeric machine
    values.
  - A minor identifying detail in `references/evidence-cases.md` (a literal
    screenshot filename from the source project) was also genericized.
  - No company, employer, or product name was ever present in this skill;
    every fix was about removing artifacts specific to one real codebase or
    machine, not about names.
- `config/skill-distribution.json`: `wph-equipment-simulator-development`
  `evolution-pack` -> `core`, with a new decision-ledger entry.
- Added to `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`'s
  skills lists; removed from both `private-plugin` manifests and the
  `private-plugin/skills/` symlink and `private-plugin/codex-skills/`
  projection.
- `lifecycle.json`: notes rewritten with the full sanitization + reclassify
  summary; `last_reviewed_version` updated.
- Version bump classified **patch** again, for the same reason disclosed in
  `7.6.29`: the 3 skills not reviewed since `7.5.0`
  (`agent-development-process`, `document-governance`,
  `teach-while-building`) still block a clean minor bump today. A public-
  tier reclassification is, in spirit, exactly the "publicly-usable"
  trigger the confirmed versioning policy names as minor — this is
  disclosed as a real, deliberate deviation, not an oversight, and the
  blocking review remains tracked separately rather than rushed to force a
  minor bump.

Full evidence:
`docs/evolution/2026-08-18-wph-equipment-simulator-development-active-promotion-evidence.md`,
`config/skill-distribution.json`'s decision ledger.

Claude Code CLI 2.1.233, `sonnet` alias.

## 7.6.29

### Promote `wph-equipment-simulator-development` to `active`

- Gathered the live routing/behavior evidence `v7.6.28`'s import explicitly
  disclosed as `NOT RUN`: routing 6/6 (100%) at repeat=3; behavior 9/9
  completed across all 3 case shapes (recognition/application/
  counterexample) at repeat=3, manually verified against each case's own
  required/forbidden behaviors (no automated numeric rubric authored yet —
  a disclosed, deliberate gap); adjacent-regression canary suite 30/30
  semantically correct at repeat=3 (2 of the first 30 attempts hit a
  transient Runner/Context-layer structured-output-retry error, confirmed
  transient by an immediate successful retry).
- `lifecycle.json`: `stage` `experimental` -> `active`.
- The skill's `evolution-pack` (private) distribution-tier classification
  is unchanged and still awaiting explicit user confirmation — tracked
  separately, not blocking this stage promotion (stage and distribution
  tier are independent axes).
- Version bump classified **patch**, corrected from an initial minor-bump
  attempt: the versioning policy confirmed this session reads "a new
  active/publicly-usable skill" as the minor trigger, and this skill stays
  `evolution-pack` (private), never publicly distributed, so no public
  capability actually changed. The minor attempt also had a real, disclosed
  side effect worth recording: crossing a 7.5→7.7 two-minor-release gap
  triggered `scripts/validate_pack.py`'s staleness check
  ("last_reviewed_version is at least two feature releases behind") for
  three unrelated skills (`agent-development-process`,
  `document-governance`, `teach-while-building`) that have not been
  reviewed since `7.5.0` — a genuine, independent finding, not caused by
  this change, now tracked separately rather than papered over by staying
  on the minor version that exposed it.

Full evidence:
`docs/evolution/2026-08-18-wph-equipment-simulator-development-active-promotion-evidence.md`

Claude Code CLI 2.1.233, `sonnet` alias. No provider-backed mutation,
credential data, or private product identifiers are included.

## 7.6.28

### Import `wph-equipment-simulator-development` as an experimental, private-tier skill

- Onboarded an externally-authored skill package
  (`.local/eval-inbox/imports/wph-equipment-simulator-development-0.1.0-experimental.zip`)
  distilled from a semiconductor WPH equipment simulator project: event-sourced
  physical material flow as authority, GUI as projection, shared-resource
  reservation (CT/EFEM robots), PM chamber interlocks, and separated raw/
  summary/capacity report outputs.
- Structural onboarding only this pass: skill folder placed under
  `.agents/skills/wph-equipment-simulator-development/`; routing cases
  (`WPH-SIM-REC-001`, `WPH-SIM-CTR-001`) merged into
  `evals/skill-routing-cases.csv` and a new
  `evals/runtime/cases/wph-equipment-simulator-development-routing.json`;
  behavior cases (`WPH-SIM-REC-001`, `WPH-SIM-APP-001`, `WPH-SIM-CTR-001`)
  registered in `evals/behavior/cases/wph-equipment-simulator-development.json`;
  `lifecycle.json` set to `stage: experimental`,
  `introduced_version: 7.6.28`.
- Classified `evolution-pack` (private tier) in
  `config/skill-distribution.json`, not `core`: unlike the already-generalized
  `equipment-control-architecture`/`equipment-domain-modeling`/
  `semiconductor-equipment-domain-knowledge`, this skill's reference material
  still carries concrete calibrated machine timing values and a specific
  reference-implementation file layout tied to one real project. Wired into
  `private-plugin/skills/` (symlink), both private plugin manifests, and
  `private-plugin/codex-skills/` via `scripts/sync_private_codex_plugin.py`.
- Live routing and behavior model evaluation were **not run** this pass —
  only structural validity is confirmed. Do not promote past `experimental`
  without that evidence.

Claude Code CLI 2.1.233, `sonnet` alias. No provider-backed mutation,
credential data, or private product identifiers are included; the source
package was already sanitized of company/customer names before import.

## 7.6.27

### Fix a real router non-trigger ambiguity found while promoting `codebase-architecture-discovery`

- `using-cloudbox-skills/SKILL.md`: clarified that a settled design/scope
  decision is not the same as "the answer is already fully determined by
  supplied text" — the router's own non-trigger line was being conflated
  with settled-decision prompts in 2 of 3 repeated attempts, causing
  `primary_skill: null` instead of `safe-incremental-refactoring` on an
  already-approved cross-service move that still carries real
  behavior/contract/transaction-preservation risk. Added a clarifying
  paragraph naming this exact scenario as the counter-example.
- `evals/runtime/cases/cad-routing.json`: fixed `CAD-NEG-02`'s eval
  over-specification — the case already tolerated an extra supporting
  skill via `allow_additional_supporting_skills: true`, but the grader's
  `execution_order` check ignored that flag; added
  `allowed_execution_orders` (an existing mechanism, already used in
  `canary.json`).

Verified: the `codebase-architecture-discovery` routing suite at
`repeat=3` went from 85.7% (18/21, gate FAIL) to 100.0% (21/21, gate
PASS). The 10-case canary regression suite — run because the fix edits
shared router infrastructure loaded for every routing decision — was
unaffected, 100.0% both before and after.

Full evidence:
`docs/evolution/2026-08-18-router-non-trigger-clarification-and-cad-neg-02-tolerance.md`

Claude Code CLI 2.1.233, `sonnet` alias. No provider-backed mutation,
credential data, or private product identifiers are included.

## 7.6.26

### Remove dead evolution-sync CLI, promote `codebase-architecture-discovery` to `active`

- Deleted `scripts/sync_evolution_sources.py`: confirmed dead, fully
  superseded by `scripts/cloudbox_skills_evolution.py`'s `source sync`
  subcommand (both call the identical `sync_source()`/
  `load_source_registry()` with identical arguments, but only the latter is
  named in `docs/AUTOMATIC_EVOLUTION_SOURCES.md`, the CI workflow, and
  `validate_evolution_source_sync.py`). Removed its two remaining mentions
  in `scripts/validate_pack.py`'s and `scripts/export_public_bundle.py`'s
  private-infrastructure exclusion lists.
- Promoted `codebase-architecture-discovery` `experimental` -> `active`:
  added 2 new adjacent-regression routing controls (a code-review boundary
  and a familiar-codebase-no-discovery-gap boundary); ran `repeat=3`
  routing (this skill's own accuracy clean at 6/6 positive and 15/15
  correctly-not-selected negative, 0% forbidden-selection violations
  across 21 attempts) and `repeat=3` behavior GREEN (6/6 pass, mean
  96.9/100); closed the previously disclosed behavior-RED gap with a real,
  measured result (a genuine drop on the application case when the skill
  is removed, landing on this skill's own two core techniques). Full
  evidence:
  `docs/evolution/2026-08-17-codebase-architecture-discovery-active-promotion-evidence.md`.

Claude Code CLI 2.1.233, `sonnet` alias. No provider-backed mutation,
credential data, or private product identifiers are included in these
public Core changes.

## 7.6.25

### Close the Iteration Debt Ledger, consolidate 4 duplicated primitives, add `codebase-architecture-discovery`

Documentation-governance sweep and internal-logic audit, converted into a
consolidation refactor and one new Core Skill:

- Iteration Debt Ledger (F1-F6) closed: removed a redundant `distribution`
  field duplicated in `config/skill-domain-catalog.json`; deleted 5 obsolete
  pre-5.6.0 apply-overlay files; removed 2 orphaned evidence-bundle scripts;
  fixed the `skill-creator` PyYAML blocker and documented the `pip3` vs
  `python3 -m pip` interpreter-mismatch gotcha; fixed stale `5.5.1` version
  strings; closed `NAMING.md` checklist drift.
- Removed superseded `docs/superpowers/` planning artifacts (17 files) and
  the stale, pre-`using-cloudbox-skills`-naming `overlay/` snapshot
  (9 files); recorded the `legacy-game-product-archaeology` /
  `gameplay-core-modernization` routing-overlap decision (accepted as
  intentional, sequential-collaborator redundancy); fixed roadmap/taxonomy
  drift in `docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md` and
  `docs/SKILL_TAXONOMY.md`.
- Full internal-logic audit of all 64 `scripts/` files
  (`docs/plans/2026-08-17-validate-scripts-internal-audit.md`), confirming
  an organic hexagonal (ports & adapters) layering and finding 4 real
  duplicated cross-cutting primitives. Consolidated all 4 into new shared
  modules -- `scripts/hashing_support.py`, `scripts/git_support.py`,
  `scripts/cli_eval_adapter_support.py`,
  `scripts/json_schema_interpreter.py` -- each verified empirically
  (byte-identical output against every real schema/case file, plus targeted
  adversarial tests for the specific points of divergence) before merging.
  Caught and fixed one transitive-consumer bug in the process: a validator
  calling an old private function name directly instead of the new shared
  one. Added a general "read the architecture map before adding a new
  cross-cutting primitive" rule to `AGENTS.md`.
- New Core Skill `codebase-architecture-discovery` (`draft` ->
  `experimental`): a staged, checkpointed batch-discovery method for
  surveying an unfamiliar codebase and empirically verifying duplicated
  logic before refactoring it, paired with `safe-incremental-refactoring`
  the same way `legacy-game-product-archaeology` is paired with
  `gameplay-core-modernization`. Real routing RED/GREEN (5/5 GREEN vs 1/5
  RED -- a genuine premature-execution-skill misroute closed) and behavior
  GREEN (2/2 graded cases, 100/100) evidence recorded in
  `docs/evolution/2026-08-17-codebase-architecture-discovery-first-pass-evidence.md`.

Claude Code CLI 2.1.233, `sonnet` alias. No provider-backed mutation,
credential data, or private product identifiers are included in these
public Core changes.

## 7.6.24

### Harden project-management synchronization gates

Refines `project-management-sync` using the `skill-creator` review process:

- adds explicit audit, dry-run, apply, and unknown-outcome reconciliation modes;
- separates provider-adapter responsibilities from the provider-neutral
  reconciliation engine;
- adds field ownership and conflict-policy rules for bidirectional sync;
- requires non-mutating discovery and blocks writes when version/capability
  evidence or adapter contract tests are missing;
- adds an unknown-version/read-only routing and behavior case.

The Skill remains public Core and portable across macOS, Windows, Ubuntu/Linux,
and CI. No provider-backed mutation or credential data is included.

## 7.6.23

### Add cross-platform project-management synchronization

Adds the Core `project-management-sync` Skill for safe synchronization with
Vikunja, OpenProject, Redmine, and similar providers:

- idempotent reconciliation and stable source/remote identity mapping;
- provider version and capability discovery with read-only fallback;
- post-write readback, timeout reconciliation, and timestamp provenance;
- macOS Keychain, Windows Credential Manager/DPAPI, Ubuntu Secret Service, and
  CI secret-store boundaries;
- pre-serialization redaction for credentials, URLs, accounts, emails, and
  remote identifiers.

Claude Code 2.1.233 using the `sonnet` alias passed 3/3 routing and 3/3
selected-skill behavior cases; the deterministic behavior rubric averaged
100/100 after a first-pass privacy finding was corrected. Qwen was not used.

## 7.6.22

### Distill four private game-development Skills and add the two-layer taxonomy

Adds four active, private `evolution-pack` Skills distilled from the sanitized
legacy-game product evidence in CloudBox Atlas:

- `gameplay-core-modernization` (`game-dev`);
- `cloudbox-game-migration` (`cloudbox-dev` / `game-dev`);
- `native-ios-game-rewrite` (`ios-dev` / `game-dev`);
- `game-quality-and-release-gates` (`qa-dev` / `game-dev`).

The release includes lifecycle, routing, behavior, runtime-eval, Claude, and
Codex projections. Claude Code 2.1.233 using the `sonnet` alias was the
provider/model for the benchmark; Qwen was not used. The behavior suite passed
all 12 repeated application records for the four new Skills at 97.1/100
average, and adjacent art/engine/generic-quality regression reruns passed.
Routing primary-skill accuracy was 100%; supporting-skill composition remains
an explicit follow-up limitation rather than an unreported pass.

## 7.6.21

### Promote private game Skills to active

Adds the private `legacy-game-product-archaeology` and
`game-asset-resolution-audit` Skills, their game-dev/art-dev/qa-dev taxonomy,
behavior and runtime benchmark cases, and synchronized Claude/Codex private
plugin projections. Both Skills pass the release evidence gates for active
lifecycle status; they remain private and are not promoted to stable or public
Core.

The asset audit now requires representative asset rows to keep measured size
relationships, logical display assumptions, provenance, chosen action, and
static-versus-runtime validation limits together, preventing an upscale or
device-readiness claim from being left only in surrounding prose.

## 7.6.20

### Add Codex marketplace support for `cloudbox-skills-private`

The private Evolution Pack now has a Codex plugin manifest and a private-only
Codex marketplace entry, matching the already-supported Claude Code install.
Public bundle export filters the private entry from both Codex and Claude
marketplace manifests. The add-on remains three private Skills, installed
alongside the 18 core Skills.

### Fix `cloudbox-skills-private`: real install was broken, `..` path traversal is forbidden

Found running an actual `claude plugin install cloudbox-skills-private@cloudbox-marketplace`
for the first time (never tested end to end before this release): it failed
with "skills: Invalid input". `private-plugin/.claude-plugin/plugin.json`'s
`skills` field used `../.agents/skills/<name>/` paths, but the real Claude
Code plugin loader forbids `..` traversal ("Copied plugins cannot reference
files outside their directory"). `scripts/validate_plugins.py`'s own check
for this was never actually exercised against the real installer and had
been allowing it for the private plugin.

- Switched to the documented cross-plugin sharing pattern: symlinks under
  `private-plugin/skills/<name>` -> `../../.agents/skills/<name>` (dereferenced
  and copied into the cache at install time, not blocked like a direct `..`
  path), referenced in `plugin.json` with forward-only `./skills/<name>/`
  paths.
- `validate_plugins.py`: updated expected paths to match, and added a check
  that each entry is an actual symlink resolving to a skill with a real
  `SKILL.md`.
- Verified for real: `claude plugin marketplace update cloudbox-marketplace`
  + `claude plugin install cloudbox-skills-private@cloudbox-marketplace`
  succeeds, `claude plugin details` shows all 3 evolution-pack skills
  correctly resolved.

RED evidence: case/contract layer plus one real `claude plugin install` run
(the actual bug reproduction and fix verification). Full run_all_checks.py
suite passes at 7.6.20.

## 7.6.18

### `safe-incremental-refactoring`: Transitive-Consumer Discovery Before a Split

Distilled from the 2026-08-15 developing-eval split incident (9 patch
releases, 7.6.9-7.6.17, to get a real end-to-end export working because
validator scripts had hardcoded transitive dependencies a direct grep never
surfaced). First skill change in this repo produced end-to-end with
Anthropic's `skill-creator` eval-loop instead of manual editing: drafted,
tested against 4 realistic prompts (including a deliberate counterexample and
a hardened adversarial variant) via paired with-skill/baseline subagent
comparisons, found and fixed a real anchoring gap in a second iteration. Full
evidence in `docs/releases/7.6.18-skill-release-evidence.md`.

- `references/evidence-checklist.md`: new "Transitive-Consumer Discovery
  Before a Split" section -- grep the moved item's name, then one hop
  further from anything referencing it, repeat until clean; an in-repo test
  suite proves internal consistency, not that a downstream
  packaging/export/install step is complete; and (iteration-2 addition) the
  discovery methods are a minimum, not a checklist -- ask what's distinctive
  about the specific item being moved, since a consumer reached by what an
  item *is* (e.g. a pickled/persisted dotted path) cannot be found by
  grepping harder.
- `SKILL.md` Step 7: one-sentence cross-reference (not duplicated).

RED evidence: skill-creator subagent-comparison loop (see release evidence
doc), not a new `evals/behavior/cases/*.json` case. Full run_all_checks.py
suite passes at 7.6.18.

Temporary sync exception continues per 7.6.1: public CloudSkill mirror gets
the same content, until the planned CrewAI migration resumes the
private-only split.

## 7.6.17

### `validate_behavior_runtime_evals.py` no longer hard-requires `validate_behavior_contract.py`

Last file found running the real export end-to-end: this validator
unconditionally required `validate_behavior_contract.py` to exist, which
7.6.16 correctly excluded from the public checkout. Gated the requirement on
the same private-checkout signal (`scripts/run_runtime_evals.py` presence)
used elsewhere.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.17 in both checkouts; the real export into CloudSkill now passes
run_all_checks.py cleanly end to end.

## 7.6.16

### Exclude `validate_behavior_contract.py` and its exclusive dependency chain

Found running the real export end-to-end: `validate_behavior_contract.py`
stayed public in 7.6.15 on the assumption it was general-purpose, but it
hard-imports `run_local_eval_review`, `run_runtime_evals`, and
`runtime_eval_common` to check contract-fingerprint consistency across the
runtime-eval harness's consumer scripts -- all three already private. Audited
every consumer of `behavior_output_contract.py`, `runtime_eval_common.py`,
`canary.json`, and `routing-decision.schema.json` before excluding (not
assumed from filenames this time): every one is already-excluded runtime-eval
tooling, so all six are now excluded together. `review-assurance.schema.json`
and `behavior-rubrics.json` were checked the same way and confirmed to have a
genuinely public consumer (`validate_review_assurance.py`,
`validate_behavior_runtime_evals.py`) -- correctly left in the public bundle.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.16 in both checkouts.

## 7.6.15

### Revert the blanket `evals/runtime/` exclusion -- scripts, not schemas, are private

Found running the real export end-to-end: excluding the whole `evals/runtime/`
directory (added in 7.6.12) broke `validate_behavior_contract.py` and other
general-purpose validators that stay active in the public checkout --
`behavior-output-contract.json`, `review-assurance.schema.json`, and
`behavior-rubrics.json` are consumed by scripts that were never private
(`validate_behavior_contract.py`, `validate_review_assurance.py`,
`validate_behavior_runtime_evals.py`). The user's actual instruction was
scripts, not data: "私有的python腳本也不用匯出到公開." Reverted the
directory-level exclusion; the private-only *scripts* added in 7.6.12
(`run_runtime_evals.py`, `validate_multimodel_panel.py`, etc.) stay excluded,
and `run_all_checks.py`'s existing skip-if-missing-script logic handles their
absence -- their now-unused data files sitting in the public repo are inert
schemas/fixtures, not a privacy concern.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.15 in both checkouts.

## 7.6.14

### `validate_skill_portability.py`: treat an absent evolution-pack skill as expected

Found running the real export end-to-end: the public checkout failed with
"classifies Skill(s) that no longer exist" and "packaging
runtime-evaluation-engineering failed: Skill directory not found" --
`skill-portability.json` legitimately keeps classifying evolution-pack
skills for when they might ever be distributed, but the validator treated
their absence in a public checkout as an error rather than the expected
result of `scripts/export_public_bundle.py` never copying them. Fixed both:
the orphaned-classification check now excludes evolution-pack names, and the
packaging eligibility check now requires the skill's directory to actually
exist.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.14 in both checkouts.

## 7.6.13

### `validate_plugins.py`: don't hard-fail on a legitimately absent private plugin

Found running the real export end-to-end for the first time: the public
checkout's `run_all_checks.py` failed with "invalid JSON private-plugin/...:
No such file" -- `load_json` was called unconditionally even though
`private-plugin/` correctly does not exist in a public checkout, turning an
expected absence into a hard error instead of the intended silent skip.
Guarded the load behind an existence check.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.13 in both checkouts.

## 7.6.12

### Move evolution-pack documentation out of the public README

The public README still documented "Interaction-derived Eval capture" and
"Runtime model evaluations" -- both `evolution-pack`-tier per
`config/skill-distribution.json`'s own definition (skill self-mining and the
routing-accuracy runtime-eval harness). Moved both sections to the new
`private-plugin/README.md` (excluded from export like the rest of
`private-plugin/`), and updated the top-of-README banner to describe the
actual export mechanism (`scripts/export_public_bundle.py` reading
`skill-distribution.json`) instead of the stale "everything is mirrored"
description.

- `scripts/export_public_bundle.py` / `scripts/validate_pack.py`: extended
  the private-infrastructure exclusion to the full runtime-eval/multimodel-
  panel harness (`evals/runtime/`, `scripts/run_runtime_evals.py`,
  `validate_multimodel_panel.py`, the `claude_eval_adapter.py`/
  `codex_eval_adapter.py` pair, `cloudbox-skills-eval*` CLI entry points, and
  related validators) -- these were previously being exported unfiltered.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.12.

## 7.6.11

### `export_public_bundle.py`: prune stale files, not just copy new ones

Found running the first real export against CloudSkill: a copy-only export
left every file from earlier, less careful full-sync mirrors sitting in the
destination forever, including the two evolution-pack skill folders
(`local-runtime-eval-debugging/`, `runtime-evaluation-engineering/`) and the
old pre-split `developing-skills/references/interaction-eval-capture.md` /
`conversation-derived-optimization.md` paths -- exactly how the original
leak this whole rework exists to fix would have kept surviving every future
export. The script now prunes any file tracked in `--dest` that this run did
not write (except an explicit `DEST_ONLY_KEEP` allowlist for files the public
repo legitimately owns, e.g. `LICENSE`), and removes directories left empty
by pruning.

RED evidence: case/contract layer only. Full run_all_checks.py suite passes
at 7.6.11.

## 7.6.10

### `export_public_bundle.py`: rewrite plugin.json URLs to the public repo

Found immediately after 7.6.9 shipped, before any real export ran: the
export script copied `.claude-plugin/plugin.json` / `.codex-plugin/plugin.json`
verbatim, which would have silently overwritten the public CloudSkill repo's
already-fixed `homepage`/`repository`/`websiteURL` fields back to the private
repo's own URL on the next sync -- the exact bug fixed by hand earlier this
session, regressing itself. `PUBLIC_REPO_URL`/`PRIVATE_REPO_URL` constants
added; the export now rewrites those fields instead of copying verbatim.

RED evidence: case/contract layer only.

## 7.6.9

### Split `developing-eval` out of `developing-skills`; structural public/private plugin boundary

Marketplace submission readiness surfaced that the temporary full-sync
exception had already mirrored all three evolution-pack skills into the
public CloudSkill repo, contradicting `config/skill-distribution.json`'s own
"never publish" classification -- a memory/discipline-dependent gap, not a
structural one (see [[cloudbox-skills-private-only]] and
[[memory-vs-process-fix]] on the CloudBox side). `developing-skills` itself
turned out to bundle generic skill-authoring craft with CloudBox's own
private conversation-mining machinery. Fixed structurally, not by
remembering to filter:

- New skill `developing-eval` (evolution-pack): owns `整理成正向案例` /
  `整理成負向案例` / `從專案提煉優化案例`, the private Eval Inbox/exchange,
  and conversation/project-history mining. `developing-skills` (now core)
  keeps the generic RED/GREEN/lifecycle/release craft and hands off to
  `developing-eval` for capture.
- `config/skill-distribution.json` reclassified `developing-skills` to core,
  added `developing-eval` as evolution-pack, and is now enforced (not just a
  deferred label) by `scripts/export_public_bundle.py`.
- `.claude-plugin/plugin.json` / `.codex-plugin/plugin.json`: `skills` field
  changed from a wildcard directory to an explicit array of the 18 core
  skill paths, validated against `skill-distribution.json`.
- New `private-plugin/.claude-plugin/plugin.json` (`cloudbox-skills-private`):
  private-repo-only add-on plugin covering the 3 evolution-pack skills,
  registered as a second entry in `.claude-plugin/marketplace.json`. Install
  it locally with `/plugin install cloudbox-skills-private@cloudbox-marketplace`
  alongside the normal `cloudbox-skills` install to keep all 21 skills
  available day-to-day; it is never mirrored to the public repo.
- New `scripts/export_public_bundle.py`: the actual, scripted answer to
  "which files are safe to publish," reading `skill-distribution.json` and
  excluding evolution-pack skill folders, `private-plugin/`, and a small set
  of private mining/evolution infrastructure outside any skill folder
  (`scripts/capture_eval_candidate.py`, `sync_eval_exchange.py`, etc.;
  `.github/workflows/evolution-source-sync.yml`).
- `scripts/validate_plugins.py`, `scripts/validate_pack.py`,
  `scripts/run_all_checks.py`, and related validators made checkout-aware:
  they detect whether evolution-pack skill directories are physically
  present and enforce the private-repo contract when they are, or the
  public-repo contract (no trace of the private plugin) when they are not --
  the same command list and scripts now work unmodified in both checkouts.

RED evidence: case/contract layer only. Not run through the runtime/model
behavior-eval harness this pass. Full `run_all_checks.py` suite passes at
7.6.9.

Temporary sync exception continues per 7.6.1 for core content only from this
version forward -- the export filter, not manual judgment, is what enforces
that boundary now.

## 7.6.8

### Skill-quality pass: near-miss routing, description discipline, live-run model choice

Conversation-derived, same 2026-08-15 session, prompted by comparing this
repo's practice against Anthropic's `skill-creator` and the third-party
`obra/superpowers` skill-writing conventions.

- `evals/skill-routing-cases.csv`: `AID-NEG-01` (the sole negative case for
  `agent-development-process`) replaced a case with no shared vocabulary
  with the skill ("write commit/branch rules for a C# repo") with a genuine
  near-miss testing the adjacency `agent-development-process`'s own SKILL.md
  already names (`coding-agent-project-governance`) -- mirrors `CAG-NEG-01`'s
  already-good pattern in the other direction. `AR-NEG-01` (architecture-review)
  flagged as similarly weak but left open, not fixed this pass.
- `developing-skills`'s description: removed the workflow/output-summarizing
  tail ("...into sanitized routing and behavior evidence or a reviewable
  replacement package"), keeping trigger conditions only -- a description
  that summarizes workflow risks Claude following the description instead of
  reading the skill body, per both external conventions.
- `references/behavior-driven-skill-development.md`: when a live model run is
  chosen for GREEN evidence, prefer the configured multi-model panel over a
  local model as the default signal for behavior/discipline changes; local
  stays fine for cheap structural/routing sanity checks.

RED evidence: case/contract layer only. Not run through the runtime/model
behavior-eval harness this pass.

Temporary sync exception continues per 7.6.1: public CloudSkill mirror gets the
same content, until the planned CrewAI migration resumes the private-only split.

## 7.6.7

### `agent-development-process`: fixing a deterministic gap belongs in the harness, not in memory

Conversation-derived, same 2026-08-15 session as 7.6.6's tag/Release incident.
Generalized beyond that one repo's release process: when a discovered gap has
one fixed, repeatable answer, the fix belongs in the harness component that
owns it, not in a memory note or a scheduled/background monitor. The user
explicitly rejected both a standing memory reminder and a proposed cron-based
audit as the fix, requiring the process artifact itself to change instead, and
reserved memory for judgment-based state that actually changes over time.

- New behavior case `AID-BEH-005` (discipline).
- `references/tool-and-state-design.md`: new "Fixing a Gap: Harness Component
  vs. Memory" section.
- `SKILL.md` Step 8: one-sentence cross-reference to this rule (not
  duplicated).

RED evidence: case/contract layer only. Not run through the runtime/model
behavior-eval harness this pass.

Temporary sync exception continues per 7.6.1: public CloudSkill mirror gets the
same content, until the planned CrewAI migration resumes the private-only split.

## 7.6.6

### `developing-skills`: tag + Release are part of the release step, not a follow-up

On 2026-08-15, five consecutive releases (7.6.1-7.6.5) shipped correctly-worded
`release:`/`sync:` commits in both `cloudbox-skills` and the public `CloudSkill`
mirror, but the `git tag` and `gh release create` steps were silently skipped in
every one, in both repos, undetected for a whole session. Backfilled the 5
missing tag/Release pairs in both repos.

- `references/skill-lifecycle-standard.md`: "Release truth" section now states
  explicitly that a `release:` commit is not a release -- tag, push, `gh release
  create`, and a `gh release list` confirmation are the same step, required
  before reporting a release as done, re-verified for every version in a
  back-to-back run, not just the latest.

RED evidence: case/contract layer (this is a process-discipline change to the
release procedure itself, not a new behavior case). `run_all_checks.py` suite
passes at 7.6.6.

## 7.6.5

### `safe-incremental-refactoring`: escalating evidence shape as complexity grows

Same originating engine-revival session. Direct user discussion about why
the session's own artifacts moved from prose, to a flat table (the
shared-consumer table), to JSON (the eval case files) as complexity grew
-- generalized into an explicit escalation rule: default to the flattest
shape that stays correct, escalate to a schema'd/self-labeling format
only on a concrete complexity signal (multi-fact cells, need for
machine-checkable schema, need for reliable diffing over revisions), not
by default or "to be safe."

- New behavior case `REF-BEH-011` (discipline).
- `evidence-checklist.md`: new "Escalating Evidence Shape as Complexity
  Grows" section.
- `developing-skills`' `SKILL.md` Step 3: one-sentence cross-reference to
  this rule (not duplicated) -- the same principle already governs how a
  RED note escalates into a formal JSON case file.

RED evidence: case/contract layer. Not run through the runtime/model
behavior-eval harness this pass.

`validate_behavior_evals.py` (167 behavior case contracts, up from 166)
and `validate_skill_context_budget.py` (`developing-skills` `SKILL.md`
10,372/10,500 bytes) pass. Synced to the public mirror per the same
temporary exception noted in 7.6.1.

## 7.6.4

### `developing-skills`: report Skill-release changes as a table

Same originating engine-revival session. The user asked, across several
consecutive Skill releases in the same session, to have "what changed"
reported as a table (id / owner Skill / pressure closed / RED layer)
rather than prose, and asked for this to be written into the Skill itself
so it becomes the standing behavior going forward, not a one-off request.

- New behavior case `DEVSK-BEH-021` (discipline).
- `SKILL.md` Step 6 ("Report execution truthfully and control release"):
  added the table-reporting rule, scoped to what actually changed in the
  release being reported, not the whole Skill's contents.

RED evidence: case/contract layer. Not run through the runtime/model
behavior-eval harness this pass.

`validate_behavior_evals.py` and `validate_skill_context_budget.py` (this
Skill's `SKILL.md` stayed under the 10,500-byte budget, 10,111 bytes)
pass. Synced to the public mirror per the same temporary exception noted
in 7.6.1.

## 7.6.3

### `safe-incremental-refactoring`: convergent-implementation elimination and async completion verification

Same originating engine-revival session, a third follow-on correction.
During a live debugging investigation, two independently-built
implementations of the same capability (different libraries/backends)
both failed identically while each reported success at every API layer
it exposed. The investigation kept alternating between the two
implementations until a live control test (launching an unrelated,
already-trusted consumer of the same shared resource) and explicit
completion-signal tracing (distinguishing "the synchronous call returned"
from "the async operation actually completed") together narrowed the
search meaningfully.

- New behavior case `REF-BEH-010` (discipline).
- `evidence-checklist.md`: two new subsections under the existing
  "Environment vs. Defect Attribution" heading -- "Convergent Failure
  Across Independent Implementations" (treat identical symptoms across
  independently-built implementations as evidence pointing at a shared
  cause, corroborated by a live control test) and "Verifying Async
  Completion, Not the Synchronous Call That Started It" (a log line
  confirming a call returned is not evidence an async operation it
  started actually completed -- trace the real completion signal).

RED evidence: case/contract layer, same disclosure basis as 7.6.1/7.6.2.
Not run through the runtime/model behavior-eval harness this pass.

`validate_behavior_evals.py` (165 behavior case contracts, up from 164)
passes. Synced to the public mirror per the same temporary exception
noted in 7.6.1.

## 7.6.2

### `safe-incremental-refactoring`: dual implementation behind a single compile-time switch

Same originating engine-revival session, a follow-on correction. After a
shared implementation was replaced and the replacement's correctness in
the actual target environment turned out not yet confirmed (it compiled,
its own API reported success, but an outside observer -- the user -- could
not confirm it actually worked there), the recovery decision was: restore
the old implementation rather than leave it deleted, rename it to reflect
what it actually is now that a second implementation exists beside it, and
put both behind exactly one compile-time flag in a single dedicated
location.

- New behavior case `REF-BEH-009` (discipline).
- `compatibility-facade.md`: new "Dual Implementation Behind a Single
  Compile-Time Switch" section -- distinguished explicitly from the
  existing Compatibility Façade pattern (that one is for responsibilities
  migrating underneath a stable calling surface; this one is for two
  complete, independent implementations of an already-existing interface,
  appropriate specifically while the new implementation's correctness is
  still an open question).

RED evidence type: case/contract layer, same disclosure basis as 7.6.1 --
not run through the runtime/model behavior-eval harness this pass.

`validate_behavior_evals.py` (164 behavior case contracts, up from 163)
passes. Synced to the public mirror per the same temporary exception noted
in 7.6.1.

## 7.6.1

### `safe-incremental-refactoring`: shared-consumer before/after state table

Conversation-derived correction from a live engine-revival session's own
real-time verification record: a slice that replaced a component shared by
three platform consumers reported success in prose for two of them while a
third had silently regressed -- the asymmetric outcome was invisible in the
verification writeup and was only caught later when the user recalled the
pre-change state from memory, costing several extra rounds of live
re-testing to reconstruct. Generalized beyond the originating platform
case: the same gap applies to any slice that replaces or consolidates a
component used by more than one consumer (multiple call sites, multiple
subclasses of a shared base, multiple client integrations), not only
multi-platform work.

- New behavior case `REF-BEH-008` (discipline): requires a per-consumer
  before/after state table, built at write time, whenever a slice touches
  a component with more than one consumer; a single-consumer slice is
  explicitly exempted (prose remains sufficient there).
- `evidence-checklist.md`: new "Shared-Consumer Before/After State" section
  with the minimum table shape and rationale.
- `SKILL.md`: one-line pointers in Step 7 (Verify) and Step 8 (Handoff).
- `REFACTOR_SLICE.template.md`: an empty table skeleton under
  `## Verification`, to fill in only when more than one consumer is
  affected.

RED evidence type: case/contract layer -- the prior Step 7/8 text and
`evidence-checklist.md`, read as written, did not require enumerating
every affected consumer, so prose-only reporting of exactly the shape that
occurred in the originating session would have satisfied the prior
checklist. Not run through the runtime/model behavior-eval harness in this
pass; disclosed as case/contract-layer evidence, not promoted to a
Skill/agent-behavior-layer GREEN claim.

`validate_behavior_evals.py` (163 behavior case contracts, up from 161),
`validate_skill_lifecycle.py`, and `validate_pack.py` (20 skills, 96
routing cases) all pass.

Synced to the public mirror alongside this release as a temporary,
explicit exception to the private-only development model, pending a
planned migration; see the public repository's README for the current
sync status.

## 7.6.0

### `coding-agent-project-governance`: independent security verification before adopting agent infrastructure

Set up the local Eval Inbox import folder (`.local/eval-inbox/`) and processed
2 candidates imported from a disconnected session via `import_eval_candidates.py`.
Both routed to `manual-review/` (no sensitive-terms file configured on this
machine, so the importer conservatively withheld auto-promotion) and were
reviewed by hand before any formal change:

- One candidate (apply the user's own existing methodology documents instead
  of generic advice) was checked against current skill content and found
  already covered by `framework-design`'s demonstrated-consumer principle and
  `document-governance`'s locate-authoritative-source discipline --
  `NO_CHANGE_JUSTIFIED`, retained as regression evidence in `rejected/`, not
  promoted.
- The other candidate (independently verify a tool's security track record
  across multiple authoritative sources before recommending adoption as
  infrastructure, rather than trusting a single third-party comparison
  article) was confirmed as a genuine, previously-uncovered gap in
  `coding-agent-project-governance` and promoted: 1 new behavior case
  (`CAG-BEH-009`) plus a short `SKILL.md` addition under "Route by risk".

`validate_pack.py` (20 skills, 96 routing cases), `validate_behavior_evals.py`
(161 behavior case contracts), `validate_skill_lifecycle.py`,
`validate_plugins.py`, and the full `scripts/run_all_checks.py` suite all
pass.

## 7.5.0

### `developing-skills`: CI status is release evidence, not an inference

Discovered while auditing this repo's own GitHub Actions history: CI
(`validate-cloudskill.yml`) had been failing on every push from v7.2.0
through v7.3.0 -- the same `teach-while-building` portability gap fixed in
v7.4.0 -- and it went unnoticed because release work only ever checked local
validator output, never the actual CI run.

`developing-skills`' release workflow (step 6) now requires checking the
real CI run for a pushed commit before calling the release done; a
CI-configured check that was never observed to run is `NOT RUN`, not
`PASS`, no matter how clean the local run was. 1 new behavior case
(`DEVSK-BEH-020`).

`validate_pack.py` (20 skills, 96 routing cases), `validate_behavior_evals.py`
(160 behavior case contracts), `validate_skill_lifecycle.py`,
`validate_plugins.py`, and the full `scripts/run_all_checks.py` suite all
pass.

## 7.4.0

### `developing-skills`: mandatory SKILL.md size gate

`scripts/validate_skill_context_budget.py` previously checked only
`developing-skills`' own SKILL.md. It now enforces a per-skill byte budget
(default 10,500 bytes) across all 20 skills, wired into
`scripts/run_all_checks.py` as before. 4 skills that were already over
budget (`equipment-control-architecture`, `development-process-tailoring`,
`equipment-domain-modeling`, `local-runtime-eval-debugging`) get a frozen
ceiling at their exact current byte count -- zero further growth room, not a
standing exemption.

`developing-skills`' release workflow (step 6) now names this check
explicitly as blocking: a budget failure must be fixed by consolidating
rules or moving detail into `references/`, not deferred, and the budget or
a grandfathered ceiling must never be raised just to make a failing skill
pass. 1 new behavior case (`DEVSK-BEH-019`).

`validate_pack.py` (20 skills, 96 routing cases), `validate_behavior_evals.py`
(159 behavior case contracts), `validate_skill_lifecycle.py`, and
`validate_plugins.py` all pass.

## 7.3.0

Distilled from this session's own naming-migration, release-sync, and
architecture-reversal friction into reusable behavior evidence, plus two
`teach-while-building` optimizations proposed after that skill's v7.2.0 landed.

### `teach-while-building`: explicit calibration override + batched checks

- New optional `LEARNING_LEVEL.md` file (sibling to `LEARNING_LOG.md`): a
  user-written, per-domain level statement that overrides both the
  no-history-default and any `LEARNING_LOG.md`-inferred signal. Only written
  when the user states their level directly, never inferred.
- Checks now batch at the next natural pause (slice/checkpoint finishing, a
  build/test succeeding) instead of firing immediately after every flagged
  concept, with an explicit exception for a concept that blocks the very next
  step. 3 new behavior cases (`TWB-BEH-007` batching, `TWB-BEH-008` blocking
  exception, `TWB-BEH-009` override-file applied).

### New cross-skill behavior evidence, distilled from this session

- `developing-skills` (`DEVSK-BEH-018`): surface a new skill/plugin
  identifier's collision with an unrelated existing product immediately,
  before it propagates across files, instead of discovering it after adoption.
- `safe-incremental-refactoring` (`REF-BEH-007`): after a slice changes
  `.gitignore` patterns, diff the newly-staged fileset against the previous
  ignore state before committing, to catch a previously-local-only file that
  got silently un-ignored.
- `document-governance` (`DOC-BEH-006`, `DOC-BEH-007`): correct an absolute
  document status claim ("archived", "no further updates") in the same change
  that introduces a scope exception, instead of leaving it stale; and verify a
  downstream/mirror remote is genuinely terminal before isolating a status-only
  commit there, to avoid a forced non-fast-forward merge at the next real sync.
- `agent-development-process` (`AID-BEH-004`): verify a load-bearing
  platform/vendor capability against authoritative documentation or a direct
  test *before* finalizing an architecture decision that depends on it, not
  after work has already been built on the assumption.

`validate_pack.py` (20 skills, 96 routing cases), `validate_behavior_evals.py`
(158 behavior case contracts), `validate_skill_lifecycle.py`, and
`validate_plugins.py` all pass.

## 7.2.0

### `teach-while-building`: zone-of-proximal-development calibration

The trigger bar was previously implicitly calibrated against an expert user's
sense of "non-obvious" -- real but silent gap for a junior or unfamiliar-with-
the-stack audience. Adds an explicit calibration section grounded in Vygotsky's
zone-of-proximal-development framing (target the gap between "already knows
alone" and "needs a full lecture," using live evidence, not a fixed assumption):

- No calibration history for a domain yet -> default toward checking *more*.
- Confirmed `LEARNING_LOG.md` history in a domain -> the bar can rise there.
- User expresses surprise about something that wasn't flagged -> treat as a
  live miss, lower the bar for that domain going forward.
- User states their own level directly -> overrides inferred calibration.

2 new behavior cases (`TWB-BEH-005` no-history-defaults-generous,
`TWB-BEH-006` surprise-is-a-live-miss-signal). `validate_pack.py` (20 skills,
96 routing cases), `validate_behavior_evals.py` (150 behavior contracts),
`validate_skill_lifecycle.py`, and `validate_plugins.py` all pass.

## 7.1.0

### New skill: `teach-while-building`

Distilled from reviewing `mattpocock/skills`' `grilling`/`teach` interaction
patterns and adapted into a lightweight, self-judged, in-task check, rather than
a separate teaching workspace or course:

- Fires only when a genuinely new, non-obvious, likely-to-matter-again concept
  comes up mid-task -- not on every explanation.
- Checks understanding with 1-2 short questions (own recommended answer stated
  alongside each), not a restated explanation.
- Logs only confirmed-durable concepts to a project-local `LEARNING_LOG.md`, in
  the user's own framing, not a transcript of the explanation.
- Explicitly out of scope: building a curriculum, lesson sequence, or resource
  list -- that's a materially heavier, different request.

Stage: `experimental` (2 routing cases, 4 behavior cases covering recognition,
discipline, counterexample, and the full positive application path).
`validate_pack.py` (20 skills, 96 routing cases), `validate_behavior_evals.py`
(148 behavior contracts), `validate_skill_lifecycle.py`, and
`validate_plugins.py` all pass.

## 7.0.0

### Plugin identity renamed: cloudbox -> cloudbox-skills

Breaking change to the published interface -- major version bump.

- `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`: plugin `name`
  `cloudbox` -> `cloudbox-skills`, `displayName`/`interface.displayName`
  `CloudBox` -> `CloudBox Skills`. `author.name`/`developerName` stay `CloudBox`
  (the brand, not the product).
- Router skill: `.agents/skills/using-cloudskill/` ->
  `using-cloudbox-skills/` (directory, `SKILL.md` name field, lifecycle.json,
  references, both behavior-eval case files re-keyed to match).
- Config template `config/cloudskill-config.template.json` ->
  `cloudbox-skills-config.template.json`; `cloudskill_repository` config key ->
  `cloudbox_skills_repository`. Local config directory convention `.cloudskill/`
  -> `.cloudbox-skills/` (existing local configs are not auto-migrated).
- Docs `CLOUDSKILL_AGENT_HANDOFF.md`, `docs/CLOUDSKILL_CHANGE_HISTORY.md`,
  `docs/CLOUDSKILL_DESIGN_AND_FLOW.md` -> `CLOUDBOX_SKILLS_*`.
- CLI executables `cloudskill-eval(-claude/-codex)`, `cloudskill-resume` ->
  `cloudbox-skills-eval(-claude/-codex)`, `cloudbox-skills-resume`.
  `scripts/cloudskill_evolution.py` -> `cloudbox_skills_evolution.py`.
- Install docs (`INSTALL.md`, `docs/CLOUDBOX_PLUGIN.md`): install command and
  `/cloudbox:<skill>` -> `/cloudbox-skills:<skill>` invocation examples updated.
- `homepage`/`repository`/`websiteURL` fields updated to
  `github.com/cloudhsu/cloudbox-skills` (this repository's new home; the prior
  public `github.com/cloudhsu/CloudSkill` gets one final synced release and is
  not updated further after that).
- Rationale and full migration checklist: `NAMING.md` (new) -- a domain-word
  decision procedure (`agent`/`engine`/`skills`/`tools`) for the CloudBox
  product family, written to prevent the plugin-vs.-an-unrelated-CloudBox-game-
  engine naming collision that prompted this release from recurring as the
  family grows (planned future `cloudbox-agent-*` roles).

### Distilled two reusable safeguards from a real engine-revival session

- `cross-platform-engine-architecture`: a comment claiming code is dead/unused
  is not evidence by itself -- require tracing the reachable call graph (or
  running the code) before excluding a file as dead.
  `references/historical-evidence-rule.md`, case `ENG-BEH-005`.
- `coding-agent-project-governance`: verify the actual host toolchain/
  environment (compilers, SDKs, target architecture) before configuring a
  cross-compile build, rather than assuming from the task description.
  `SKILL.md` "Inspect before prescribing", case `CAG-BEH-008`. Also adds a
  "long-running/multi-session progress" checkpoint-convention row to
  `references/artifact-matrix.md`.

Both source cases are sanitized (no project/product names, paths, or dates).
`validate_pack.py` (94 routing cases, unchanged), `validate_behavior_evals.py`
(142 -> 144 behavior contracts), `validate_skill_lifecycle.py`, and
`validate_plugins.py` all pass. Live model grading (`grade_behavior_evals.py`)
not run as part of this release.

## 6.5.0

### Promoted five eval-inbox candidates to Skill content

- `coding-agent-project-governance`: added `CAG-BEH-006` (delegation scope for
  irreversible release steps -- weigh established in-session delegation trust
  against reversibility and audience before proceeding autonomously through
  merge/tag/publish) and `CAG-BEH-007` (three-tier ALLOW/ASK/DENY tool-permission
  classification replacing a binary allow/deny split, with pattern-matching
  bypass-vector disclosure) to `references/risk-routing.md`.
- `safe-incremental-refactoring`: added `REF-BEH-006` (classify a failure as
  environment-agnostic or mechanism-specific before treating a
  differently-configured CI run as environment-vs-defect evidence) to
  `references/evidence-checklist.md`.
- `runtime-evaluation-engineering`: added `RTE-BEH-010` (sub-agent evaluation
  containment -- isolate the target system and scope tool access regardless of
  prompt framing, then verify change-tracking state afterward) to
  `references/case-and-grader-design.md`.
- `developing-skills`: added `DEVSK-CONV-006` (treat an eval-loop comparison
  that reveals a candidate's own overgeneralized or self-contradicted wording
  as RED evidence at the wording layer, with a two-round revise-and-retest cap
  and a harder-scenario requirement before concluding a no-delta candidate has
  low value) to `references/behavior-driven-skill-development.md`.
- All five candidates were empirically tested via baseline-vs-candidate
  sub-agent comparisons before promotion; one (`CAG-BEH-006`) showed a
  genuine, reproducible behavioral delta, the other four converged with
  independently-reasoned baseline behavior and are promoted primarily for
  their more complete and explicit disclosure/classification content. Nine
  sibling candidates from the same mining passes were tested and rejected
  (no behavioral delta after a required harder-scenario retest, or superseded
  by these same five); see `.local/eval-inbox/rejected/` for the retained,
  non-deleted evidence trail.
- No lifecycle stage, schema, or bundle-format change.

## 6.4.1

### Windows export bundle corruption fix

- Fixed `export_eval_candidate.py`'s `package_outbox()` building `payload_hashes`
  manifest keys with `str(path.relative_to(outbox))`, which yields backslash
  separators on Windows while `zipfile.write()` independently normalizes the
  archive member name to forward slashes on every OS -- the manifest's declared
  key never matched the actual archive member, and `import_eval_candidates.py`
  rejected the whole archive as an invalid zip, silently discarding every
  candidate inside it. Only affected Windows invocations without `--no-zip`.
- Found via the 6.4.0 version-compatibility self-test in
  `validate_interaction_capture.py`, which crashed with a `KeyError` before
  the fix on a Windows machine. Fixed by using `Path.as_posix()` instead of
  `str()`, matching zipfile's own normalization. See #19, #20.

## 6.4.0

### Evidence-driven lifecycle templates

- Added one authoritative registry and deterministic selector/composer for
  `lightweight-change`, `bounded-feature`, and `skill-evolution`; seven future
  template IDs remain explicitly deferred and fail closed as unsupported.
- Preserved every template's stage partial order through deterministic
  topological composition, with owner/gate conflicts and cycles stopping plan
  creation instead of silently weakening lifecycle control.
- Bound selected evidence to work, source, task definitions, facts, risk, and
  registry identity, with automatic invalidation and ordered lineage when that
  context changes.
- Made JSON evidence identity type-preserving so booleans and numbers cannot
  alias across admission or replan; regression mutations cover facts and risk
  in both boolean directions.
- Added layer-typed RED/GREEN governance to prevent implementation evidence
  from being promoted into unexecuted Skill, provider, or release claims.
- Retained manual Eval ZIP import, unsupported/legacy recovery, privacy policy,
  lifecycle-first planning, evidence-second verification, and token reduction
  only after those higher priorities are preserved.
- Made export/import contract identity explicit across bundle 2.0, exporter
  2.0, candidate schema 1.0, CloudBox version, and host/runtime; mismatched
  archives and duplicate payload names fail closed before any candidate
  publication, while correctly declared 6.3 archives remain consumable by the
  6.4 importer.
- Revalidated every candidate and the owning private-term policy before Eval
  Exchange network/Git activity, removed local config-path provenance from
  exported payloads, converted malformed sanitization metadata into controlled
  rejection evidence, migrated path-bearing 6.3 provenance into manual review,
  and made incomplete publication rollback a durable reconciliation state.

## 6.3.0

### Manual Eval ZIP exchange

- Fixed exported bundle names to `<project>-<host>-<agent>-<YYYYMMDDTHHMMSSZ>-<bundle-id8>.zip`, with project and agent aliases retained only in ignored project-local configuration.
- Required ZIP filenames to match their versioned manifest before any candidate is imported.
- Added one-run mixed batch coverage for supported, duplicate, unsupported, and malformed archives, including deterministic disposition and zero model/provider dependencies.
- Withdrew the unreleased controlled-tool broker and adapter experiment; its concurrency, filesystem-confinement, staging, and NAS lessons remain future research rather than shipped authority.
- Preserved manual import, Git source synchronization, unsupported archive retention, and the separate explicit review required before formal Skill or Eval changes.

## 6.2.0

### Adaptive lifecycle and review assurance

- Added composable lifecycle profiles with versioned plans, risk-triggered replanning, durable checkpoints, interruption reconciliation, action identity, budgets, and deployment-versus-operational closure.
- Added risk-selected Review Assurance levels from deterministic-only checks through cross-family 2x2 review, with truthful achieved levels, hash-bound exceptions, blocking vetoes, and token-aware scheduling.
- Hardened lifecycle persistence with revision checks, fencing-token lease turnover, authority-scope enforcement, atomic replacement, and directory durability synchronization.
- Added executable contracts, behavior cases, documentation, and repository-wide deterministic validation for the new lifecycle and review mechanisms.
- Recorded controlled external CLI/MCP adapters as a post-6.2 evolution discussion; no new external execution authority is introduced by this release.
- Recorded the approved post-6.2 split into a public development Core and a locally installable private Evolution Pack; no repository split or private upload is part of 6.2.

## 6.1.0

### Git-first evolution intake and architecture elicitation

- Added a token-free, private Git source synchronization path with bounded source scopes, secret-reference configuration, durable Exchange state, idempotent partial-write recovery, and zero-model no-change runs.
- Added versioned Eval export bundles with integrity manifests, normalized project/host/agent filenames, explicit unsupported-bundle handling, and preserved manual import/export operation.
- Added a shared architecture decision elicitation protocol that asks only material boundary questions, records assumptions, and allows reversible progress when answers are unavailable.
- Documented the 6.1 operational boundary: background automation may stage private evidence, but Skill modification, formal Eval promotion, PR, merge, and release remain separately authorized and evidence-gated.
- Added deterministic validators and independent release review for secrecy, archive integrity, recovery, workflow persistence, and the new architecture behavior contracts.

## 6.0.0

### Evidence-gated Skill evolution

- Added executable task-continuity contracts that preserve authority, action, provider, cost, latency, model-identity, and lineage evidence across multi-session evolution work.
- Added a repository-owned, bounded cross-family review panel with durable attempt reservation, deterministic schema enforcement, explicit degraded and unresolved states, and independently reviewable sanitized evidence.
- Added lifecycle and compatibility controls for major-version review currency, exact-candidate lineage, no-change decisions, rollback evidence, and release gating.
- Hardened Runtime Eval provider isolation and canonical-model provenance without allowing aliases or malformed consequential actions to self-certify.
- Preserved the full RED-to-GREEN correction history and final four-cell Task 8 PASS evidence for the reviewed 6.0 source candidate.

## 5.8.0

### Multi-model Skill distillation and Eval adjudication

- Added an adaptive, role-separated multi-model protocol: independent sanitized extraction, RED and owner selection, one minimal patch, blinded cross-family judging, dimension-level disagreement capture, safety vetoes, and explicit adjudication.
- Added cost controls: routine candidates use deterministic checks and an inexpensive reviewer; a diverse 2x2 panel is reserved for safety, authority, routing-owner, disputed-answer, or release-significant decisions and stops when findings saturate.
- Made the coordinator contract host-neutral: Codex may coordinate Claude Code CLI workers and Claude Code may coordinate read-only `codex exec` workers, with unique worker outputs, canonical returned-model evidence, truthful degraded-panel states, and explicit no-subprocess boundaries for sandboxed surfaces.
- Added permanent behavior contracts for multi-model Runtime Eval design and conversation-derived Skill optimization. Multi-model agreement alone is not GREEN evidence.

### R07 Claude repeat evidence and grader lineage

- Completed the first release-grade Claude Code CLI R07 run: routing 15/15 and Behavior 3/3 PASS. The archived deterministic scores were 82.7 / 85.0 / 92.0 (average 86.6).
- Fixed a third demonstrated `verification-scenarios` false negative: all three outputs contained numbered bold Markdown fault-injection scenarios followed by `Expected:`, but the grader awarded 0/8. Re-grading the preserved raw JSONL without a new model call yields 90.7 / 93.0 / 100.0 (average 94.6).
- Behavior grade reports now persist input and rubric SHA-256 values, separating model-output changes from offline grader changes.
- Kept semantic safety outside keyword scoring. Cross-model judges identified failover fencing, late-completion, physical-authority, and over-assumption concerns that require semantic adjudication even when deterministic coverage passes.

## 5.7.0

### Claude Code CLI Runtime Eval provider

- Added `claude` as a third Runtime Eval provider (Claude Code CLI headless, alongside Ollama and Codex CLI), isolated with `--safe-mode --tools "" --permission-mode acceptEdits --no-session-persistence --strict-mcp-config` and explicit workspace-isolation prompt framing.
- First live run found and fixed two real bugs: a Qwen3/Ollama-only `/no_think` directive leaking into the shared prompt builder and breaking Claude's stdin slash-command parser, and occasional structured-output retry exhaustion from an unframed prompt letting the model attempt a disabled tool.
- Added `cloudskill-eval-claude`, a quota-conscious one-repeat smoke wrapper.

### Provider registry

- Added `evals/runtime/contracts/providers.json` + `scripts/providers_contract.py` as the single authoritative source for the Runtime Eval provider set, replacing hand-copied `--provider` choices tuples across consumers.
- Added `scripts/validate_providers_contract.py` with positive-propagation (consumers must derive `--provider` choices from `PROVIDER_IDS`, not a literal tuple) and negative-drift-injection (forbidden hand-typed provider tuples) mutation tests, mirroring the existing Behavior output contract's anti-drift pattern.
- Added a decoupled `--behavior-repeat N` option to `run_local_eval_review.py`/`cloudskill-resume`, independent of routing `--repeat` (previously hard-coded to 1 regardless of the top-level flag).

### First live Codex evidence

- First-ever live Codex Runtime Eval run in this repository's history; found and fixed a retired CLI flag (`--ask-for-approval`, removed from codex-cli 0.147.0) that had never been caught because the adapter had never actually been executed against a live process before.

### R07 Behavior grader precision (two rounds)

- Fixed false negatives in `assumptions-unknowns` and `restart-reconstruction` (regex too rigid for numbered/bulleted real-world phrasing) and, in a second round found via the first live Codex run, `state-authority` and `verification-scenarios` (regex too narrow for an "Authority matrix" table and numbered imperative fault-injection scenarios) plus a too-tight `reconnect-reconciliation` proximity window.
- Re-grading already-captured provider output with no new model calls raised scores consistently across all three providers (Codex 78->100, Ollama repeat=3 average 79.8->83.8, Claude 78->84), confirming grader precision rather than a content quality gap.
- Added executable regression fixtures (RED against the pre-fix rubric, GREEN after) so these precision regressions cannot silently reappear.

### Eval Inbox: disconnected-session export, project-history mining, and Git-based exchange

- Added `.agents/skills/developing-skills/assets/export_eval_candidate.py` (config-free, self-contained) and `scripts/import_eval_candidates.py` for capturing interaction Eval candidates from a session with no reachable CloudSkill repository, transferred as a zip and merged with re-sanitization and de-duplication.
- Added project-history-derived Eval capture (trigger phrase `從專案提煉優化案例`): mining a project's commit history, architecture/design documents, and code for reusable engineering pressure, with auto-bounded scope, `inferred`/`unknown`-only confidence discipline, and third-party attribution caution.
- Added `scripts/sync_eval_exchange.py`: Git-based transport of captured candidates between machines through a separate, user-owned private exchange repository, for the case where `.local/eval-inbox/` being gitignored on every machine (by design) strands candidates captured on a second machine even when that machine can also reach the CloudSkill repository.

### Platform and surface support

- Added `docs/PLATFORM_SUPPORT_MATRIX.md`, `config/skill-portability.json`, and `scripts/package_surface_skills.py`/`scripts/validate_skill_portability.py`: classifies every Skill `portable`/`hybrid`/`cli-only` for sandboxed surfaces (claude.ai web, Claude Desktop, Claude API Skills, which upload one Skill at a time as a zip and do not share filesystem access with the CloudSkill repository), and packages eligible Skills into the zip structure those surfaces require.
- Confirmed existing Windows/macOS Codex CLI and Claude Code CLI install coverage (`install.ps1`/`install.sh`, plugin marketplace and standalone modes) was already real; documented Gemini CLI's own claimed `.agents/skills/` alias support as unverified.

### Skill development discipline

- Formalized two of this release's own retrospective lessons into `developing-skills/SKILL.md` as an explicit rule and "common mistakes" entries: a new instance of an authoritative-contract pattern is not complete until it reaches the same anti-drift mutation-test rigor as its closest existing sibling, and a fix's own side effects (for example, a new dynamic import writing bytecode cache) must be checked for whether they can reintroduce the class of problem they were meant to prevent.

## 5.6.0

### Local Ollama execution

- Added a no-API-key `ollama` provider to the executable Runtime Eval runner.
- Defaulted local Eval execution to `qwen3:4b`, context 4096, temperature 0, seed 42, and disabled thinking for stable routing JSON.
- Added installed-model checks, local-server diagnostics, structured-output parsing, and provider-specific timing/token metadata.
- Kept the OpenAI Responses API provider available for optional cloud or GitHub Actions runs.

### Executable model evaluations

- Added an OpenAI Responses API runtime runner with strict JSON-schema routing output, request IDs, retries, latency, token usage, and privacy-preserving `store=false` requests.
- Added an eight-case Canary Suite covering code review, equipment state composition, version-scoped documents, application architecture, ACK-versus-completion semantics, no-skill translation, English equipment architecture, and historical-interaction skill optimization.
- Added a deterministic grader for primary skill, required supporting skills, forbidden selected skills, execution order, valid skill IDs, no-skill accuracy, output validity, and router self-inclusion.
- Added machine-readable summary metrics and a strict Canary release gate.

### Validation and operations

- Added static Runtime Eval validation to `scripts/run_all_checks.py`; ordinary pushes do not consume model API credits.
- Added a manually triggered GitHub Actions workflow using the `OPENAI_API_KEY` repository secret and an explicit model input.
- Added artifact upload for raw JSONL results and graded summaries.
- Added local-result exclusions so API outputs and machine-specific evidence are not committed by default.
- Preserved all 17 skill IDs, 87 routing cases, 87 behavior contracts, and existing plugin installation behavior.

## 5.5.4

### Routing contract and trigger hygiene

- Removed prompt language as a `using-cloudskill` trigger; Chinese, English, and mixed-language tasks now route only by engineering decision boundary.
- Added a structured routing contract for `primary_skill`, `supporting_skills`, `rejected_skills`, `execution_order`, reason, and confidence.
- Defined `using-cloudskill` as a router rather than a downstream supporting skill, except when the task is specifically about routing policy.
- Separated deliverable ownership from execution order so a supporting quality skill may establish metric validity before document transformation.
- Moved detailed conversation-derived scenarios from the router body into `references/conversation-routing-map.md` to limit router growth.

### Regression coverage

- Added Chinese translation and rewriting no-skill boundaries.
- Added English equipment-architecture and mixed-language code-review positive cases.
- Added explicit owner-versus-execution-order and router-self-inclusion discipline cases.
- Expanded both routing cases and behavior case contracts from 83 to 87.
- Preserved all existing skill IDs, canonical paths, plugin installation behavior, and private Eval Inbox behavior.

## 5.5.3

### Conversation-derived skill optimization

- Expanded `using-cloudskill` routing for recurring architecture, equipment-control,
  domain-modeling, code-review, document-governance, application, and agent-development cases.
- Added clearer routing boundaries for communication defects, equipment state authority,
  distributed IPC recovery, version-scoped field statistics, and multi-audience documents.
- Expanded `developing-skills` with a controlled workflow for mining sanitized historical
  interactions into repeatable routing and behavior evaluation cases.
- Added explicit handling for incomplete conversation access, sensitive project context,
  GitHub read-only permissions, overlay delivery, and truthful verification reporting.
- Added regression cases derived from recurring engineering discussions without retaining
  proprietary customer, project, equipment, path, or operating-value details.

### Fixes

- Restored the required `CloudBox skills` marker in the `using-cloudskill`
  OpenAI metadata.
- Fixed plugin validation failure caused by incompatible metadata wording.
- Updated manifest metadata and file counts for the optimized skill package.

### Compatibility

- Preserved all existing skill IDs and canonical skill paths.
- No breaking changes to plugin installation, local configuration, or Eval Inbox behavior.

## 5.5.2

### CloudBox dual-plugin packaging

- Added a `cloudbox` plugin manifest for Codex/ChatGPT and a separate Claude Code plugin manifest, both pointing to the existing canonical `.agents/skills/` source instead of duplicating skills.
- Added local/Git marketplace catalogs for both plugin systems and documented installation, update, namespacing, and standalone-versus-plugin collision rules.
- Added configuration-only installer mode so plugin users can configure the private Eval Inbox without copying duplicate standalone skills or guidance.
- Added the supplied CloudBox ICO plus generated PNG icon and logo assets; the OpenAI manifest exposes the logo, composer icon, and `#00A2EA` brand color.

### Plugin coexistence and branding

- Rebranded user-facing routing metadata to CloudBox while preserving the `CloudSkill` repository name, configuration paths, and stable skill IDs.
- Added CloudBox-only and hybrid coexistence rules for Superpowers or other workflow plugins, including one-router ownership and truthful reporting of host-level enable/disable state.
- Added routing and behavior regression cases for explicit CloudBox-only use, hybrid responsibility separation, and host plugin-management requests.

### Validation

- Added deterministic validation for both plugin manifests, both marketplace catalogs, canonical skill paths, matching versions, and PNG branding assets.
- Added plugin validation to the standard check runner and package-required-file audit.

## 5.5.1

### Local repository installation and configuration

- Added optional local CloudSkill repository and Eval Inbox paths to the PowerShell and Bash installers.
- Added user-level and project-local configuration files so Codex or Claude Code can reuse the configured repository without repeating paths.
- Added a private `.local/eval-inbox` lifecycle with candidate, manual-review, processed, and rejected states; local interaction data remains excluded from Git.

### Interaction-derived Eval capture

- Extended `developing-skills` so the phrases `整理成正向案例` and `整理成負向案例` capture the current relevant interaction as a sanitized Eval candidate.
- Made sanitization mandatory by default, prohibited raw transcript storage, and prevented daily capture from modifying formal Evals, skills, commits, or remote branches.
- Added candidate and mining-report templates plus a deterministic capture helper that discovers project or user configuration and routes uncertain records to manual review.

### Validation and baseline repair

- Added install/config/candidate-capture smoke validation to the standard check runner.
- Restored trigger-only `Use when...` descriptions for legacy skills that had regressed during the 5.5 repository rebuild, then regenerated the manifest.
- Added routing and behavior contracts for positive capture, negative capture, sanitization failure, and non-Eval conversation summaries.

## 5.5.0

### Semiconductor equipment domain knowledge

- Added `semiconductor-equipment-domain-knowledge` for EFEM/Main Frame/process-chamber responsibilities, material and environment flow, component capability interpretation, vacuum/gauge/pump semantics, PVD principles, and physical-to-software translation.
- Added explicit separation of general process principles, historical training evidence, product-specific hardware behavior, recipe-specific values, and current controlled specifications.
- Added public-sanitization and safety limits so confidential training material informs generalized skill behavior without publishing proprietary topology, schedules, identifiers, or operating procedures.

### Equipment triggers and physical semantics

- Narrowed equipment-skill routing so terminology/process questions use domain knowledge, topology/Sequence/resource/recovery questions use equipment control architecture, and state/command/unit/quality questions use equipment domain modeling.
- Expanded equipment-control guidance for EFEM/loadlock/transfer/process-chamber material flow, atmosphere/vacuum boundaries, pump/vent completion, sensor validity, process readiness, and power/plasma completion evidence.
- Expanded equipment-domain modeling with component-state patterns for actuators, measurements, regulators, motion, pumps, thermal utilities, and process-energy sources.

### Evaluation and evidence

- Added routing and behavior contracts for vacuum gauges, MFCs, pump/vent, wafer transfer, plasma/PVD readiness, training-value limitations, and multi-skill composition.
- Added a sanitized evidence record for semiconductor-equipment training material and updated deterministic validation requirements.

## 5.4.0

### Equipment-control architecture

- Added `equipment-control-architecture` for physical/runtime/network/responsibility topology, Sequence and Equipment Service boundaries, command/event lifecycle, shared-resource arbitration, interlocks, Local/Simulate/Remote parity, distributed IPC recovery, and equipment-platform modernization.
- Added explicit rules for timeout versus physical completion, late-result reconciliation, resource-owner loss, restart recovery, protocol/version negotiation, configuration governance, and bounded real-equipment pilots.
- Added templates for equipment architecture and event contracts.

### Equipment domain modeling

- Added `equipment-domain-modeling` for component identity, state/command lifecycle, Actual/Desired/Commanded/Readback/SP/PV semantics, pending-write reconciliation, typed command strategies, capability interfaces, snapshots, config schemas, and metadata-driven UI.
- Added selection rules for inheritance (`is-a`), composition (`has-a`), capability interfaces (`can-do`), and generics (`same pattern, different type`).
- Added command and domain-model templates plus validation and compatibility guidance.

### Platform evolution and evidence

- Added a sanitized evidence record derived from private equipment-architecture and training material; confidential names, schedules, detailed topology, customer data, and hardware identifiers are intentionally excluded.
- Added a two-roadmap model that separates product capability growth from deployment/migration topology.
- Added routing and behavior contracts for distributed equipment, config-driven chambers, automatic UI, common-library boundaries, simulation-to-hardware validation, and multi-skill composition.

## 5.3.0

### Skill-system maturity

- Added `using-cloudskill` to select and order the smallest sufficient set of process, domain, change, quality, and handoff skills.
- Added `developing-skills` to make skill creation and modification evidence-driven and behavior-test-driven.
- Changed all skill descriptions to trigger-only `Use when...` contracts so routing metadata does not become a shortcut around the skill body.

### Evaluation and validation

- Added behavior-evaluation contracts with recognition, application, and counterexample cases for every skill.
- Added separate validators for descriptions and behavior cases; case validation is explicitly not treated as a completed model execution.
- Added installation smoke tests for canonical Codex and Claude skill copies.
- Added a single check runner and GitHub Actions workflow.
- Made pack version validation derive from `VERSION` and cross-check README, changelog, and manifest instead of hard-coding one release.

### Development discipline

- Added RED baseline, GREEN verification, adjacent-skill regression, common-mistake, and truthful evidence requirements for skill changes.
- Added skill contract and behavior-evaluation templates.
- Documented conceptual influences from public skill-authoring work without importing another repository's full methodology.

## 5.2.0

### Touch/device utility architecture

- Added repository/document evidence from a historical Qt/C++ touch IC utility without copying proprietary source, command tables, binaries, customer details, or logs.
- Expanded cross-platform native architecture guidance for authoritative device inventory, HID/USB protocol and transport separation, hot plug, privileged OS behavior, monitor/input mapping, firmware update, installer/startup, product variants, and field support.
- Added a dedicated touch/native-device utility architecture reference.

### Product evolution and project governance

- Expanded development-process tailoring to reconstruct actual evolution from specifications, Git history, tags, release notes, customer feedback, test utilities, installer changes, and field defects.
- Added controls for product/release horizons, technical spikes, urgent scope insertion, capacity/dependencies, release baselines, variant divergence, rollback, and field feedback.
- Added a product-evolution reference and reusable evolution-map template.

### Specification evolution

- Expanded document governance for request/analysis/decision/current-spec/release-baseline separation, version lineage, supersession, and distinct implementation/verification/release status.
- Added checks for filename, cover title, revision history, approval, content, and release-link consistency.
- Added routing evaluations for native device utilities, evolution reconstruction, specification drift, product variants, and release quality gates.

## 5.1.0

### Qt component modernization

- Added repository evidence from the historical `cbComponent` and `cbWorkshop` Qt component suites.
- Expanded cross-platform native architecture guidance for legacy Qt Designer plug-ins, qmake/CMake coexistence, Qt 5/Qt 6 migration, ABI and `.ui` compatibility, duplicate-source authority, and optional Qt/OpenCV/Charts/3D feature boundaries.
- Added a Qt component modernization reference and execution-plan template.
- Added routing evaluations that distinguish native Qt modernization from generic framework design and safe incremental refactoring.
- Upgraded the architect profile from user-stated Qt-tool capability to repository-verified evidence.

## 5.0.0

### Documentation architecture

- Removed full history snapshot directories; Git commits and annotated tags are authoritative.
- Reduced root-level Markdown entry points and introduced a document ownership map.
- Consolidated overlapping profile/capability documents.
- Separated source evidence by source without repeating it in the profile.
- Replaced standalone duplicated standards with one concise governance overview linked to executable skills.
- Consolidated migration guidance into the changelog and release index.
- Added an exact-paragraph duplication audit.

### Codex and Claude Code

- Added `INSTALL.md` for user and project installation.
- Added PowerShell and Bash installers.
- Added `CLAUDE.md` as a minimal adapter importing `AGENTS.md`.
- Kept `.agents/skills/` as the canonical skill source and synchronized it to Claude Code locations.
- Updated coding-agent governance for dual-tool repositories.

### Skill behavior

- Document governance now checks for an existing authoritative source before creating a new document.
- Coding-agent workflow recognizes both `AGENTS.md` and `CLAUDE.md`.
- Added a Claude project adapter template.

## 4.0.0

- Added source-grounded Bento and CloudBox evidence.
- Added safe incremental refactoring and cross-platform engine architecture.
- Added evidence confidence levels and source-aware architecture guidance.

## 3.0.0

- Added Client/Server, cross-platform native, coding-agent governance, and architect profile.

## 2.0.0

- Added documentation governance, ISO/IEC 25010, process tailoring, and AI-agent development.

## 1.0.0

- Initial architecture-review, framework-design, and code-review skills.
