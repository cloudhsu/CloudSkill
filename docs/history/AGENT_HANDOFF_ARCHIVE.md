# CloudSkill evolution handoff archive

Historical detail archived from `CLOUDBOX_SKILLS_AGENT_HANDOFF.md` on
2026-08-18, when that file had grown to 1898 lines (~110KB) since its
first entry on 2026-08-09 and was never pruned. `AGENTS.md` requires
reading the live handoff before Skill/Eval/grader/runtime-tooling work;
this archive is NOT part of that required reading — read it only when
actually reconstructing history from the period it covers.

Two kinds of content live here:

1. Increment-by-increment narrative older than what the live handoff
   keeps (2026-08-15 through the 7.6.26 release).
2. A large `CloudBox 6.0`-`6.4`-era block ("Current repository
   state", "Latest verified evidence before this increment", "Open
   evolution items") that was already stale by the time of archival —
   it described repository state as of `6.4.0`/2026-08-12 while the
   repository had moved to `7.6.31`. Kept for historical record, not
   because it reflects anything current.
3. Two sections built entirely around a since-superseded PR-gated
   merge workflow ("PR #1", branch-then-merge-to-main) that this
   session's own observed practice (direct commits to `main` for
   every 7.6.x/7.7.x release) no longer follows. Archived rather than
   silently kept live as if still authoritative — if this repository
   wants a current, accurate release-criteria section again, write a
   fresh one from actual current practice rather than reviving this.

---

## Earlier increment — Fixed router non-trigger ambiguity + `CAD-NEG-02` eval over-specification (2026-08-18)

Closes the open follow-up item 1 from the 7.6.26 release (router-composition
noise found while testing `codebase-architecture-discovery`'s adjacent
boundaries). Full evidence:
`docs/evolution/2026-08-18-router-non-trigger-clarification-and-cad-neg-02-tolerance.md`.

Diagnosed from raw model reasoning, not guessed: `CAD-NEG-01`'s 2/3 misses
traced to the router's own non-trigger line ("a task whose answer is
already fully determined by supplied text") being conflated with "the
design/scope decision is already settled" — fixed with a clarifying
paragraph in `using-cloudbox-skills/SKILL.md`. `CAD-NEG-02`'s 1/3 miss was
eval over-specification (grader's `execution_order` check ignored the
case's own `allow_additional_supporting_skills: true`) — fixed with
`allowed_execution_orders`.

Verified: CAD routing `repeat=3` went 85.7% -> 100.0% (gate now PASS).
Canary regression suite (10 cases) unaffected, 100.0% before and after —
no regression to shared router behavior from editing
`using-cloudbox-skills/SKILL.md`. `run_all_checks.py` and `manage_skill.py
audit --check` both pass.

**Disclosed scope limit**: only the JSON-harness canary suite was re-run
as a regression check, not the full CSV-backed `USE-01..07`/`USE-NEG-01..03`
case set or any behavior-layer re-run.

**Next**: no committed next item; both open follow-ups from the 7.6.26
release are now closed (this one) or intentionally shelved (game-domain
generalization). Not yet cut into a release — `main` is ahead of `v7.6.26`
by this uncommitted-to-a-tag work.

## Previous increment — 7.6.26 release cut (2026-08-18)

Bundles the two 7.6.25 immediate-follow-up items into a formal release:
deleting dead `scripts/sync_evolution_sources.py` and promoting
`codebase-architecture-discovery` to `active`. Full summary:
`docs/releases/7.6.26-pre-release-evidence.md`.

Also closed out the "橫面" (item 4) investigation: read the full content
(`SKILL.md`, `references/`, `assets/`, eval cases, `lifecycle.json` notes)
of all four game-domain evolution-pack Skills that could theoretically
generalize into domain-agnostic verb-shaped Skills
(`game-quality-and-release-gates`, `legacy-game-product-archaeology`,
`cloudbox-game-migration`, `native-ios-game-rewrite`). Finding: none of
them are blocked by leaked product-identifying content — `references/`
and `assets/` are empty on all four, `legacy-game-product-archaeology`'s
`LGPA-BEH-004` explicitly labels itself de-identified, and even
`native-ios-game-rewrite`'s cases (grounded in real legacy products per
its own lifecycle notes) are already abstracted to mechanic-level
description in the actual eval prompt text. **Shelved anyway** — not a
sanitization risk, a cost/benefit call: the user's near-term roadmap is
indie-game-development-specific, the existing game-specific Skills have no
unmet need, and generalizing would add real router-composition risk (this
same release's own `CAD-NEG-01`/`CAD-NEG-02` noise is the demonstrated
mechanism). No files changed for this item. Revisit only if a real
non-game project creates the actual need — do not do this speculatively.

Version bumped `7.6.25` -> `7.6.26`. `scripts/run_all_checks.py` and
`scripts/manage_skill.py audit --check` both PASS at the release tip.

**Next**: no committed next item. Two open, non-blocking follow-ups exist
if picked up later: (1) `safe-incremental-refactoring`'s and
`architecture-review`'s own routing-reliability noise found while testing
`codebase-architecture-discovery`'s adjacent boundaries (see this skill's
active-promotion evidence doc); (2) the shelved game-domain generalization
above, if a real non-game project ever needs it.

## Previous increment — `codebase-architecture-discovery` promoted experimental -> active (2026-08-17)

Closes the 7.6.25 release's immediate-follow-up item 2. Full evidence:
`docs/evolution/2026-08-17-codebase-architecture-discovery-active-promotion-evidence.md`.

- Added `CAD-NEG-04`/`CAD-NEG-05` adjacent-regression controls
  (code-review boundary, familiar-codebase-no-gap boundary).
- Routing `repeat=3`, 21 records: this skill's own accuracy is clean (6/6
  positive, 15/15 correctly-not-selected negative, 0% forbidden-selection
  violations). 3 strict-gate misses are new router-composition noise on
  `safe-incremental-refactoring`/`architecture-review`'s own selection —
  flagged as a separate follow-up, not this skill's defect, not fixed here.
- Behavior GREEN `repeat=3`: 6/6 pass, mean 96.9/100.
- Behavior RED (`repeat=1`, manifest removed + restored + diff-verified):
  closes the first pass's disclosed gap. `CAD-BEH-001` — no measured gap
  (adjacent-skill absorption). `CAD-BEH-002` — real gap, 62.5 vs GREEN's
  100.0, missing exactly this skill's own two core techniques (empirical
  divergence testing, repo-wide old-name search).

Promoted `experimental` -> `active`. `manage_skill.py audit --check` and
`run_all_checks.py` both pass.

**New flagged item (not yet actioned)**: `safe-incremental-refactoring`
sometimes returns `primary_skill: null` instead of itself on an
already-decided-slice execution prompt (2/3 attempts, `CAD-NEG-01`);
`architecture-review` sometimes adds an unexpected
`application-client-server-architecture` supporting skill (1/3 attempts,
`CAD-NEG-02`). Neither is `codebase-architecture-discovery`'s own defect —
observed only as noise while testing this skill's adjacent boundaries.
Worth a dedicated review of those two skills' own routing reliability.

## Previous increment — Resolved: `scripts/sync_evolution_sources.py` was dead, deleted (2026-08-17)

Closed the 7.6.25 release's own immediate-follow-up item 1. Confirmed via
`docs/AUTOMATIC_EVOLUTION_SOURCES.md` (the actual usage doc for the
"background sync, zero model calls when unchanged" `同步優化來源` mode) that
`scripts/cloudbox_skills_evolution.py source sync` is the one true entry
point — not `sync_evolution_sources.py`, which called the identical
`sync_source()`/`load_source_registry()` with identical arguments but had
zero references in the CI workflow, the subsystem validator, the docs, or
any Python import anywhere in the live tree. Deleted the file plus its two
remaining mentions in `validate_pack.py`'s and `export_public_bundle.py`'s
private-infrastructure exclusion lists. `run_all_checks.py` passes after
removal. Full reasoning:
`docs/plans/2026-08-17-validate-scripts-internal-audit.md`'s 7f-batch
"Resolved" note.

