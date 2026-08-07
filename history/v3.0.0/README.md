# Software Architect Codex Pack

Version: **3.0.0**

This pack encodes a broad software/system architect operating model rather than a single-domain identity.

## Architecture Profile

The profile now explicitly covers:

- Frontend/backend and Client/Server application architecture.
- HTTP API, transaction, RBAC, audit, migration, responsive UI, deployment, and operations.
- Qt-based cross-platform IC tools on Windows, Linux, and Android.
- An OpenGL-based 2D game engine on iOS, Android, and Windows.
- Framework and platform architecture.
- Semiconductor equipment and industrial-control architecture.
- ISO/IEC 25010 quality governance.
- Waterfall, iterative, Agile, XP, and hybrid lifecycle tailoring.
- AI-agent system development and coding-agent project governance.

Read:

- `ARCHITECT_PROFILE.md`
- `PRACTICAL_ARCHITECTURE_EVIDENCE.md`

## Skills

| Skill | Primary use |
|---|---|
| `$architecture-review` | Review and compare architecture decisions |
| `$application-client-server-architecture` | Full-stack, frontend/backend, APIs, persistence, RBAC, UI, deployment |
| `$cross-platform-native-architecture` | Qt, OpenGL, native lifecycle, platform layers, hardware integration |
| `$framework-design` | Frameworks, engines, SDKs, plug-ins, product-line architecture |
| `$code-review` | Production correctness, concurrency, resources, communication, recovery |
| `$document-governance` | Controlled and traceable engineering documents |
| `$software-quality-iso25010` | Product-quality scenarios, metrics, evidence, release gates |
| `$development-process-tailoring` | Waterfall, iterative, Agile, XP, hybrid process |
| `$coding-agent-project-governance` | AGENTS.md, risk routing, subagents, worktrees, tests, release |
| `$agent-development-process` | Building an AI-agent product or agentic system |

## Important Distinction

```text
Coding agent governs software development work in a repository
    → $coding-agent-project-governance

AI agent is itself the product being designed and released
    → $agent-development-process
```

## Package Contents

```text
software-architect-codex-pack-v3/
├── AGENTS.md
├── ARCHITECT_PROFILE.md
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
└── .agents/
    └── skills/
        ├── architecture-review/
        ├── application-client-server-architecture/
        ├── cross-platform-native-architecture/
        ├── framework-design/
        ├── code-review/
        ├── document-governance/
        ├── software-quality-iso25010/
        ├── development-process-tailoring/
        ├── coding-agent-project-governance/
        └── agent-development-process/
```

## Installation

### Personal global guidance

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex"
New-Item -ItemType Directory -Force "$HOME\.agents\skills"

Copy-Item ".\AGENTS.md" "$HOME\.codex\AGENTS.md" -Force
Copy-Item ".\.agents\skills\*" "$HOME\.agents\skills\" -Recurse -Force
```

Keep detailed project-specific rules in each repository.

### Repository installation

Copy:

- `AGENTS.md`
- selected `.agents/skills/`
- `PLANS.md`
- project-specific standards/templates

into the repository and commit them when they are team rules.

## Validation

Run:

```text
python scripts/validate_pack.py
```

The validator checks:

- Skill folder/name agreement.
- Required frontmatter.
- Duplicate names.
- Description size.
- `agents/openai.yaml`.
- global `AGENTS.md` size.
- manifest generation.

## Skill Evaluation

`evals/skill-routing-cases.csv` provides positive and negative routing cases. Use it as a seed set and add real failures over time.

## Design Rule

Global `AGENTS.md` stays relatively compact. Detailed workflows live in skills and references so they are loaded only when relevant.
