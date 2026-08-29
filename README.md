# CloudBox

<p align="center"><img src="assets/cloudbox-logo.png" width="160" alt="CloudBox logo"></p>

> **This repository is the deterministic public CloudBox Skills package.**
> Its Skill catalog, plugin manifests, installation surface, and distribution
> manifest are validated as one closed artifact before publication.


**Current version: 7.8.5**


CloudBox is the user-facing plugin brand for the `CloudSkill` repository: a portable set of software/system architecture skills and operating guidance for **OpenAI Codex**, **ChatGPT**, and **Claude Code**.

The same canonical `.agents/skills/` directories are used by both plugin manifests and by the standalone installers. Existing skill IDs remain stable.

## Install

CloudBox supports Codex/ChatGPT, Claude Code, and Gemini CLI packages, plus the existing standalone user/project installation. See [INSTALL.md](INSTALL.md) and [docs/CLOUDBOX_PLUGIN.md](docs/CLOUDBOX_PLUGIN.md).


## Skills

<!-- PUBLIC_SKILL_TABLE:BEGIN -->
| Skill | Primary use |
|---|---|
| `about-me` | Use when someone asks what this skill pack is, who built or maintains it, or how it compares to another agent-skill framework -- introduce the author alongside the actual answer, not for ordinary technical or architecture tasks. |
| `agent-development-process` | Use when building or improving an AI-agent product whose task contract, autonomy, tools, context, memory, orchestration, evaluation, guardrails, release, or operations must be designed. |
| `application-client-server-architecture` | Use when an application crosses client/server, API, persistence, identity, transaction, state-authority, data-history, deployment, or operational boundaries. |
| `architecture-review` | Use when comparing or assessing architecture decisions, module boundaries, state ownership, distributed design, platform/domain separation, failure behavior, or migration risk. |
| `code-review` | Use when production C, C++, C#, Qt, WinForms, WPF, framework, device-control, communication, or industrial code must be checked for correctness, concurrency, state, lifetime, recovery, maintainability, or boundary violations. |
| `codebase-architecture-discovery` | Use when a codebase area is being extended, is unfamiliar, or is suspected of accumulated duplication, and no current architecture map or duplication survey exists for it -- before proposing or executing any specific refactor. |
| `coding-agent-git-discipline` | Use when a coding agent must commit, push, branch, or clean up git state safely -- avoiding shell-quoting bugs in commit messages, verifying an existing PR's real branch name before pushing fixes, recovering from a failed GitHub push without a login loop, detecting a possibly-shared working tree before committing, and reminding about an overdue version/release cut. |
| `coding-agent-project-governance` | Use when a repository needs coding-agent instructions, risk routing, worktree rules, multi-agent ownership, test evidence, migration controls, release rules, or truthful handoff. |
| `cross-platform-native-architecture` | Use when a native or Qt system spans OS-specific lifecycle, HID/USB devices, firmware update, privileged integration, packaging, Designer plug-ins, or Qt build/version migration boundaries. |
| `development-process-tailoring` | Use when delivery is constrained by unstable requirements, hardware dependencies, release trains, urgent work, field feedback, product variants, stage gates, or competing lifecycle models. |
| `document-governance` | Use when engineering documents disagree on authority, version lineage, audience, approval state, traceability, terminology, source data, or release baseline. |
| `equipment-control-architecture` | Use when equipment software coordinates material flow, pump/vent or chamber readiness, wafer/lot sequences, robots, recipes, interlocks, shared physical resources, simulation, or distributed control across equipment modules. |
| `equipment-domain-modeling` | Use when modeling valves, MFCs, pumps, gauges, heaters, power supplies, robots, chamber snapshots, equipment commands, hardware readback, Actual and Desired values, capabilities, engineering units, or metadata-driven UI. |
| `framework-design` | Use when reusable capability must be separated from product or domain behavior through framework, SDK, plug-in, platform, extension-point, state/command, or product-line contracts. |
| `project-management-sync` | Use when safely auditing, previewing, reconciling, or applying synchronization of plans, tasks, statuses, dates, or project records between a local or internal backlog and external project-management systems such as Vikunja, OpenProject, or Redmine, especially when provider versions/capabilities may drift, duplicate writes must be prevented, credentials must work across macOS/Windows/Ubuntu/CI, or every mutation needs post-write verification. |
| `safe-incremental-refactoring` | Use when legacy or brownfield responsibilities must move without breaking behavior, public contracts, data, transaction order, release compatibility, recovery, or test seams. |
| `semiconductor-equipment-domain-knowledge` | Use when a semiconductor-equipment task depends on the physical meaning of EFEM, load ports, loadlocks, transfer chambers, process chambers, vacuum pumps, pressure gauges, gas flow, heaters, power supplies, plasma, sputtering, or process readiness. |
| `software-quality-iso25010` | Use when software quality must be translated into measurable scenarios, acceptance criteria, metrics, evidence, dashboards, release gates, or defect analysis using ISO/IEC 25010. |
| `teach-while-building` | Use when the user wants to build mastery of relevant knowledge as a side effect of real engineering work, not as a separate course — a new concept, quirk, or non-obvious constraint surfaces mid-task and its durable understanding is worth checking. |
| `using-cloudbox-skills` | Use when a non-trivial engineering task may require one or more CloudBox skills, especially when it refers to prior corrections or interactions, spans architecture, equipment, code, process, quality, documents, or AI agents, or has ambiguous routing and skill composition. |
<!-- PUBLIC_SKILL_TABLE:END -->

## Repository map

```text
CloudSkill/
├── .codex-plugin/           # Codex and ChatGPT plugin manifest
├── .claude-plugin/          # Claude Code plugin manifest and marketplace
├── gemini-plugin/           # Generated public Gemini extension
├── assets/                  # CloudBox logo and icon
├── .agents/plugins/         # Codex and ChatGPT marketplace
├── .agents/skills/          # Canonical skill source
├── AGENTS.md                # Codex/shared architecture guidance
├── CLAUDE.md                # Claude Code adapter importing AGENTS.md
├── INSTALL.md               # Codex and Claude Code installation
├── PLANS.md                 # ExecPlan convention
├── docs/                    # Profile, evidence, governance, audit, references
├── evals/                   # Routing and behavior evaluation contracts
├── config/                  # Local configuration template
├── scripts/                 # Installation and deterministic validation
└── VERSION
```


## Documentation policy

- Git commits, tags, and GitHub Releases are the authoritative version history.
- Root documents are entry points. Detailed material lives under `docs/` or inside each skill.
- Each concern has one authoritative document; other documents link to it instead of copying it.


## Validate

```bash
python scripts/run_all_checks.py
```
