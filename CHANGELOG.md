# Changelog

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
