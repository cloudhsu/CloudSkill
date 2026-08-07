# Software Architect Codex Pack

Version: **4.0.0**

This pack encodes a source-grounded software/system architect operating model.

## What changed in v4

Version 4 uses two concrete implementation sources:

1. The supplied complete lunch-ordering system repository.
2. The public historical CloudBox cross-platform engine repository.

The pack now separates:

- Full-stack/Client-Server architecture.
- General cross-platform native architecture.
- Cross-platform engine architecture.
- Safe brownfield refactoring.
- Coding-agent repository governance.
- AI-agent product development.

## Source-grounded Profile

Read:

- `ARCHITECT_PROFILE.md`
- `SOURCE_VERIFICATION_BENTO.md`
- `CROSS_PLATFORM_ENGINE_EVIDENCE.md`
- `ARCHITECTURE_CAPABILITY_MATRIX.md`
- `PRACTICAL_ARCHITECTURE_EVIDENCE.md`

## Skills

| Skill | Primary use |
|---|---|
| `$architecture-review` | Review and compare architecture decisions |
| `$application-client-server-architecture` | Frontend/backend, API, RBAC, transaction, data, UI, deployment |
| `$cross-platform-native-architecture` | Qt/native platform, OS, ABI, hardware, packaging |
| `$cross-platform-engine-architecture` | Director/scene, update/render, graphics, resources, engine adapters |
| `$framework-design` | Frameworks, SDKs, plug-ins, product-line architecture |
| `$safe-incremental-refactoring` | Brownfield modernization and compatibility-preserving decomposition |
| `$code-review` | Production correctness, concurrency, persistence, communication, recovery |
| `$document-governance` | Controlled and traceable engineering documents |
| `$software-quality-iso25010` | Product-quality scenarios, metrics, evidence, release gates |
| `$development-process-tailoring` | Waterfall, iterative, Agile, XP, hybrid process |
| `$coding-agent-project-governance` | AGENTS, risk routing, subagents, worktrees, tests, release |
| `$agent-development-process` | Building an AI-agent product or agentic system |

## Important Distinctions

```text
General Qt/native application architecture
  → $cross-platform-native-architecture

Game/graphics engine runtime architecture
  → $cross-platform-engine-architecture
```

```text
Coding agents modify a software repository
  → $coding-agent-project-governance

An AI agent is the product being built
  → $agent-development-process
```

```text
Review an intended target architecture
  → $architecture-review

Move a live legacy system toward it safely
  → $safe-incremental-refactoring
```

## Package Contents

```text
software-architect-codex-pack-v4/
├── AGENTS.md
├── ARCHITECT_PROFILE.md
├── SOURCE_VERIFICATION_BENTO.md
├── CROSS_PLATFORM_ENGINE_EVIDENCE.md
├── ARCHITECTURE_CAPABILITY_MATRIX.md
├── PRACTICAL_ARCHITECTURE_EVIDENCE.md
├── AGENT_DEVELOPMENT_STANDARD.md
├── CODING_AGENT_PROJECT_STANDARD.md
├── DOCUMENT_STANDARD.md
├── PLANS.md
├── REFERENCES.md
├── CHANGELOG.md
├── VERSION
├── scripts/
├── evals/
└── .agents/skills/
```

## Installation

### Global personal guidance

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex"
New-Item -ItemType Directory -Force "$HOME\.agents\skills"

Copy-Item ".\AGENTS.md" "$HOME\.codex\AGENTS.md" -Force
Copy-Item ".\.agents\skills\*" "$HOME\.agents\skills\" -Recurse -Force
```

### Repository use

Copy only the skills and standards relevant to that repository.

Project-specific facts belong in the repository's own `AGENTS.md`, domain-invariant documents, architecture map, and runbooks.

## Validation

Run:

```text
python scripts/validate_pack.py
```

Routing cases are in:

```text
evals/skill-routing-cases.csv
```

Add real failures over time instead of expanding instructions speculatively.
