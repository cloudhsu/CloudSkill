# CloudBox

<p align="center"><img src="assets/cloudbox-logo.png" width="160" alt="CloudBox logo"></p>

**Current version: 6.0.0**

CloudBox is the user-facing plugin brand for the `CloudSkill` repository: a portable set of software/system architecture skills and operating guidance for **OpenAI Codex**, **ChatGPT**, and **Claude Code**.

The same canonical `.agents/skills/` directories are used by both plugin manifests and by the standalone installers. Existing skill IDs remain stable.

## Install

CloudBox supports Codex/ChatGPT and Claude Code plugins, plus the existing standalone user/project installation. See [INSTALL.md](INSTALL.md) and [docs/CLOUDBOX_PLUGIN.md](docs/CLOUDBOX_PLUGIN.md).


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
├── .codex-plugin/           # Codex and ChatGPT plugin manifest
├── .claude-plugin/          # Claude Code plugin manifest and marketplace
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

- [Design purpose and flow](docs/CLOUDSKILL_DESIGN_AND_FLOW.md)
- [Evolution change history](docs/CLOUDSKILL_CHANGE_HISTORY.md)
- [Current agent/conversation handoff](CLOUDSKILL_AGENT_HANDOFF.md)

Start with the handoff document when continuing an existing multi-session Skill evolution task.

## Runtime model evaluations

CloudBox includes an executable routing Eval harness in `evals/runtime/`. Static CI validates the suite and grader without calling a model. Local execution defaults to Ollama and requires no API key; OpenAI execution remains optional. Private results are written under `.local/runtime-evals/`.

Validate the Eval suite without a model call:

```bash
python3 scripts/validate_runtime_evals.py
python3 scripts/run_runtime_evals.py --provider ollama --model qwen3:4b --dry-run
```

Run one local smoke case:

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --case-id R06-chinese-translation-no-skill \
  --repeat 1
```

Run the complete local Canary Suite:

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --repeat 1 \
  --num-ctx 4096
```

Grade the latest result file:

```bash
python3 scripts/grade_runtime_evals.py \
  --input .local/runtime-evals/<result-file>.jsonl \
  --output .local/runtime-evals/<summary-file>.json
```

The grader deterministically checks primary-skill accuracy, required supporting skills, forbidden selected skills, execution order, no-skill behavior, valid skill IDs, output shape, and router self-inclusion. It does not claim to grade the full semantic quality of the final engineering answer.

## Validate

```bash
python scripts/run_all_checks.py
```
