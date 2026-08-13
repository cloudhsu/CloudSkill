# Changelog

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
