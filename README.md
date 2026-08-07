# CloudSkill

**Current version: 5.5.1**

CloudSkill is a portable set of software/system architecture skills and operating guidance for **OpenAI Codex** and **Claude Code**.

The same canonical `SKILL.md` directories are used for both tools. Codex installs them under `.agents/skills`; Claude Code installs them under `.claude/skills`.

## Install

See [INSTALL.md](INSTALL.md) for user-level and project-level installation on Windows, macOS, and Linux.


## Interaction-derived Eval capture

A local CloudSkill clone can be registered during installation. The installer stores only local paths and safe defaults; it does not store credentials. After configuration, the phrases `整理成正向案例` and `整理成負向案例` create sanitized candidates under the private Eval Inbox. Candidates do not modify formal Evals, skills, commits, or remote branches until a separate review/import task is explicitly requested.

## Skills

| Skill | Primary use |
|---|---|
| `using-cloudskill` | Select and order the smallest sufficient skill set |
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

## Repository map

```text
CloudSkill/
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

## Validate

```bash
python scripts/run_all_checks.py
```