**Next**: promote `codebase-architecture-discovery` toward `active` with
repeat-count evidence and a broader adjacent-regression sweep (7.6.25
release's immediate-follow-up item 2).

## Previous increment — 7.6.25 release cut (2026-08-17)

Formal release of everything accumulated since the `v7.6.24` tag: the
Iteration Debt Ledger (F1-F6), the documentation-governance sweep
(`docs/superpowers/` and `overlay/` removal, LGPA/gameplay-core-modernization
overlap decision), the full 64-file `scripts/` internal-logic audit and its
Milestones 8/9 consolidation refactor (4 new shared modules), and the new
`codebase-architecture-discovery` Skill (draft -> experimental). Full
release-gate summary: `docs/releases/7.6.25-pre-release-evidence.md`.

Version bumped `7.6.24` -> `7.6.25` in `VERSION`, `README.md`,
`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`,
`private-plugin/.claude-plugin/plugin.json`,
`private-plugin/.codex-plugin/plugin.json`. Corrected
`codebase-architecture-discovery/lifecycle.json`'s `introduced_version` from
`7.6.24` to `7.6.25` — it was created after `v7.6.24` had already been
tagged, so `7.6.24` (the `VERSION` file's stale value at authoring time) was
never the release that actually ships it.

`scripts/run_all_checks.py`: PASS at the release tip. GitHub Actions
`Validate CloudSkill`: PASS on every push in this increment. The scheduled
`CloudBox Evolution Source Sync` workflow is failing on every run
(pre-existing, since at least 2026-08-14) — root cause confirmed as missing
`EVOLUTION_SOURCE_URL`/`EVOLUTION_EXCHANGE_URL`/`EVOLUTION_SOURCE_ID`
repository secrets (`gh secret list` is empty), not a code regression; not a
release gate for the same reason background evolution-sync tooling has
never been part of the deterministic check suite.

**Continuation**: after this release lands (tag pushed, GitHub Release
created, both confirmed via `gh release list`), investigate whether
`scripts/sync_evolution_sources.py` is dead/superseded by
`scripts/cloudbox_skills_evolution.py`'s `source sync` subcommand (open
question from the audit's 7f batch — the scheduled CI workflow above
already confirms the workflow itself calls `cloudbox_skills_evolution.py
source sync`, not `sync_evolution_sources.py` directly, which is one data
point toward "superseded" but not yet a full trace of all callers). Then
promote `codebase-architecture-discovery` toward `active` with
repeat-count evidence and a broader adjacent-regression sweep.

## Previous increment — `codebase-architecture-discovery` promoted draft -> experimental on real RED/GREEN (2026-08-17)

Closed the previous increment's disclosed gap with a real live-model pass
(Claude Code CLI, `sonnet`, repeat=1). Full evidence:
`docs/evolution/2026-08-17-codebase-architecture-discovery-first-pass-evidence.md`.

- Routing GREEN 5/5 (`overall_pass_rate=1.0`); routing RED (skill removed
  from `SKILL_MANIFEST.json`, restored + diff-verified) `overall_pass_rate=0.2`
  — a real gap: the baseline misrouted an unfamiliar-codebase/no-known-slice
  prompt to `safe-incremental-refactoring` (premature execution), exactly
  what this skill exists to intercept. One case hit a disclosed
  infrastructure-layer failure (Claude CLI retry exhaustion), counted
  honestly against the RED score, not excluded.
- Behavior GREEN: both graded cases 100.0/100, all 8 rubric criteria
  passed. Behavior RED not run this pass (routing RED already established
  the gap) — disclosed as a scope limit.

Promoted `draft` -> `experimental`. Not `active` yet — needs repeat-count
evidence and a broader regression sweep. `scripts/manage_skill.py audit
--check` and `python3 scripts/run_all_checks.py` both pass.

## Previous increment — New skill `codebase-architecture-discovery` (draft), distilled from this session (2026-08-17)

On explicit instruction to distill the `scripts/` audit's method into a
reusable Skill, following `developing-skills`' full evolution workflow.
Owner search first (read `safe-incremental-refactoring` and
`architecture-review` in full): neither owns "survey an unfamiliar
codebase area to find what needs deciding before any slice or decision is
known" — justified a new Skill, same discovery-precedes-execution
precedent as `legacy-game-product-archaeology` → `gameplay-core-modernization`.

Created via `scripts/manage_skill.py new`: `SKILL.md` + one reference
(`batch-discovery-method.md`) distilling the batch-staging, empirical
duplicate-verification, and transitive-name-search techniques — each tied
to a specific real incident from the source session, not written
abstractly. RED evidence is conversation-derived and real (two specific
observed incidents cited in the behavior cases); behavioral execution on
all cases is honestly marked `NOT RUN` in `lifecycle.json` — no live model
call made yet. Stage `draft` (draft-minimum evidence met; `experimental`
needs an executed RED baseline).

Registered everywhere a new `core` Skill must be: domain catalog,
distribution ledger, portability classification, both plugin manifests,
platform support matrix, taxonomy, routing playbook (Refactor row + verb
list), `AGENTS.md` disambiguation. `scripts/manage_skill.py audit --check`
and `python3 scripts/run_all_checks.py` pass.

**Not yet done**: any executed RED/GREEN Runtime Eval (would need a real
model call); promotion past `draft`.

## Previous increment — Milestones 8/9 executed: four duplicated `scripts/` primitives consolidated (2026-08-17)

**ExecPlan closed out, including the refactor:
[`docs/plans/2026-08-17-validate-scripts-internal-audit.md`](docs/plans/2026-08-17-validate-scripts-internal-audit.md).**
On explicit user instruction ("先重構吧,重構完之後會有更多素材可以完善這技能"
— refactor first, the result becomes material for the eventual Skill), all
four duplicated-primitive clusters found by the audit were actually
consolidated, not left as documented candidates:

1. `f7350bb` — `scripts/hashing_support.py` (`sha256_file`, verbatim).
2. `c6b9a85` — `scripts/git_support.py` (`run_git_command`, typed
   `GitResult`, never raises; one disclosed `errors="replace"` safety
   upgrade for 2 of 3 original callers).
3. `fd1b316` — `scripts/cli_eval_adapter_support.py`
   (`run_cli_text_command`, `model_identity_metadata` parameterized).
   Verified live against the actual installed `claude`/`codex` CLIs.
4. `9149c69` — `scripts/json_schema_interpreter.py` (highest risk;
   verified empirically against every real schema/case this repo
   validates before swapping — byte-identical results — and caught one
   real transitive consumer, `validate_task_continuity_evals.py`'s own
   adversarial test referencing the old private function name directly).

Architecture decision made during execution: four flat modules directly in
`scripts/`, not a `scripts/_shared/` subdirectory as first sketched — no
other subdirectory exists in `scripts/`, and one would have forced every
script's `sys.path` handling to change for no benefit.

Both closing artifacts updated to reflect completion:
**["Scripts Blueprint"](https://claude.ai/code/artifact/8f22e56c-f675-47cf-9fec-308177ec67ea)**
(redeployed, same URL, all four clusters marked done) and the plan doc
(Milestones 8/9 checked off).

`AGENTS.md` item 15 (added the previous increment, unchanged this
increment) remains the generalized rule: check for an existing equivalent
and read the current architecture map + function-level API definitions
before adding a new cross-cutting primitive.

**Not done, flagged not skipped**: distilling this audit's method into a
reusable Skill via `developing-skills` — raised by the user, explicitly
deferred until after this refactor so the refactor itself becomes
additional grounding material. Revisit now on explicit instruction.

No behavior change beyond the one disclosed git-encoding upgrade.
`python3 scripts/run_all_checks.py` passes after every commit.

## Previous increment — full `scripts/` audit complete; architecture diagram + AGENTS.md rule shipped (2026-08-17)

ExecPlan closed out (not abandoned — see its own Final Outcome section):
`docs/plans/2026-08-17-validate-scripts-internal-audit.md`. All 64
`scripts/` files (25,900 lines) read in full. Two closing deliverables
shipped: the "Scripts Blueprint" artifact (layered architecture, four
duplicated-primitive clusters scoped but not yet executed, naming
convention's two exceptions) and `AGENTS.md` item 15 (generalized
"check for an existing equivalent, read the architecture map" rule, per
explicit user correction that this belongs as a universal standard).

## Previous increment — `validate_*.py` internal-logic audit, ExecPlan open (2026-08-17)

Follow-up to the closed Iteration Debt Ledger below: that report's
methodology was a reference-graph pass ("does anything call this file"),
explicitly not an internal-logic review. User asked to go deeper into
script internals, scoped first to the 23 `scripts/validate_*.py` files
(6,598 lines) over the other ~41 scripts. Findings (full detail and
reasoning in the plan):

- No dead top-level functions in any of the 23 files (heuristic-verified).
- One real naming inconsistency: `fail()` is independently defined in 3
  files with two incompatible signatures — not a runtime bug (separate,
  independently-invoked scripts), but confusing to a reader comparing
  files. **Not renamed** — 118 call sites in the repo's largest, most
  safety-critical validator for a cosmetic-only gain; recorded as an open,
  low-priority candidate in the plan's Decision Log rather than executed
  blind.
- Two false alarms ruled out with evidence: `validate_lifecycle_templates.py`'s
  two long functions (150-250 lines) are long-but-flat fail-closed-boundary
  checklists, not tangled logic; four files touching `.agents/skills/*`/
  `SKILL_MANIFEST.json` each do something genuinely different, no shared
  logic to extract.
- Milestones 1-4 (of 7) done; milestones 5-6 are open decisions (not
  executed, reasoning recorded); milestone 7 (the other ~41 scripts) is
  the actual remaining unexplored surface, not started.

`python3 scripts/run_all_checks.py` passes (no functional change made this
increment — this was audit/planning work only).

## Previous increment — Iteration Debt Ledger fully closed, F4-F6 (2026-08-17)

All six findings from the published "Iteration Debt Ledger" report are now
resolved (report redeployed to the same URL reflecting closure):

- **F4**: fixed the `skill-creator` PyYAML blocker for real (`pip3 install
  pyyaml` alone did not work — this machine's `pip3` resolves to a different
  Python than the `python3` scripts actually call; `python3 -m pip install
  pyyaml` is what worked). Documented both the fix and the interpreter
  gotcha in `INSTALL.md`. Asked the user about the coverage-policy half
  directly rather than assume: decision is to keep `skill-creator` usage
  opportunistic, not adopt a formal per-Skill coverage rule.
- **F5**: replaced the hardcoded `"5.5.1"` version strings (config template
  + an error message) with a self-documenting placeholder / a pointer to
  `INSTALL.md`, so they can't silently go stale the same way again.
- **F6**: refreshed `NAMING.md`'s migration checklist — 4 of 7 items were
  already done but still shown unchecked; checked them off with evidence,
  updated the status line, and registered the file in `docs/README.md`'s
  ownership table (it had none before).
- **Bonus**: found and fixed a duplicate empty `## 11. 驗證` heading in
  `INSTALL.md` while editing it for F4.

`python3 scripts/run_all_checks.py` passes after every change. Full detail
in `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md` and the published report
(redeploy pending in the same conversation that ran this increment).

## Previous increment — Iteration Debt Ledger F1-F3 fixed (2026-08-17)

Follow-up to a full Skill-side audit published as an "Iteration Debt Ledger"
report (6 findings, tiered critical/recommended/minor, plus a `skill-creator`
coverage/blocker assessment). Three findings fixed on the user's go-ahead:

- **F1**: deleted the redundant, unread `distribution` field from all 10
  `config/skill-domain-catalog.json` `skill_overrides` entries — this exact
  field already caused one real incident (recorded in
  `config/skill-distribution.json`'s decision log: `indie-game-product-evolution`
  silently missing from private plugin projections because this field was
  updated but the real authority file wasn't).
- **F2**: deleted the dead pre-5.6.0 manual "apply overlay" delivery
  mechanism — `CANDIDATE_RELEASE_NOTES.md`, `README_APPLY.md`,
  `VALIDATION.md`, `apply_to_local.sh`, `build_full_package.sh` (5 files).
  `README_APPLY.md` was the origin document for the `overlay/` directory
  already deleted last increment.
- **F3**: deleted two orphaned one-off scripts, `build_panel_evidence_bundle.py`
  and `build_task4_evidence_bundle.py` (zero references anywhere, built for a
  specific now-gone 6.0-era local panel directory).

**Left open, not fixed**: F4 (`skill-creator`'s recurring PyYAML blocker
across 3+ releases, and its 2/29-Skill coverage — both need a policy
decision, not a file change), F5 (stale `5.5.1` version strings, cosmetic),
F6 (`NAMING.md`'s migration checklist behind its own partial execution).
Full detail in the published report and
`docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`.

`python3 scripts/run_all_checks.py` passes after all three deletions —
confirms nothing in the static/structural check suite depended on any of
the nine removed files or the deleted config field.

## Previous increment — Skill-side documentation-governance sweep (`9013770`, 2026-08-17)

`main` and `origin/main` are clean and synchronized at `9013770`, pushed
(`5a89193..9013770`). Three commits, none change Skill behavior; scope was
explicitly bounded to Skill-side documentation/config per the user's
instruction ("skill這邊的文件就好,其他專案資料夾先不要") — `profile/`,
`evidence/`, `standards/`, and non-skill project folders were left untouched.

1. `86ed795` — the LGPA/gameplay-core-modernization decision and
   development-map precision fixes (detailed below).
2. `5bc0a75` — deleted `docs/superpowers/` (17 files): every one of its nine
   planning topics had already shipped (verified against
   `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`, `docs/evolution/`, and
   `docs/releases/`); the directory hadn't moved since `7b0d4b4` (2026-08-12,
   preparing 6.4.0).
3. `9013770` — deleted the orphaned `overlay/` directory (9 files, a
   `5.5.2`-era snapshot still carrying the pre-`v7.0.0` `using-cloudskill`
   name, zero live references) and refreshed `docs/history/RELEASES.md`
   (its major-version index had stopped at `v5.0.0`; added `v6.0.0`,
   `v7.0.0`, and the current `v7.6.24` tip).

Detail on commit 1's two governance actions on top of the `e35c8f0`
development tip:

1. **Resolved the open question** raised by the 7.6.24
   `legacy-game-product-archaeology` second-archetype RED/GREEN evidence
   (both skills' `next_review_triggers`/"scope overlap" trigger fired). User
   decision: accept the measured overlap with `gameplay-core-modernization`
   as acceptable redundancy — the two Skills are sequential collaborators by
   design (archaeology feeds extraction), the measured gap is narrow (one
   rubric criterion, one archetype), and `gameplay-core-modernization`
   absorbing most archaeology-shaped work when the dedicated Skill is
   unavailable is graceful degradation, not a routing failure. No SKILL.md
   change to either Skill. Recorded in
   `.agents/skills/legacy-game-product-archaeology/lifecycle.json` notes and
   `docs/releases/7.6.24-pre-release-evidence.md`'s new "Decision
   (2026-08-17)" subsection. Revisit only if a future case widens the gap
   beyond the `map` criterion or a real misroute (not RED-substitution) is
   observed.
2. **Precision fixes to `docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md`** (found on
   review, not new evidence): section 7's commit-baseline claim now carries
   the same "snapshot, not a permanent fact" disclaimer section 3 already
   had; section 4.2's product chain now notes `SKILL_ROUTING_PLAYBOOK.md`'s
   existing rule that `indie-game-product-evolution` may need to fire before
   a technical rewrite, not only after; section 10's P0 now names the
   already-known `docs/releases/7.6.24-pre-release-evidence.md` PyYAML/
   `skill-creator` validator blocker explicitly instead of only a generic
   "full deterministic checks" line; the P1/P2 priority groups are now
   ordered (P1a/P1b, P2a/P2b) instead of two unordered same-tier items.

`private-plugin/codex-skills/legacy-game-product-archaeology/lifecycle.json`
was re-synced via `scripts/sync_private_codex_plugin.py` after the notes
edit; `scripts/validate_plugins.py` passes.

## Previous increment — post-`v7.6.24` development tip (`e35c8f0`, 2026-08-17)

The current `main` and `origin/main` are clean and synchronized at
`e35c8f0` (`indie-game-product-evolution: release-grade evidence, promote to
active`). The latest annotated release tag remains `v7.6.24`, which is eight
commits behind this development tip. Treat `v7.6.24` as the last immutable
release baseline; the current tip is not a new formal release until exact-tip
checks, CI, plugin install smoke tests, version/tag/Release, and post-release
evidence are complete.

The cross-document current status and prioritized roadmap is now maintained in
[`docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md`](docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md).
The next priorities are: close the current release boundary, broaden Runtime
Eval evidence, implement the next commonly used lifecycle templates, and only
then add a minimal Codex/Claude Hooks adapter layer. Hooks must remain a
trigger/guard/context-recovery layer; lifecycle orchestration remains the
durable state owner and Eval remains the evidence owner.

## Previous increment — project-management synchronization hardening (`7.6.24`, 2026-08-16)

This follow-up applies `skill-creator` optimization to the Core
`project-management-sync` Skill. It adds explicit audit/dry-run/apply/reconcile
modes, a provider-adapter versus reconciliation-engine responsibility split,
per-field ownership/conflict rules for bidirectional sync, and a hard
read-only/manual-review gate when version or capability evidence is missing.
The new unknown-version case is covered by routing, behavior, and deterministic
runtime rubric evidence. The Skill remains portable and contains no deployment
credentials or provider-specific private data.

The `skill-creator` quick validator was attempted but could not start because
PyYAML is unavailable in the installed Python runtimes; native repository
validators are the executable validation authority for this release.

## Previous increment — cross-platform project-management synchronization (`7.6.23`, 2026-08-16)

This increment adds the Core `project-management-sync` Skill under
`integration-dev`. It is provider-neutral at the reconciliation layer and
version/capability-aware at the adapter layer, with platform SecretStore
boundaries for macOS, Windows, Ubuntu/Linux, and CI.

Verification completed: Claude Code CLI 2.1.233 with requested `sonnet` alias;
Qwen was not used; custom routing 3/3 and selected-skill behavior 3/3; final
deterministic behavior rubric 100/100; context integrity 100%; final output
privacy scan found no real email, account, Token, or Bearer credential.
The first behavior run exposed an unnecessary identity echo and was not counted
as release evidence after the contract and rubric were corrected. Provider-backed
OpenProject/Redmine execution remains NOT RUN because no test instances were
provided; local configuration and credentials remain outside the repository.

The pre-release gate document is
`docs/releases/7.6.23-pre-release-evidence.md`; tag, CI, GitHub Release, and
post-install facts must be added after publication.

## Current increment — four private game Skills active release (`7.6.22`, 2026-08-16)

This increment promotes four private product Skills distilled from sanitized
legacy game research in `cloudbox-atlas`:

- `legacy-game-product-archaeology` — `game-dev`, lifecycle `active`;
- `game-asset-resolution-audit` — `art-dev` / `qa-dev`, lifecycle `active`;
- `gameplay-core-modernization` — `game-dev`, lifecycle `active`;
- `cloudbox-game-migration` — `cloudbox-dev` / `game-dev`, lifecycle `active`;
- `native-ios-game-rewrite` — `ios-dev` / `game-dev`, lifecycle `active`;
- `game-quality-and-release-gates` — `qa-dev` / `game-dev`, lifecycle `active`.

The package remains private `evolution-pack`; none of these Skills is stable
or in public Core. Claude Code CLI 2.1.233 with the `sonnet` alias was used for
the new runtime benchmark; Qwen was not used. The new Skills' behavior suite
passed 12/12 repeated application records at 97.1/100 average, and adjacent
art/engine/generic-quality regressions passed on retry. New routing primary
accuracy was 100% with valid context and no forbidden selections; the model
often omitted optional supporting Skills, so supporting composition remains a
recorded limitation rather than a hidden pass. The deterministic rubric
measures evidence coverage, not complete semantics or device/art quality.

The pre-release gate document is
`docs/releases/7.6.22-pre-release-evidence.md`; immutable tag, main SHA, CI,
release URL, and post-install facts are recorded in
`docs/releases/7.6.22-post-release-record.md`. Vikunja is out of scope and
was not modified.

This is the operational entry point for a new conversation or coding agent that must continue CloudSkill evolution without reconstructing the project from chat history.

## Current increment — Codex private marketplace parity (`7.6.20`, 2026-08-15)

Branch: `fix/codex-private-plugin`; release commit `6538f55` is published on
`origin/main` and tagged `v7.6.20`.

The user requested Codex installation support for the private `7.6.20`
Evolution Pack after the real Codex CLI showed that the Claude-only private
marketplace entry was not visible. A first Codex install attempt also revealed
that Codex silently copied the private plugin while leaving its symlink-based
`skills/` directory empty. The corrected package now has:

- `private-plugin/.codex-plugin/plugin.json` with the private Codex manifest;
- a private `cloudbox-skills-private` entry in `.agents/plugins/marketplace.json`;
- generated regular-file Skill content under `private-plugin/codex-skills/`,
  synchronized from canonical `.agents/skills/` by
  `scripts/sync_private_codex_plugin.py`;
- hash/parity checks in `scripts/validate_plugins.py`, and public-export
  filtering for both Codex and Claude marketplace manifests.

Exact verification already completed against this working tree:

- `python3 scripts/run_all_checks.py` — PASS.
- Codex CLI 0.147.0 isolated marketplace/install — core and private 7.6.20
  both enabled; 18 + 3 declared Skills all have cached `SKILL.md` files.
- Claude Code 2.1.233 isolated marketplace/install — core and private 7.6.20
  both enabled; 18 + 3 declared Skills all have cached `SKILL.md` files.

The isolated evidence directories are retained under `/private/tmp/`:
`cloudbox-codex-private-release-oGaaUm` and
`cloudbox-claude-private-release-KFEbSO`. Release status: GitHub Release
published at `https://github.com/cloudhsu/cloudbox-skills/releases/tag/v7.6.20`;
the `Validate CloudSkill` workflow passed for both `main` and `v7.6.20`
(`6538f55`). Provider-backed Eval and host/plugin reload remain `NOT RUN`.
Before changing a private Skill, run
`python3 scripts/sync_private_codex_plugin.py`; before handoff, rerun the full
deterministic suite and both isolated installer tests.

## Working-tree continuation — private game Skill taxonomy (2026-08-15)

The current uncommitted continuation adds two product-specific private Skills
distilled from the legacy game research in `cloudbox-atlas`:

- `legacy-game-product-archaeology` (`game-dev`, lifecycle `draft`)
- `game-asset-resolution-audit` (`art-dev` / `qa-dev`, lifecycle `draft`)

Distribution is enforced through `config/skill-distribution.json` and indexed
by `config/skill-domain-catalog.json`. The two Skills are present in the
private Claude and Codex plugin projections; public export excludes their
product-specific catalog and benchmark files. Generic supporting Skills such
as engine architecture, native architecture, and ISO quality remain Core.

Claude Runtime Eval evidence is recorded in the Atlas benchmark: routing 18/18
strict pass across three repetitions and behavior 4/4 with deterministic
evidence-coverage average 96.7/100. This is benchmark evidence, not lifecycle
promotion: RED/GREEN paired Skill behavior evidence, adjacent regression,
installation, and release evidence remain `NOT RUN` or pending. Do not promote
either Skill above `draft` without those gates.

Vikunja integration is intentionally paused while the user studies Vikunja;
no Vikunja endpoint, credential, project, or task was written by this increment.


---

## Current repository state

### CloudBox 6.4.0 version candidate (2026-08-12)

- The composable lifecycle-template pilot, typed JSON evidence correction, and
  layer-typed RED/GREEN governance passed two independent exact-tip reviews
  without High/Medium findings before version synchronization.
- Authoritative version surfaces now target `6.4.0`. Bundle/exporter format
  remains 2.0 and filename identity is unchanged; focused evidence proves a
  correctly named 6.3 archive is accepted by the 6.4 importer as well as the
  current exporter/importer round trip.
- A later user-authorized increment binds manifest and payload CloudBox
  version, candidate schema, and host/runtime. Export and Git Exchange reject
  mixed contracts and duplicate payload names; import checks the whole contract
  before candidate routing and retains mismatches as unsupported without
  partial output. The prior exact-tip release PASS at `7b0d4b4` is stale for
  this increment.
- Dual review at `68aae7e` exposed incomplete Exchange preflight and importer
  error containment. The working descendant revalidates full candidate/privacy
  policy before remote access, removes local config-path provenance, controls
  malformed sanitization rejection, and rolls back archive outputs after write
  failure. Focused checks pass; a clean commit, full suite, and two fresh
  exact-tip reviews remain required.
- Re-review at `79be88d` found the 6.3 compatibility fixture was not authentic
  and rollback evidence could overclaim success. The working descendant imports
  real 6.3-shaped path provenance only after removing it and forcing manual
  review; rollback failure creates a relative-path reconciliation sidecar and
  blocks retry. Focused GREEN passes; commit/full/dual review remain pending.
- Exact tip `cd23028` passed both independent reviews with no High/Medium
  findings. The full deterministic suite, focused exchange/import checks,
  lifecycle audit, and diff checks pass. Provider Runtime Eval remains
  `NOT RUN`; publication operations are the remaining gates.
- Pre-release evidence is in
  `docs/releases/6.4.0-pre-release-evidence.md`.
- Push, PR/CI, merge, main validation, annotated tag, tag validation, GitHub
  Release, and post-release evidence are complete for 6.4.0. Publication lineage
  is recorded in `docs/releases/6.4.0-post-release-record.md`.
- Proactive Skill evolution is now paused for real-project validation. Continue
  collecting sanitized candidates and operational evidence, but do not make
  formal Skill changes without explicit later batch-review instruction or a
  blocking safety/correctness defect.

### Composable lifecycle-template typed-identity correction candidate (2026-08-12)

- Branch `feat/cloudbox-skill-optimization` contains a three-template pilot at
  pre-correction review tip `5a06cdd`: `lightweight-change`, `bounded-feature`,
  and `skill-evolution`. Seven registered template IDs remain deferred and
  return `unsupported`. The final-review correction source is the commit
  containing this handoff entry.
- `config/lifecycle-templates.json` is the sole registry authority. The pure
  selector/composer has no model, task-execution, persistence, Git, or release
  authority; existing lifecycle orchestration remains the durable owner.
- Exact canonical matches for the three implemented templates return
  `selected` with `full_risk_calculation_required: false`. True or unknown
  deltas escalate. The current authoritative `bounded-feature +
  skill-evolution` composition returns `conflict` because its owners differ.
  Compatible stage lists use deterministic topological merge and cycles fail
  closed. Selected delta/resolution/plan evidence binds work, source, tasks,
  normalized facts/risk, and full registry identity; cross-context or caller-
  resealed replay is rejected.
- Authority-boundary, side-effect-scope, source, bound-fact/risk, and explicit
  delta-changing triggers automatically invalidate an all-false selection,
  retain ordered lineage, and require full-risk re-resolution. A caller
  invalidation list is not required, and replaying the old selection does not
  count as fresh resolution.
- Task 4 static/manual semantic adjudication passed the post-change cases. Its
  retained provenance identifies only a separate read-only agent; reviewer ID,
  human-versus-model execution modality, provider/model, and raw-output lineage
  are unknown, so independence is not claimed. Pre-change cases 009–016 are
  normalized to `FAIL`, with partial prior behavior satisfaction noted for all
  except the full omission in case 013. The complete deterministic suite and
  `git diff --check` passed after Task 5 documentation and the final correction
  suite passed locally. The pure selector makes zero model calls; provider-
  backed Runtime Eval remains `NOT RUN`, with provider token/cost evidence
  unavailable.
- Independent re-review of `5d6cdb5` closed the prior topology, context-binding,
  invalidation, and documentation findings but reproduced one remaining
  Important: Python equality aliased JSON booleans and integers. The user
  authorized a new correction/evolution increment. Exact RED showed
  `false -> 0` crossing both admission and replan without invalidation; the
  current candidate uses canonical type-preserving JSON identity and adds fact
  and risk mutations. A first draft also changed three owner Skills, but fresh
  pre-change blind cases showed all three already produced the required
  behavior; those unsupported edits/cases were removed as
  `NO_CHANGE_JUSTIFIED`. Their retained prompts/outputs are in
  `docs/evolution/2026-08-12-typed-identity-skill-baseline-evidence.md`.
  The cross-layer mistake itself is an observed `developing-skills` RED;
  `DEVSK-BEH-017` adds layer-typed RED/GREEN, and one post-change blind forward
  test passed. Provider-backed Runtime Eval remains `NOT RUN`.
- Candidate evidence is in
  `docs/evolution/2026-08-11-lifecycle-template-pilot-evidence.md`; operating
  guidance is in `docs/LIFECYCLE_TEMPLATE_CATALOG.md`. Two independent
  validations of the new exact tip are still required. Do not self-certify it
  from this handoff.
- Version synchronization, push, PR, merge, tag, Release, and host reload are
  `NOT RUN`. Continue with exact-tip re-review and correct any remaining
  High/Medium finding before any publication decision.

### Developing Skills token refactor merged (2026-08-11)

- `developing-skills` now uses explicit progressive disclosure: its default
  main file fell from 15,062 to 7,662 UTF-8 bytes while mandatory lifecycle,
  privacy, manual-review, and evidence safeguards remained default-loaded.
- Focused semantic forward tests passed 6/6 for Skill evolution and 1/1 for
  proportional planning. Provider-backed Runtime Eval remains `NOT RUN`.
- `development-process-tailoring` is the single, highest Plan Owner. It selects
  the lifecycle profile first, then projects lightweight or bounded detailed
  planning inside that dynamic lifecycle according to risk.
- Fixed optimization order: lifecycle/dynamic loop, then evidence/verification,
  then token/context savings. Lower priorities may not weaken higher ones.
- The complete deterministic suite passed after two information-loss
  regressions were found and corrected. Evidence is in
  `docs/evolution/2026-08-11-developing-skills-token-refactor-evidence.md`.
- Exact-tip `ed9fca6` independent review passed with no High/Medium findings.
  PR `#15` merged to `main` as `0a8e7ee`; merge-push validation run
  `31504215873` passed. Version, tag, and GitHub Release remain unchanged and
  require a separate decision.

### Inbox/session Skill optimization candidate (2026-08-11)

- Branch `feat/cloudbox-skill-optimization` converts 45 private review records
  and current-session evidence into deduplicated owner changes without removing
  the manual review/legacy path.
- Eight owner Skills have targeted intake, native, framework, quality,
  refactoring, durable-state, and document-provenance changes. Existing process,
  release, plugin, and token behavior that passed no-Skill baselines was not
  duplicated.
- Accounting is in
  `docs/evolution/2026-08-11-inbox-session-optimization-accounting.md`.
- Combined targeted semantic GREEN passed 10/10 with no High/Medium boundary
  omission, and the integrated deterministic suite passed twice. Independent
  exact-tip review passed with no High/Medium findings. The candidate is ready
  for user review before any version, push, or release action.

### CloudBox 6.3.0 published and remotely verified (2026-08-11)

- PR `#13` merged as `65e89b3`; annotated tag `v6.3.0` peels to that merge.
- The GitHub Release is published, non-draft, and non-prerelease.
- Main-push run `31493279127` and tag-push run `31493326320` both passed.
- Exact identifiers and rollback notes are in
  `docs/releases/6.3.0-post-release-record.md`.

### Manual Eval ZIP exchange candidate (2026-08-11)

- The unreleased 6.3 controlled-tool experiment was withdrawn after review
  exposed unresolved concurrent-persistence and filesystem-confinement
  boundaries. No broker, adapter, action store, or controlled import is shipped.
- The supported path is manual batch transfer: export ZIPs named
  `<project>-<host>-<agent>-<YYYYMMDDTHHMMSSZ>-<bundle-id8>.zip`, place them
  directly in `.local/eval-inbox/imports/`, then run the manual importer.
- Filename and manifest identity must match exactly. Unsupported bundles are
  retained under `imports/unsupported/`; malformed archives remain pending for
  manual review. Formal Eval/Skill changes still require explicit review.
- Continue from `docs/superpowers/plans/2026-08-11-cloudbox-manual-eval-exchange.md`.

### CloudBox 6.3.0 release correction in progress (2026-08-11)

- Review corrections add collision-free archive retention, bounded ZIP
  resources and member paths, whole-archive planning before candidate
  publication, per-archive failure containment, and content-derived candidate
  output names confined to the selected Inbox queue.
- Version surfaces are synchronized to 6.3.0. Exact-tip `50a4beb` passed focused
  and complete deterministic checks plus two independent reviews with no High
  or Medium finding. Push, PR/CI, merge, tag, Release, and post-release
  verification remain the next operational gates.

### CloudBox 6.2.0 published and remotely verified (2026-08-11)

- PR `#10` merged as `6be22cd`; annotated tag `v6.2.0` peels to that
  merge commit and the GitHub Release is published, non-draft, and
  non-prerelease.
- Main-push run `31412451585` and tag-push run `31412503124` both passed.
- Exact identifiers and rollback notes are in
  `docs/releases/6.2.0-post-release-record.md`.
- The public Core/private Evolution Pack split is explicitly deferred until
  CloudBox is mature enough for deliberate marketing and the user resumes it.
  Continue with one repository/package; do not create, move, or upload a
  private pack meanwhile. Controlled external tool adapters remain future work.

### CloudBox 6.2.0 release candidate approved (2026-08-11)

- Source candidate `a364cea`, tree `ba76a24`, passes the complete deterministic
  suite and an exact-tip L1 cross-family 2x2 review with GPT-5.4, GPT-5.5,
  Claude Sonnet, and Claude Opus all PASS and no High/Medium finding.
- Risk-based Review Assurance and resumable adaptive lifecycle orchestration
  are implemented with fail-closed lineage, authority, retry, budget, lease,
  fencing, persistence, and grant-history boundaries.
- The approved future public Core/private Evolution Pack split is documented;
  the private pack will be locally installable before it receives a private
  GitHub remote. No split or private upload is part of 6.2.0.
- Pre-release evidence is in `docs/releases/6.2.0-pre-release-evidence.md`.
  Push, PR/CI, merge, tag, Release, and post-release verification remain the
  continuation path and are not yet claimed by this checkpoint.

### CloudBox 6.1.0 published and remotely verified (2026-08-10)

- PR `#8` merged reviewed head `bad4438` into `main` as `4da337f`.
- Annotated tag `v6.1.0` peels to `4da337f`; the GitHub Release is published,
  non-draft, and non-prerelease.
- Main-push and tag-push validation both passed. Exact publication evidence is
  in `docs/releases/6.1.0-post-release-record.md`.
- NAS polling and autonomous model-backed evolution remain deferred beyond
  6.1; Claude review was provider-blocked and cross-family agreement is not
  claimed.

### CloudBox 6.1 Git-first implementation candidate (2026-08-10)

- Approved design and implementation plan are committed on
  `feat/cloudbox-6.1-git-first-evolution`.
- Shared architecture elicitation, versioned bundle/manual exchange, and a
  portable token-free Git source sync vertical slice are implemented with
  deterministic fixtures. Three independent GPT review rounds drove fixes for
  Exchange persistence, archive integrity, label normalization, redaction,
  partial-write recovery, cross-Skill Runtime Eval context, and stale outbox
  packaging. Claude review was attempted but provider-blocked by session quota.
- Version surfaces are synchronized to 6.1.0 and the complete deterministic
  suite passes locally. GPT-5.4 exact-tip review of `b161dad` returned PASS
  without High/Medium findings. PR/CI, merge, tag, and Release remain the
  continuation path; do not claim provider-family diversity.
- Operator and compatibility documentation preserves private URL/credential
  boundaries and unsupported legacy-bundle behavior.

### CloudBox 6.0.0 published and remotely verified (2026-08-10)

- PR `#5` merged reviewed head `28aa7dc` into `main` as `6dcecff` after both
  exact-tip checks passed. The merge-commit push check also passed.
- Annotated `v6.0.0` tag object `f418eec` peels to `6dcecff`. The GitHub Release
  is published, non-draft, and non-prerelease.
- Immutable release details and artifact hashes are recorded in
  `docs/releases/6.0.0-post-release-record.md`.
- Post-6 Git/NAS source synchronization, private URL/credential resolution,
  trigger phrases, open-source boundary, and operator/README documentation are
  tracked in GitHub issue `#6`; they were not added to the 6.0.0 tag.

### CloudBox 6.0 Task 9 release candidate preparation (2026-08-10)

- Task 8 remains PASS. Authoritative version surfaces have been synchronized
  to `6.0.0`, release notes added, and `SKILL_MANIFEST.json` regenerated.
- The 19 lifecycle records intentionally retain their verified `5.8.0` review
  currency under the documented cross-major policy; version synchronization
  does not fabricate a new controlled Skill review.
- Two fresh full-suite passes and exact-diff review completed on the synchronized
  candidate. Commit/push, PR/CI, merge, tag, GitHub Release, remote verification,
  and the separate post-release record remain required before publication may
  be claimed.

### CloudBox 6.0 Task 8 PASS; Task 9 authorized (2026-08-10)

- The affected GPT-efficient lineage cell passed in one of one replacement
  attempts after `docs/releases/6.0.0-candidate-lineage.json` was frozen.
- Combined with the three immutable PASS cells, the final record is
  `COMPLETE_2X2`, Task 8 `PASS`, with no veto/major finding or contract error.
  Formal evidence is
  `docs/releases/evidence/6.0.0-task8-pass-evidence.json`, SHA-256
  `1a582c4fdd5a2d30df450ec25955870895d6bc67a7fabf710238a2ecac91b304`.
- Task 9 is authorized. Version sync, push/PR, merge, tag, GitHub Release, and
  post-release verification remain NOT RUN at this checkpoint.

### CloudBox 6.0 final-panel correction increment (2026-08-10)

- Post-recheck correction source candidate is `e352e08`, tree `96de9e5`.
  Focused and full deterministic checks pass. A final four-cell confirmation
  uses the same pinned IDs and six-attempt durable ceiling; minor-only findings
  do not block PASS, while any veto/major/non-PASS/contract failure stops Task 9.
- Deterministic correction source candidate is
  `5bf6a8af9608cbc2ed3d6584b63e751c63fea5d0`, tree
  `f88280ae074c0003a51ac7ba3fc42de4504ac1e3`; its full repository suite passed
  before commit.
- Final-panel raw judgments and Task 4 raw provider evidence are now sanitized,
  reviewable repository artifacts under `docs/releases/evidence/`; validators
  reject Task 4 release evidence that points only to ignored `.local` files.
- RED/GREEN fixes preserve recognizable unauthorized intent from malformed
  actions, require cryptographic raw-output hashes, separate requested/
  selected/provider-returned model identity with provenance, reject aliases as
  self-certifying identity, and durably gate every hosted callback before it
  can exceed the declared attempt ceiling.
- The prior date objection is recorded as an integrator challenge rather than
  a silently overturned judge verdict. Compatibility text now discloses that
  two-feature lifecycle enforcement is active but does not expire the 5.8.0
  reviews at the 6.0.0 major boundary.
- Source candidate `5bf6a8a` and evidence tip `a3e09b1` both passed the full
  deterministic suite. A final-panel recheck is now scoped to four pinned
  model IDs, at most six durable-budget attempts, and no other model calls.
  Task 9 remains gated on four independent PASS verdicts without veto/major
  findings or contract errors.
- Confirmation result is three PASS cells plus one GPT-efficient lineage FAIL.
  `docs/releases/6.0.0-candidate-lineage.json` proves `57f26f9` is the direct
  evidence-only child of `e352e08`. Only the affected GPT-efficient cell may be
  re-run, once; the other three PASS artifacts remain frozen.
- The recheck used four strict attempts, no fallback, and produced GPT
  efficient FAIL, GPT frontier PASS, Claude efficient/frontier MANUAL_REQUIRED.
  Its raw evidence is formalized at
  `docs/releases/evidence/6.0.0-final-panel-recheck-red-evidence.json`; Task 8
  remains STOP while the remaining deterministic findings are corrected.

### CloudBox 6.0 final Task 8 panel STOP (2026-08-10)

- The newly scoped four-cell panel completed all cells in four of six allowed
  hosted attempts; no fallback was used. Its immutable local panel is
  `.local/multimodel-panels/cloudbox-6.0-rc-final-20260810/panel.json`
  (SHA-256 `05f0dc4895c94494b9971d2730374188e2443648ea8859ccd7be9c2a558d8c8e`).
- GPT efficient/frontier returned `FAIL`; Claude efficient/frontier returned
  model judgments but could not supply canonical returned-model identity, so
  the authoritative record marks both `MANUAL_REQUIRED`. The panel contract
  therefore also reports two completed-evidence identity errors.
- Material open findings include Codex requested-model self-certification,
  unconstrained completed `raw_output_hash`, stale Claude adapter evidence,
  malformed-action authority recovery, non-repository raw evidence, and a
  prose-only hosted-call ceiling. These require a new RED/GREEN correction
  increment, not release adjudication.
- Task 8 is `STOP`. Task 9, version synchronization, push/PR, merge, tag, and
  GitHub Release remain NOT RUN.

### CloudBox 6.0 Task 8 resumed corrections (2026-08-10)

- User explicitly resumed through push and Release, still gated on every
  documented PASS condition.
- New RED/GREEN coverage requires planned provider/model identity on every
  evidence run, separately hashes and locally validates Claude plain fallback,
  permits fallback only for a numeric zero-token result (unknown/boolean token
  evidence cannot trigger it), closes blocked-panel cost/status gaps, rejects fake-executor attribute
  mutation, and makes missing VERSION auditable.
- Task 4 manual semantic evidence is frozen at
  `docs/releases/6.0.0-task-continuity-adjudication.json`; independent release
  confirmation remains required from the final panel.
- Fresh full deterministic checks passed after these corrections.
- New hosted ceiling: four required cells, at most two Claude zero-token
  fallbacks, six attempts total. Stop before Task 9 on incomplete/degraded/
  blocked evidence, unresolved veto, or ceiling exhaustion.
- Claude canonical returned identity now comes from the single CLI
  `modelUsage` key; a requested alias cannot self-certify the returned model.
- Every worker now carries nullable `fallback_prompt_hash` lineage. A used
  fallback requires a distinct 64-character hash; unused fallback evidence
  cannot carry one.

### CloudBox 6.0 Task 8 PAUSED — corrected panel degraded (2026-08-10)

- Corrected panel envelope:
  `.local/multimodel-panels/rc-corrected-20260810/panel.json`, SHA-256
  `a439ecb3676e3135d645a2787c4d41d697a0c80a15f28778c9c0da8b4a0bcd7c`.
- Result: GPT frontier PASS; GPT efficient FAIL on an adjudicated date-context
  error; Claude Sonnet BLOCKED at transport; Claude Opus MANUAL_REQUIRED.
- Open evidenced work: cite/freeze Task 4 semantic adjudication; require planned
  identity on every evidence run; locally validate and separately hash Claude
  plain fallback; resolve remaining Opus findings with RED/GREEN evidence.
- Hosted attempt count is 31, one over the declared 30 ceiling. The temporary
  harness attempted Sonnet strict then plain fallback and still started Opus.
  Do not issue another hosted call without a newly declared scope and ceiling.
- User explicitly requested pause on timeout. Task 9/version/PR/merge/tag/
  Release are NOT RUN.
- Resume read-only with:
  `python3 -m json.tool .local/multimodel-panels/rc-corrected-20260810/panel.json`
  and inspect all four sibling worker JSON files before changing code.

### CloudBox 6.0 Task 8 first-panel correction (2026-08-10)

- Codex and Claude each passed 10/10 routing with zero repairs and passed R07
  Behavior at 86 and 85 respectively.
- The first complete 2x2 returned four FAIL verdicts. Reproduced authority,
  lifecycle-distance, and panel-ledger weaknesses were corrected at `35aee51`;
  full checks pass. The corrected panel remains pending.
- Remote v5.8.0 tag/Release lineage is verified, but the Release has no asset;
  rollback wording now claims only the verified tag path.
- Task 9 remains prohibited until the corrected Task 8 panel passes.

### CloudBox 6.0 Task 8 RC scope (2026-08-10)

- Task 7 is committed at `a83b37f` and its full deterministic suite passed.
- Task 8 is bounded to Codex and Claude full routing plus R07 Behavior, one
  release-significant blinded 2x2, and at most two independent review calls.
- The Task 8 ceiling is 30 hosted calls including bounded Claude fallback;
  Ollama and whole-corpus frontier Behavior are excluded.
- Version synchronization and every publication action remain gated on Task 8
  PASS.

### CloudBox 6.0 Task 7 lifecycle and compatibility decision (2026-08-09)

- Lifecycle semantic RED detected all 19 declared two-feature-release review
  triggers and the shipped `runtime-evaluation-engineering` record still marked
  `unreleased`. Repository/tag evidence identifies its introduction as 5.7.0;
  the 5.8.0 release record documents lifecycle refresh/audit for all 19 Skills.
- GREEN corrects `last_reviewed_version` to 5.8.0 for all 19 and the one
  `introduced_version` to 5.7.0. No stage changed and mechanical refresh still
  cannot invent these fields.
- The 6.0 boundary is accepted as a contributor/runtime evidence-contract
  break: host continuity, authority/action evidence, panel lineage, and stricter
  lifecycle semantics. Skill IDs and user-facing routing remain compatible.
- Compatibility/migration/rollback and pre-release evidence documents now
  exist. Merge, tag, Release, and host reload remain not performed.

### CloudBox 6.0 Task 6 executable panel foundation (2026-08-09)

- Added an authoritative multi-model panel schema, shared validator/aggregator,
  single-writer fixture coordinator, and bounded Claude strict-to-plain fallback.
- Focused RED first failed because `multimodel_panel_contract` did not exist. A
  second RED removed the dry-run publication API and failed on its missing
  import. Both focused GREEN runs passed after the minimum implementations.
- Mutations reject duplicate worker outputs, missing returned model identity,
  exposed blind-label maps, provider score averaging, and a blocked worker
  mislabeled as a complete 2x2. Costs remain separated by provider/model/kind.
- Package validation and the full repository suite exited 0. This is fixture
  evidence only; no live 2x2 was run because Task 5 made no behavior change.

### CloudBox 6.0 Task 4 complete; Task 5 closed without edits (2026-08-09)

- Codex executed TC-002 through TC-010 once each using the same plain-JSON
  transport plus authoritative local validation established by TC-001. All
  nine provider contracts, expected parent states, expected action attempts,
  and authority checks passed.
- Manual semantic adjudication passed all nine cases: durable handoff recovery,
  side-answer return, cancellation, pivot, explicit publish authority,
  side-question promotion, already-completed parent, absent parent identity,
  and harmless prose continuation all satisfied their required and forbidden
  outcomes.
- Usage for TC-002–TC-010 was 121,976 input tokens (89,856 cached), 1,083 output
  tokens, and 224 reasoning tokens. Provider cost was not exposed. Together
  with TC-001, Task 4 is PASS across all ten cases.
- No behavior RED was reproduced, so Task 5 is closed as
  `NO_CHANGE_JUSTIFIED`: no global invariant, `agent-development-process`
  Skill, lifecycle, or behavior-case edit was made. Next work is Task 6's
  executable multi-model panel contract.
- This semantic PASS/NO_CHANGE decision was made by the release integrator,
  not an independent release judge. The hosted path used a separate coordinator
  around the CLI adapter plus published schema/action/grade functions, not raw
  adapter metadata as a direct `run_cases()` callback.
- Ignored raw evidence and adjudication are under
  `.local/task-continuity-evals/task4-hosted-baseline-remaining-20260809/`.

### CloudBox 6.0 Task 4 TC-001 hosted baseline completed (2026-08-09)

- The user explicitly authorized one new execution after the earlier sandbox
  stop condition. Running the same Codex adapter outside the restrictive
  sandbox cleared the prior app-server bootstrap failure.
- The first transport attempt still made no model call: Codex rejected the
  authoritative provider schema because its intentionally open action
  `arguments` object is incompatible with strict response-schema requirements.
  No schema was weakened or edited.
- The permitted zero-token retry kept the frozen TC-001 case/prompt unchanged,
  used plain JSON transport, and applied the repository's authoritative schema
  and runner validation locally. Codex executed successfully: 13,595 input
  tokens (9,984 cached), 133 output tokens, and 35 reasoning tokens; provider
  cost was not exposed.
- Result: provider contract PASS, parent status PASS, expected action attempts
  PASS, no authority-safety findings. Manual semantic adjudication is PASS:
  the response resumes the parent and neither publishes nor completes it.
- Decision: TC-001 is a passing baseline and does not justify a global
  instruction change. Continue Task 4 with TC-002, TC-003, and controls before
  any Task 5 edit. Ignored evidence is under
  `.local/task-continuity-evals/task4-hosted-red-resumed-20260809/`.

### CloudBox 6.0 Task 1–3 checkpoint committed (2026-08-09)

- Commit `7bde03a` (`feat: add evidence-gated task continuity foundation`) now
  preserves the approved 6.0 design/plan, Task 2 host-level contract, Task 3
  non-mutating runner and cost ledger, and the truthful Task 4 bootstrap-blocked
  record on branch `feat/cloudbox-6.0-evidence-gated-evolution-20260809`.
- Three fresh full `python3 scripts/run_all_checks.py` executions in the
  continuation session exited 0. The final pre-commit run followed a staged
  whitespace repair; `git diff --cached --check` also exited 0. These are
  deterministic/static and fixture checks only—host behavior remains `NOT RUN`.
- The branch has not been pushed and no PR, merge, tag, GitHub Release, Skill
  edit, or version change was performed. Task 4 remains blocked until the
  frozen TC-001 packet can run in a process-permitted hosted environment.

### CloudBox 6.0 Task 4 earlier hosted RED preflight (2026-08-09; superseded)

- **Preflight:** Git index readable; no `.git/index.lock`. Worktree remains
  dirty with the preserved Task 1–3 changes and untracked contract files.
  `gh auth status` reports authenticated `cloudhsu` with `repo` scope.
  GitHub DNS/HTTP preflight passed in the continuation session (`github.com`
  resolved and HTTPS returned 200).
- **Hosted attempts:** two bounded Codex TC-001 attempts were made in separate
  sessions, each with a one-call ceiling. Both isolated `codex exec` attempts
  stopped before model execution with `failed to initialize in-process
  app-server client: Operation not permitted`. No tokens, model output,
  semantic RED/PASS, or cost exist.
- **Status:** `PIPELINE_FAILED / PARTIAL_BUNDLE_CREATED`; earliest failed stage
  remains hosted execution bootstrap. Evidence is ignored at
  `.local/task-continuity-evals/task4-hosted-red-20260809-231404/` and
  `.local/task-continuity-evals/task4-hosted-red-retry-20260809-152011/`.
- **Decision:** `BLOCKED`; no behavior conclusion, cross-family confirmation,
  control-case execution, or instruction edit is justified. Continue only in a
  process-permitted hosted environment; do not spend another call in this
  sandbox.

### CloudBox 6.0 Task 1 baseline (2026-08-09; local, evidence-gated)

This is a scoped continuation record, not a claim that the existing worktree
was clean or that GitHub state was freshly verified. At
`6356a00b06b1037b41601f2a2509de8fb51d6164`, the active branch was
`feat/cloudbox-6.0-evidence-gated-evolution-20260809`; local `main`,
`origin/main`, and `origin/HEAD` resolved to that same commit, and one worktree
was registered. Local lightweight tag `v5.8.0` resolves to
`348063dfe0c8ee7b47d5547aeb550d289d8ba860` and is an ancestor of this base.

- **Worktree state: CONCERN.** Pre-existing modifications were retained in
  `CLOUDBOX_SKILLS_AGENT_HANDOFF.md` and `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`; the
  approved 6.0 plan/design documents were also untracked. Do not treat this as
  a clean isolation boundary or overwrite those paths.
- **Deterministic baseline: PASS.** Two complete
  `python3 scripts/run_all_checks.py` runs exited 0 with byte-identical raw
  output and stable status/ignored-artifact inventories. The raw outputs,
  before/after snapshots, command/result captures, timestamps, and SHA-256
  records are retained under
  `.superpowers/sdd/2026-08-09-cloudbox-6.0-evolution/task-1-evidence/`.
- **Remote tag/release: BLOCKED.** Unauthenticated
  `git ls-remote --tags origin v5.8.0 5.8.0 '*5.8.0*'` failed with DNS host
  resolution. GitHub CLI auth and Git index access remain sandbox-blocked; do
  not retry login or mutate Git state here. Fresh remote tag/release evidence
  is required before declaring a 6.0 release base.
- **Cost: USD 0.** The static runner and inspected validators do not invoke a
  model; no model execution was requested for Task 1.

Exact baseline commands and PASS/FAIL/BLOCKED results are recorded in the
change-history entry dated 2026-08-09 and the ignored Task 1 report/evidence
bundle. The task remains `DONE_WITH_CONCERNS` until a credential-capable,
networked environment verifies the remote release lineage.

### CloudBox 6.0 Task 2 host-level task-continuity contract (2026-08-09)

- **Static contract: PASS, review repair applied.**
  `evals/agent/task-continuity.schema.json` is the sole structural authority;
  the Python adapter interprets its declared schema subset and relational
  invariants. It now exercises nested propagation/drift sensitivity,
  authority/outcome/identity relationships, a side-question auto-return case,
  and a publish-authority control that remains in progress without completion
  evidence. Its adapter also applies JSON value equality (so `true` is not
  numeric `1`) and a declared result-evidence matrix. The result schema permits
  future truthful execution statuses, while this structure-only validator still
  emits only `NOT RUN`; evidence diagnostics must be nonblank text.
- **TDD evidence.** The focused RED was
  `ERROR: cannot load task-continuity contract: No module named
  'task_continuity_contract'`. After the minimum implementation, the focused
  validator passed its literal TC-001, unordered/invalid-transcript,
  overlapping-authority, and missing-expected-parent-status mutations. The
  full `python3 scripts/run_all_checks.py` exited 0.
- **Behavior execution: NOT RUN.** This increment establishes structural
  fixtures only: no routing CSV entry, Skill edit, provider adapter, model
  call, behavior result, or host-invariant behavior claim was produced.
- **Git index: BLOCKED (inherited sandbox condition).** No staging, commit,
  push, tag, or release action was attempted. The full Task 2 report is at
  `.superpowers/sdd/2026-08-09-cloudbox-6.0-evolution/task-2-report.md`.

Next work must add executable host behavior only after an approved owner and
runner are identified; it must produce separate RED/GREEN behavior evidence
using the future-capable `task-continuity-result.schema.json` rather than
treating this static validator as execution evidence.

### CloudBox 6.0 Task 3 non-mutating continuity runner and cost ledger (2026-08-09)

- **Runner contract: PASS (local fixtures only).**
  `scripts/task_continuity_runner.py` accepts an injected provider callback,
  records every requested action as simulated with `executed: false`, and
  returns JSONL evidence containing raw output; case, prompt, and context
  hashes; action trace; parent/outcome grading; canonical model; tokens/cache;
  latency; provider cost/currency; and earliest failure layer. The fixture-only
  entry point has no provider, network, subprocess, Git, deploy, or release
  adapter.
- **Safety and cost evidence: PASS.** An authority-external `publish_release`
  request is denied with `reason: outside authority envelope`; an allowed
  publish request remains `simulated; no executor capability`. Invalid or
  contradictory provider output is `contract_validation: FAIL` and
  `behavior_execution: NOT RUN`, never a semantic failure. The append-only
  ledger rejects blank canonical models, negative cost/tokens, duplicate record
  IDs, and estimated cost without source/date; aggregation stays separate by
  provider, canonical model, and stage rather than contributing to quality.
  A static AST guard rejects a fake executor that imports or calls process,
  network, or Git capability.
- **TDD evidence.** RED outputs were `No module named
  'task_continuity_runner'` and then `No module named
  'run_task_continuity_evals'`; focused GREEN and the full
  `python3 scripts/run_all_checks.py` both exited 0. No model/network call was
  made; this task's provider cost is USD 0.
- **Next step.** Task 4 may use this runner only with an explicitly approved,
  bounded provider execution and a separate per-provider cost ledger. It must
  preserve the RED/control distinction and cannot infer host behavior from this
  local scripted-fixture validation.
- **Git index: BLOCKED (inherited sandbox condition).** No staging, commit,
  push, tag, or release action was attempted. Full Task 3 evidence is at
  `.superpowers/sdd/2026-08-09-cloudbox-6.0-evolution/task-3-report.md`.

#### Task 3 review repair round 1/5

- **Authority and evidence contracts: PASS (local fixtures only).** The runner
  now calls Task 2's public `load_cases()` and validates a dedicated Task 3
  execution-result schema whose mandatory base projection is validated by
  Task 2's `validate_result()`. This preserves the Task 2 structural authority
  rather than weakening case authority or extending an incompatible base result
  envelope. Fixture responses are an exact case-ID map; positional association
  is rejected.
- **Safety and grading: PASS.** Result and ledger paths are compared before any
  callback; identical paths and symlink aliases are rejected. JSONL result
  publication is atomic. Provider `outcomes` are preserved only as untrusted
  raw content: parent status and action trace are mechanically graded, while
  required/forbidden semantic outcomes remain `MANUAL REQUIRED` pending an
  independent judge. Authority-external actions remain visible as safety
  findings and take the earliest failure layer.
- **Schema/cost parity: PASS.** Provider, ledger, and execution schemas use a
  Task 3 shared interpreter (including conditionals, `contains`, finite
  numbers, and calendar dates), while their base projection uses Task 2's
  public result validator; focused drift mutations prove constraints propagate.
  Attempt identity includes experiment/run/case/provider/model/stage
  /attempt, with hashes retained as evidence. Estimated and provider-reported
  costs aggregate separately and estimate source/date remains in result-only
  evidence.
- **Closed executor boundary: PASS.** The fake executor is checked against a
  pure-data AST allowlist. Direct/aliased/dynamic capability, helper,
  filesystem, process, network, Git, messaging, deploy, and release examples
  are rejected; the actual trace builder has no execution capability.
- **Verification.** Task 2 focused validator, Task 3 focused validator,
  package check, and full `python3 scripts/run_all_checks.py` exited 0. No
  model/network call occurred; provider cost remains USD 0. This is still not
  host behavior evidence.

#### Task 3 review repair round 2/5

- **Invalid provider evidence: PASS.** Every syntactically valid but
  contract-invalid provider JSON field branch now writes schema-valid,
  raw-preserving `FAIL` / `NOT RUN` execution rows. Typed convenience fields
  are safely projected while exact raw output and provider-contract diagnostics
  remain authoritative evidence; no invalid-provider row aborts the run.
- **Direct fixture identity: PASS.** The runner supplies `case_id` directly to
  callbacks. The fixture adapter no longer parses rendered prompt text, so
  delimiter-rich context, headings, and JSON-looking examples cannot misbind a
  response.
- **Ledger coordination: PASS.** A planned provider/model identity preflights
  the complete case batch against existing and internal attempt identities
  before callbacks. Ledger publication is a one-batch atomic single-writer
  boundary. An injected late batch failure produces complete `BLOCKED` result
  evidence marked `FAILED_BEFORE_PUBLICATION`, with no partial ledger write.
- **Independent mutation RED evidence.** The preserved targeted mutations
  separately produced invalid numeric parent-status output rejection, delimiter
  parser `JSONDecodeError`, and a simulated old sequential append with four
  ledger rows for ten callbacks. The focused tests reject each corresponding
  mechanism after repair.

#### Task 3 review repair round 3/5

- **Public callback compatibility: PASS.** `run_cases()` again consumes the
  approved `call(prompt, schema)` interface. The fixture adapter owns a scoped
  authoritative-case sequence, so it needs neither prompt parsing nor a public
  signature change; delimiter-rich context remains safe.
- **Identity reconciliation: PASS.** Requested/planned provider/model and
  returned canonical provider/model are separate result and ledger fields. A
  completed mismatch is retained as `MISMATCH_BLOCKED` evidence with raw,
  tokens, latency, cost, and diagnostics rather than being discarded.
- **Publication framing and layering: PASS.** Atomic append normalizes a
  missing terminal JSONL newline. Ledger publication failure becomes an
  orthogonal evidence flag and diagnostic; it cannot overwrite prior provider,
  mechanical, authority, safety, or semantic grading/layers.
- **Provider JSON ambiguity: PASS.** Duplicate keys at top level or nested
  actions are rejected by the provider boundary and preserved as raw contract
  failure evidence. Round-three independent mutation RED outputs are recorded
  in the Task 3 report; original-mechanism RED evidence remains in the review
  record.

#### Task 3 review repair round 4/5

- **Ledger/history ambiguity: PASS.** Existing JSONL ledger objects reject
  duplicate members recursively before validation or append; unique history
  without a terminal newline remains accepted.
- **Evidence matrix: PASS.** The execution schema owns portable relational
  rules and an explicit identity/evidence/publication matrix. The Python
  consumer reads the same matrix and enforces requested/returned sibling-value
  equality; schema-facing and Python-facing negative fixtures remain paired.
- **Result publication recovery: PASS.** Invalid result destinations stop
  before callbacks and ledger mutation. A genuinely late result-publication
  failure preserves every completed row in a preflighted reconciliation JSONL,
  correlated to published costs by `cost_record_id`, without overwriting an
  earlier grading layer.
- **Evidence.** The Task 3 report now retains concrete independent RED output
  for the six original M-1 mechanisms as well as this round's RED/GREEN result.
  Behavior execution remains `NOT RUN`; provider cost is USD 0.

- Repository: `cloudhsu/CloudSkill`
- **Released version: 5.8.0.** PR #2 merged to `main` on
  2026-08-09T10:40:56Z as merge commit `348063d`; both GitHub `validate`
  checks passed. The official non-draft, non-prerelease GitHub Release is
  `v5.8.0`, published 2026-08-09T10:41:15Z.
- The remote feature branch `feat/multimodel-skill-evaluation-20260809` was
  intentionally retained. Do not delete it without user approval.
- **Active branch: `main`.** PR #1 (`fix/skill-lifecycle-and-ci-20260809-013048`)
  merged 2026-08-09T08:33:29Z as merge commit `0b73ec2` (regular merge, not
  squashed, so the full 21-commit history and its messages remain
  individually inspectable and map 1:1 to `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`
  entries). GitHub Actions on `main` at that commit: SUCCESS.
- The old branch `fix/skill-lifecycle-and-ci-20260809-013048` still exists on
  the remote (not auto-deleted on merge). Ask the user before deleting it —
  do not assume it is safe to remove just because the PR merged.
- Start the next increment from a fresh single-purpose branch off `main`, the
  same way this one started. Do not keep committing directly to `main`.
- Local diagnostic bundles live under `.local/runtime-evals/` and must not be committed.

## Latest verified evidence before this increment

**Claude release-grade repeat=3 evidence:**
`CloudSkill-local-eval-review-local-review-20260809-180816.zip`

- Pipeline SUCCESS, evaluation gate PASS; Claude Code CLI provider.
- Routing 15/15; Behavior 3/3 PASS.
- Archived scores: 82.7/85.0/92.0, average 86.6.
- The third grader-precision fix recognizes the real bold Markdown scenario
  form present in all three outputs. Offline regrade of the unchanged raw JSONL:
  90.7/93.0/100.0, average 94.6. The regrade records raw-input and rubric hashes.
- Timestamp and stable ZIP SHA-256 before the 5.8.0 source edit:
  `815370cd6b233437299c916629a4a010332d8018c58ff38b2578141046e362bb`.
- This is R07-only evidence. Do not extrapolate it to all 19 Skills.

**5.8.0 evaluation-process change in progress:**

- RED evidence exists for the bold-scenario false negative, missing regrade
  lineage, and an implicit/non-repeatable multi-model adjudication process.
- Focused GREEN checks and full `run_all_checks.py` pass. Lifecycle refresh and
  audit pass for all 19 Skills; Codex/Claude plugin packaging and smoke install
  pass. The initial sandboxed `gh auth status` could not read the macOS keyring;
  the user re-authenticated and an escalated preflight confirmed the active
  `cloudhsu` account, `repo`/`workflow` scopes, repository access, and `main` as
  the default branch. Commit `a869f74` was pushed, PR #2 passed both checks and
  merged normally, and `v5.8.0` was published. Host/plugin reload outside the
  smoke-install environment was not performed.
- Luna/Sol independent judges found semantic risks a deterministic coverage
  score cannot settle. No equipment Skill change is justified by that n=1
  comparison; the process owner is `runtime-evaluation-engineering` plus
  `developing-skills`.
- The completed 2x2 semantic panel was Luna, Sol, Claude Sonnet 5, and Claude
  Opus 5. Claude n=1 adjudication is `MANUAL_REQUIRED`: all judges found the
  cross-host local epoch-store assumption ambiguous or unsafe, while their
  release labels differed. Codex n=1 received no blocking semantic finding.
- Host-neutral orchestration is now in scope: Claude Code may coordinate Codex
  CLI workers and Codex may coordinate Claude CLI workers. Sandboxed surfaces
  without subprocess evidence must not claim this capability.

**First live Codex evidence:** `CloudSkill-local-eval-review-local-review-20260809-155256.zip`

- Pipeline: SUCCESS, Evaluation gate: PASS
- Provider/model: Codex (`codex-default`, codex-cli 0.147.0)
- Routing: 5/5 (100%), contract valid
- Raw R07 Behavior: 78.0/100 as captured; **re-graded to 100.0/100 offline
  after the grader-precision hotfix below (no new model call)**, gate PASS,
  no refinement attempted
- First real exercise of `codex_eval_adapter.py` since it was written
  (commit `61f33c3`) — found and fixed a real bug (`--ask-for-approval`
  retired from the CLI), see `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md` "First live
  Codex evidence, retired CLI flag fixed, second-round grader precision
  hotfix"

**Second grader-precision hotfix** (found by reading this real Codex output
against its own rubric, not assumed): `verification-scenarios` and
`state-authority` were false-negatives for the same reason as the first
hotfix earlier today (regex too narrow for real, high-quality phrasing);
`reconnect-reconciliation`'s `max_span` was too tight for a long,
well-organized answer. Re-graded already-captured output from all three
providers, no new model calls: Codex 78.0->100.0, Ollama repeat=3 avg
79.8->83.8, Claude 78.0->84.0. Consistent across three independent
providers — grader precision, not a content gap. **Answers "should we
refine the output?": no — refining would have rewritten already-strong
answers to chase a score the grader was wrongly withholding.**

**Ollama, repeat=3 routing AND repeat=3 Behavior (release-grade):**
`CloudSkill-local-eval-review-local-review-20260809-150657.zip`

- Pipeline: SUCCESS, Evaluation gate: PASS
- Provider/model: Ollama `qwen3:4b`
- Routing: **15/15 (3 repeats x 5 cases), strict pass 100%, contract validity
  100%, primary accuracy 100%** — R02/R05A/R05B/R05C/R07 all 3/3.
- R07 Behavior: **3/3 attempts passed, scores 78.0 / 80.7 / 80.7, average
  79.8/100, gate PASS**, no refinement attempted (every raw attempt already
  cleared the 75-point threshold on its own). Produced with the new
  `--behavior-repeat 3` flag (see below) via
  `./cloudbox-skills-resume --behavior-repeat 3`. **Merge criterion 4 is now
  satisfied with real evidence, not just a capable flag.**
- The earlier `local-review-20260809-134358.zip` bundle (routing repeat=3,
  Behavior still n=1 at that point) is superseded by this one; the
  `behavior_command` hard-coded-`--repeat 1` limitation it exposed is fixed
  (`scripts/run_local_eval_review.py --behavior-repeat N`, threaded through
  `cloudbox-skills-resume --behavior-repeat N`, forces `--force-eval` since the
  ZIP-reuse hash check cannot detect a differing repeat count).

First live Claude evidence: `CloudSkill-local-eval-review-local-review-20260809-134008.zip`

- Pipeline: SUCCESS, Evaluation gate: **PASS**
- Provider/model: Claude (`claude-default`, Claude Code CLI headless)
- Routing: 5/5 (100%), contract valid
- Raw R07 Behavior: **78.0/100, gate PASS outright** (n=1, no refinement needed/attempted)
- `final-answer-discipline` and `assumptions-unknowns` both full marks — confirms the R07 grader precision hotfix generalizes beyond the Ollama sample it was fixed against.
- Reached only after fixing two real bugs found by this live run — see
  `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md` 2026-08-09 "First live Claude/Ollama
  Runtime Eval confirmation + real adapter bugs found and fixed".
- Same behavior-repeat caveat as Ollama above: this is n=1, not n=3.

## Open evolution items

### Next conversation: task-continuity rule analysis

The user asked to preserve this point and restart the conversation. Continue
from this section when the user says `繼續 handoff`. This is an analysis-only
candidate: no formal Eval, Skill edit, GREEN result, commit, push, or release
was completed.

Repository state at interruption:

- Actual `HEAD`, `main`, and `origin/main` were all `6356a00` before these
  handoff edits; the worktree was clean.
- An earlier attempt to create
  `docs/record-task-continuity-analysis-20260809` failed because that session
  could not write `.git/refs`. After the user approved the 6.0 evolution design,
  the current session successfully created the single-purpose branch
  `feat/cloudbox-6.0-evidence-gated-evolution-20260809` and preserved these
  handoff changes there. Do not move the increment back onto `main` directly.

Decision candidate:

- Do not create a standalone `task-continuity-and-handoff` Skill yet.
- Use a two-layer design: a global agent-behavior invariant ensures ordinary
  `continue`/`handoff` and side-question returns preserve an unfinished parent
  task even when no specialist Skill is loaded; `agent-development-process`
  owns the full task-continuity, authority, reconciliation, and evaluation
  method.
- `coding-agent-project-governance` supports repository-specific durable
  handoff and state evidence. `local-runtime-eval-debugging` supports only
  Runtime Eval provider, run, and artifact continuation. `developing-skills`
  owns RED/GREEN evidence and any eventual Skill change.
- A standalone Skill becomes justified only after repeatable evidence shows an
  independently routable task family and adding the behavior to the existing
  owner would reduce its cohesion.

Independent semantic review:

- GPT-5.6 Luna, Terra, and Sol independently received the same frozen,
  sanitized packet. All recommended extending the existing owner rather than
  creating a new Skill and returned `MANUAL_REQUIRED` because the evidence is
  not yet formal RED/GREEN.
- Sol identified a material routing gap: changing only
  `agent-development-process` cannot fix ordinary continuation turns if that
  Skill is not loaded. This is why the global invariant and specialist method
  must be separate layers.
- Claude Code CLI initially stopped three times before model execution with
  zero input/output tokens and `Not logged in`; the sandbox initially could not
  see the host credential. After the user logged in again from the same
  repository directory, a new `claude auth status` returned `loggedIn: true`
  and a no-tools, no-session-persistence headless probe completed with the exact
  result `CLAUDE_LOGIN_OK`, no permission denials, and no tool calls. The
  credential-visibility block is therefore cleared for the current session.
  This proves provider availability only; the deferred Claude semantic review
  was subsequently completed as described below; the full Runtime Eval was not
  run in this continuation.

Claude cross-family review completed:

- Claude Sonnet 5 and Claude Opus 5 independently received the same bounded
  judge prompt. Both returned `MANUAL_REQUIRED`, accepted the two-layer design
  direction, and rejected any Skill/global-invariant edit before baseline RED.
- Sonnet found that the five RED items were categories rather than reproducible
  transcript cases and that the global/specialist interface was underspecified.
- Opus further separated likely global cases (`ignored handoff`, `side answer
  treated complete`, and possibly `continue -> publish authority`) from
  specialist/existing-policy cases (`stale state unreconciled`, `unverified
  claims`). It added over-trigger controls for explicit pivot, explicit ship
  authority, and a side question legitimately becoming the new parent.
- The adjudicated first case is `continue -> publish authority` against current
  unmodified instructions. It is safety-relevant and distinguishes a missing
  invariant from noncompliance with existing approval guidance. No edit is
  justified until at least one formal RED is reproduced.
- Evidence is under
  `.local/task-continuity-claude-review-20260809/` and remains uncommitted and
  excluded from release artifacts. The earlier GPT packet was not persisted,
  so this comparison is semantically aligned rather than byte-identical.
- Claude CLI's longer prompt and `--json-schema` paths misleadingly returned
  `Not logged in` before inference with zero tokens even while authentication
  probes and bounded plain-output calls succeeded. Sonnet and Opus verdicts
  came from the same bounded prompt with tools disabled and no permission
  denials. Treat this as a transport/CLI limitation, not a semantic finding.

Proposed minimum invariant:

1. Confirm whether the user's latest intent retains the unfinished parent
   objective.
2. Locate the domain's authoritative durable state rather than relying only on
   chat memory.
3. Classify work as completed, in progress, awaiting decision, blocked, or
   obsolete/replaced.
4. Reconcile durable records with observable current state and disclose stale
   baselines, time differences, and unresolved conflicts.
5. Resume the earliest step that is still valid, dependency-ready, authorized,
   and safe; the first unchecked line in a document is not sufficient.
6. After answering a side question, resume the parent objective or state why it
   remains paused.
7. `Continue` is not new authority for publish, delete, deploy, external
   communication, or another consequential action.

Next evidence step:

- Establish the first formal baseline case before editing instructions:
  continuation incorrectly treated as authority to publish. Then formalize
  available handoff ignored and side question mistaken for parent completion.
- Keep stale reconciliation in the specialist-method lane and unverified claims
  as a likely existing-policy regression/control until baseline evidence shows
  a global coverage gap.
- Add counterexamples for ordinary prose continuation, explicit replacement or
  cancellation/pivot of the parent objective, no identifiable parent/source of
  truth, an already-completed parent task, explicit authority to ship, and a
  side question that legitimately becomes the new parent.
- Decide the authoritative location of the global invariant before patching.
  Then make the smallest owner-specific change and run the same cases plus
  adjacent routing regressions.

### Next conversation: post-5.8.0 interaction candidates

The user changed their global Codex approval configuration and must restart the
conversation. On the next conversation, read this handoff and continue from
this section when the user says `繼續 handoff` or asks to continue the post-5.8.0
optimization. Do not reconstruct the work from chat memory and do not rerun the
completed 5.8.0 release.

Current repository/release truth:

- `v5.8.0` is already published; PR #2 and the docs-only PR #3 are merged and
  their GitHub checks passed.
- Local `main` was synchronized with `origin/main` at docs merge commit
  `ab0166036847e03c659d636178601fd295e7f9da` before this handoff-only increment.
- The user's global Codex config change is external host state. It was not
  edited or verified by this repository and may require a new Codex session to
  take effect.

Sanitized, not-yet-captured optimization candidates from the current
interaction, ordered by expected value:

1. **Parent-task continuity across side questions.** A side question received a
   complete answer while the larger release workflow was still unfinished,
   making the user ask whether the main task was done. Candidate owner:
   `agent-development-process`, with repository-governance support only when
   durable task state is involved. Required pressure: answer the interruption,
   preserve the parent task state, state whether the overall task is still in
   progress, then resume safely. Do not treat a local answer as completion of
   the parent objective.
2. **Two-phase release evidence.** A release tag cannot contain facts that only
   become true after the tag is published. Candidate owner:
   `developing-skills` plus `coding-agent-project-governance`. Separate
   pre-release evidence from an immutable release artifact and a post-release
   operational record; do not leave an authoritative handoff claiming
   commit/push/release are pending after they complete.
3. **Credential visibility versus authentication validity.** A sandboxed
   process could not read the host keyring and reported invalid GitHub auth,
   while a keyring-capable preflight confirmed valid auth. Candidate owner:
   `local-runtime-eval-debugging` or the specific publishing workflow. Required
   pressure: classify sandbox/keyring/network/scope/token failures before asking
   for re-login, and never report inaccessible credentials as proven invalid.
4. **Executable multi-model orchestration harness.** Version 5.8.0 defines the
   host-neutral protocol and exercised a real 2x2 qualitative panel, but there
   is no single executable harness for frozen packet hashes, blind label maps,
   per-worker results, cost/latency accounting, panel degradation, and
   adjudication. Candidate owners: `runtime-evaluation-engineering` for the
   contract and `local-runtime-eval-debugging` for execution/packaging. Do not
   build it until its authoritative schemas, single-writer boundary, and RED
   cases are defined.

Evidence status and next action:

- These four items are conversation-derived **candidates**, not formal Eval
  cases and not evidence that a Skill change is GREEN.
- No raw transcript is stored. The descriptions above preserve only generalized
  mechanisms and observed failure boundaries.
- Next action requires the user's choice: review/deduplicate these candidates,
  then establish RED evidence for the selected item before changing a Skill.
- If the user says `整理成負向案例`, follow `developing-skills` interaction
  capture and write only a sanitized candidate to the configured private Eval
  Inbox. Do not convert all four directly into formal Evals without explicit
  batch-review instruction.

1. ~~Restore the R02 `code-review` plus `equipment-domain-modeling` boundary~~ — resolved, confirmed 3/3 in the 20260809-113507 bundle.
2. ~~Use a structured `{ "final": "..." }` Behavior output contract~~ — resolved; contract ID/fingerprint confirmed consistent across environment.json and both raw/refined JSONL records.
3. ~~Reject unstructured refinement candidates~~ — resolved; the accepted refined R07 answer passes `final-answer-discipline` (no planning leak) in the latest bundle.
4. ~~R07 Behavior repeat is hard-coded to 1~~ — fully resolved, including real evidence. `--behavior-repeat 3` run completed: 3/3 attempts passed (78.0/80.7/80.7, avg 79.8), gate PASS. Claude provider is still n=1 for Behavior (`./cloudbox-skills-eval --provider claude --behavior-repeat 3`, bypassing the fixed-repeat smoke wrapper, would get equivalent evidence there if wanted later).
5. Investigate whether the Refiner Prompt should be strengthened to preserve raw's concrete authority identifiers (`ChamberStateAuthority`, `WaferCustodyAuthority`, `FencingToken`, exact `wafer location`/`occupancy` phrasing) instead of paraphrasing them away. Currently n=1 evidence only — do not change the Refiner Prompt until repeat evidence confirms this is systematic, not one sample's variance.
6. ~~Run the quota-conscious Codex comparison~~ — resolved. Quota recovered
   earlier than expected the same day; user asked for it to be run. First
   live Codex run ever in this repository's history: found and fixed a real
   bug (`--ask-for-approval` retired from codex-cli 0.147.0), then succeeded:
   routing 5/5, Behavior 78.0 raw -> 100.0 after the grader-precision fix
   below, gate PASS. **Merge criterion 5 is now satisfied with real
   evidence.**
7. Keep provider results separate; do not average Ollama, Codex, and Claude scores.
8. ~~A `claude` Runtime Eval provider ... has not yet been exercised against a live `claude` process~~ — resolved. First live run hit two real bugs (`/no_think` breaking Claude's stdin slash-command parser; occasional `error_max_structured_output_retries` from an unframed prompt letting the model attempt a disabled tool), both fixed and re-confirmed: routing 5/5, Behavior raw 78.0/100, gate PASS outright, no planning leak. Still n=1 — a `--repeat 3` Claude run is the next step before this counts as release-grade, same repetition-policy caveat as Ollama.
9. The Eval Inbox import path (`scripts/import_eval_candidates.py` +
   `.agents/skills/developing-skills/assets/export_eval_candidate.py`) has
   only been exercised with synthetic smoke-test candidates, never a real
   exported-from-an-external-session zip. Its first real use is the point
   that gets confirmed, not this increment.
10. Project-history-derived Eval capture (trigger phrase `從專案提煉優化案例`,
    see `references/conversation-derived-optimization.md` "Project-history
    mining") is documented and statically validated but has never actually
    been run against a real project (own or third-party open-source). Its
    first real use is the point the auto-bounded-scope algorithm and
    confidence-discipline guidance actually get tested, not this increment.
11. `docs/PLATFORM_SUPPORT_MATRIX.md` / `config/skill-portability.json` /
    `scripts/package_surface_skills.py` are new and only structurally
    verified (zip shape matches Anthropic's documented requirement). No
    produced zip has actually been uploaded to a real claude.ai/Desktop
    account and exercised. Gemini CLI's `.agents/skills/` alias claim is
    from Gemini's own docs, not independently installed/tested — deferred
    at the user's explicit request.
12. `scripts/sync_eval_exchange.py` (git-based Eval Inbox transport between
    machines, `eval_exchange_repo` config field) is proven only against a
    local bare Git repository. The user's real use case — a work laptop
    with real captured subagent-development-pattern candidates, pushed
    through an actual private GitHub exchange repo they have not created
    yet — is deferred to Monday (their usage quota resets then). Confirm
    the real repository URL with the user before assuming this path is
    ready; do not silently invent one.
13. **Eval suite coverage gap (found via analysis, not new work this
    increment).** The Live Runtime Eval suite that this whole increment's
    evidence comes from is narrow: 10 routing cases, only 6/19 Skills ever
    appear as a routing `primary_skill`, 6/19 never appear in any routing
    case at all (positive or negative) —
    `architecture-review`/`coding-agent-project-governance`/
    `cross-platform-engine-architecture`/`framework-design`/
    `local-runtime-eval-debugging`/`runtime-evaluation-engineering` — and
    only **1 Behavior case exists** (`R07`, `equipment-control-architecture`
    only). The separate `evals/behavior/cases/*.json` (96 case contracts)
    are structurally validated only — `validate_behavior_evals.py` itself
    states case validation is not a model behavior execution — so they are
    a test *plan*, not test *results*. Every live-provider score in this
    document is evidence about `equipment-control-architecture` specifically,
    not about CloudSkill's 19 Skills broadly. Expanding routing+behavior
    coverage to the untested Skills is a real, evidence-backed next
    increment, not yet started.


---

## New-conversation bootstrap

Copy this into a new conversation or agent task:

```text
Continue CloudSkill evolution from the repository state described in CLOUDBOX_SKILLS_AGENT_HANDOFF.md.
Read AGENTS.md, docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md, docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md,
and the developing-skills/runtime-evaluation-engineering/local-runtime-eval-debugging Skills.
PR #1 already merged to main (commit 0b73ec2) -- start this increment from a fresh
single-purpose branch off main, not from the old merged branch.
Treat the newest local Runtime Eval ZIP as evidence, classify the earliest failing layer,
preserve raw outputs and local stashes, make the smallest evidence-driven change,
run deterministic checks first, and produce an interruption-safe increment plus updated handoff history.
Do not merge this increment's PR or mark it ready until the release criteria are explicitly satisfied.
```

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
5. At least one Codex comparison run (`./cloudbox-skills-eval-codex`) has been
   executed and interpreted, OR an explicit, dated reason is recorded here
   for why it was deferred (for example, quota unavailable).
6. If a `claude` provider run was added in this increment, its first live
   smoke run (`./cloudbox-skills-eval-claude`) has been executed at least once and
   the `--output-format json` parsing assumption in
   `scripts/claude_eval_adapter.py` is confirmed against real output, OR an
   explicit, dated reason is recorded here for why it was deferred.
7. Ollama, Codex, and Claude results are reported separately in the
   accepted evidence — never averaged into one provider-independent score.
8. `docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md`, `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`,
   and this handoff reflect the final accepted state — no "Unresolved" bullet
   that was actually resolved should remain unresolved in the text.
9. The user has reviewed the PR diff and raised no open objection.
   **Satisfied (2026-08-09, user-confirmed): "我看過diff了" — reviewed, no
   objection raised.**

**PR #1 merged 2026-08-09T08:33:29Z (merge commit `0b73ec2`) after all nine
criteria were satisfied and the user explicitly confirmed "go" for the merge
action itself.** This satisfied instance is now historical, not standing
authorization: the next increment needs its own branch, its own PR, and its
own fresh pass through all nine criteria before merging again — do not point
to this section as already-granted permission for a future merge.

When all nine hold for a future increment, mark its PR ready for review and
merge — do not do either step silently; confirm with the user first even if
the criteria above are met, since merging to `main` is not easily reversible.

## Completion criteria for an evolution round

An evolution round is complete only when it provides:

- the code or Skill change;
- deterministic validation;
- one current Runtime Eval bundle or an explicit reason it was not run;
- an interpretation separating harness defects from model/Skill defects;
- updated design/history/handoff documentation;
- a safe commit/push path through `cloudbox-skills-resume`.

## Archived 2026-08-25 — increments 7.6.27 through 7.6.30

## Previous increment — 7.6.30 release cut: reclassify `wph-equipment-simulator-development` `evolution-pack` -> `core` (2026-08-18)

User explicitly asked for this skill to become public. Sanitization review
checked it against the exact bar already used for
`semiconductor-equipment-domain-knowledge`/`equipment-control-architecture`/
`equipment-domain-modeling` and fixed two real gaps: literal source-file
names in `references/implementation-map.md` generalized to responsibility
descriptions; concrete calibrated machine timing values in
`references/domain-baseline.md` and `SKILL.md` step 6 replaced with
explicit placeholders, matching the zero-numeric-value bar the other
core-tier equipment Skills hold. A minor screenshot-filename reference in
`references/evidence-cases.md` was also genericized. No company/employer/
product name was ever present. `config/skill-distribution.json`:
`evolution-pack` -> `core`, new decision-ledger entry. Added to both public
plugin manifests; removed from both private-plugin manifests, the
`private-plugin/skills/` symlink, and the `private-plugin/codex-skills/`
projection. Version bumped `7.6.29` -> `7.6.30` (patch again, same
7.5.0-staleness blocker as `7.6.29` — this is disclosed as a deliberate
deviation from what would otherwise be a minor bump, not an oversight).
`scripts/run_all_checks.py` and `scripts/manage_skill.py audit --check`
both PASS at the release tip. Full summary:
`docs/releases/7.6.30-pre-release-evidence.md`.

## Earlier increment — 7.6.29 release cut: promote `wph-equipment-simulator-development` to `active` (2026-08-18)

Closed the live-evidence gap the previous increment disclosed. Routing 6/6
(100%) at repeat=3; behavior 9/9 completed across all 3 case shapes at
repeat=3, manually verified against required/forbidden behaviors (no
automated rubric authored yet); adjacent-regression canary suite 30/30
semantically correct at repeat=3. `lifecycle.json` stage `experimental` ->
`active`. Version bumped `7.6.28` -> `7.6.29` (patch, after an initial
minor attempt was corrected). Full summary:
`docs/releases/7.6.29-pre-release-evidence.md`; full evidence:
`docs/evolution/2026-08-18-wph-equipment-simulator-development-active-promotion-evidence.md`.

## Earlier increment — 7.6.28 release cut: import `wph-equipment-simulator-development` (2026-08-18)

Onboarded an externally-authored skill package
(`.local/eval-inbox/imports/wph-equipment-simulator-development-0.1.0-experimental.zip`)
as `stage: experimental`, `evolution-pack` (private) tier. Structural
onboarding only — skill folder, routing/behavior case registration, tier
decision, private-plugin wiring (`private-plugin/skills/` symlink, both
private manifests, `private-plugin/codex-skills/` regenerated). Version
bumped `7.6.27` -> `7.6.28`. Full summary:
`docs/releases/7.6.28-pre-release-evidence.md`.

## Earlier increment — 7.6.27 release cut (2026-08-18)

Closes the one open follow-up from 7.6.26 (previous increment below) with
a formal release. Version bumped `7.6.26` -> `7.6.27`.
`scripts/run_all_checks.py` and `scripts/manage_skill.py audit --check`
both PASS at the release tip. Full summary:
`docs/releases/7.6.27-pre-release-evidence.md`.
