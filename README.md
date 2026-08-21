# CloudBox

<p align="center"><img src="assets/cloudbox-logo.png" width="160" alt="CloudBox logo"></p>

> **This public repository is exported from the private `cloudbox-skills`
> repository via `scripts/export_public_bundle.py`, which reads
> `config/skill-distribution.json` to include only `core`-tier content.**
> Every other tier is private (skill self-development/conversation-mining
> tooling, and unsanitized product-derived skills split by domain: game,
> operations/marketing, art) and never exported here. This is a temporary
> arrangement; the split back to a private-only, public-partial-mirror model
> resumes once the planned CrewAI migration work begins.

**Current version: 7.6.35**

CloudBox 6.4 adds pre-qualified, deterministic lifecycle templates while
retaining risk-based Review Assurance and resumable adaptive planning. See
`docs/LIFECYCLE_TEMPLATE_CATALOG.md`, `docs/REVIEW_ASSURANCE_LEVELS.md`, and
`docs/RESUMABLE_LIFECYCLE_ORCHESTRATION.md`. A later-version discussion for
controlled CLI/MCP integration is recorded in
`docs/future/CONTROLLED_EXTERNAL_TOOL_ADAPTERS.md`.
The approved later split between the public development package and a locally
installable private evolution package is recorded in
`docs/future/PUBLIC_PRIVATE_PACKAGE_SPLIT.md`.

CloudBox is the user-facing plugin brand for the `CloudSkill` repository: a portable set of software/system architecture skills and operating guidance for **OpenAI Codex**, **ChatGPT**, and **Claude Code**.

The same canonical `.agents/skills/` directories are used by both plugin manifests and by the standalone installers. Existing skill IDs remain stable.

## Install

CloudBox supports Codex/ChatGPT, Claude Code, and Gemini CLI packages, plus the existing standalone user/project installation. See [INSTALL.md](INSTALL.md) and [docs/CLOUDBOX_PLUGIN.md](docs/CLOUDBOX_PLUGIN.md).


## Skills

| Skill | Primary use |
|---|---|
| `using-cloudbox-skills` | Select and order the smallest sufficient skill set |
| `developing-skills` | Develop and release skills with routing and behavior evidence |
| `architecture-review` | Reconstruct and compare architecture decisions |
| `semiconductor-equipment-domain-knowledge` | EFEM/material flow, component purpose, vacuum, PVD, process readiness, and physical-to-software interpretation |
| `equipment-control-architecture` | Sequence/service, material flow, readiness, shared resources, interlocks, distributed IPC, config-driven equipment platforms |
| `equipment-domain-modeling` | Equipment component state/command, units/quality, Actual/Desired, capabilities, snapshots, catalogs, metadata-driven UI |
| `application-client-server-architecture` | Frontend/backend, API, RBAC, transactions, data, UI, deployment |
| `cross-platform-native-architecture` | Qt/native platforms, touch/device utilities, HID/USB, OS integration, firmware, packaging, legacy modernization |
| `cross-platform-engine-architecture` | Director/scene, update/render, graphics, resources, platform adapters |
| `framework-design` | Frameworks, SDKs, plug-ins, product-line architecture |
| `safe-incremental-refactoring` | Brownfield modernization and compatibility-preserving decomposition |
| `code-review` | Correctness, concurrency, persistence, communication, recovery |
| `document-governance` | Controlled documents, evolving specifications, baselines, traceability, release evidence |
| `software-quality-iso25010` | Quality scenarios, metrics, evidence, release gates |
| `development-process-tailoring` | Lifecycle tailoring, product evolution, release trains, customer/field feedback, project controls |
| `coding-agent-project-governance` | Repository instructions, risk routing, subagents, tests, release |
| `agent-development-process` | Building an AI-agent product or agentic system |
| `project-management-sync` | Version-aware, idempotent synchronization with external project-management systems |

## Repository map

```text
CloudSkill/
├── .codex-plugin/           # Codex and ChatGPT plugin manifest
├── .claude-plugin/          # Claude Code plugin manifest and marketplace
├── gemini-plugin/           # Generated public Gemini extension
├── private-gemini-plugin/   # Generated private Gemini extension
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
├── scripts/                 # Install, capture, validation, and documentation audit
├── CHANGELOG.md
└── VERSION
```

## Documentation policy

- Git commits and annotated tags are the authoritative version history.
- `history/` contains only a release index; it does not duplicate full source snapshots.
- Root documents are entry points. Detailed material lives under `docs/` or inside each skill.
- Each concern has one authoritative document; other documents link to it instead of copying it.

See [docs/README.md](docs/README.md) for the document ownership map.

## Evolution and handoff

- [Design purpose and flow](docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md)
- [Development map and roadmap](docs/CLOUDBOX_SKILLS_DEVELOPMENT_MAP.md)
- [Evolution change history](docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md)
- [Current agent/conversation handoff](CLOUDBOX_SKILLS_AGENT_HANDOFF.md)

Start with the handoff document when continuing an existing multi-session Skill evolution task.

## Validate

```bash
python scripts/run_all_checks.py
```
