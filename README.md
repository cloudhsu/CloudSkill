# CloudSkill

**Current version: 5.0.0**

CloudSkill is a portable set of software/system architecture skills and operating guidance for **OpenAI Codex** and **Claude Code**.

The same canonical `SKILL.md` directories are used for both tools. Codex installs them under `.agents/skills`; Claude Code installs them under `.claude/skills`.

## Install

See [INSTALL.md](INSTALL.md) for user-level and project-level installation on Windows, macOS, and Linux.

## Skills

| Skill | Primary use |
|---|---|
| `architecture-review` | Reconstruct and compare architecture decisions |
| `application-client-server-architecture` | Frontend/backend, API, RBAC, transactions, data, UI, deployment |
| `cross-platform-native-architecture` | Qt/native platforms, OS integration, ABI, hardware, packaging |
| `cross-platform-engine-architecture` | Director/scene, update/render, graphics, resources, platform adapters |
| `framework-design` | Frameworks, SDKs, plug-ins, product-line architecture |
| `safe-incremental-refactoring` | Brownfield modernization and compatibility-preserving decomposition |
| `code-review` | Correctness, concurrency, persistence, communication, recovery |
| `document-governance` | Controlled and traceable engineering documents |
| `software-quality-iso25010` | Quality scenarios, metrics, evidence, release gates |
| `development-process-tailoring` | Waterfall, iterative, Agile, XP, and hybrid process |
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
├── evals/                   # Skill-routing cases
├── scripts/                 # Install, validation, and documentation audit
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
python scripts/validate_pack.py
python scripts/audit_docs.py
```
