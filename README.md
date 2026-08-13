<p align="center"><img src="assets/cloudbox-logo.png" width="160" alt="CloudBox logo"></p>

<h1 align="center">CloudBox Skills</h1>
<p align="center"><strong>Build real knowledge as a side effect of real engineering work — no course, no interruption.</strong></p>

**Current version: 7.3.0**

> **This public repository is a partial mirror.** Active development of the
> full CloudBox skill pack has moved to a private repository. This public
> copy keeps receiving updates for **`teach-while-building`** — the one
> skill meant for general use — while everything else below is a frozen
> snapshot from the last full sync (v7.1.0).

## The problem

Ask an agent to explain a bug or a platform quirk and it'll explain it well.
You'll nod, feel like you get it, and move on. Two weeks later the same class
of bug bites you again — because *feeling* like you understood something
(**fluency strength**) and actually *retaining* it (**storage strength**) are
different things, and only effortful recall builds the second one. A separate
course fixes this but costs time you don't have mid-project.

## The fix: `teach-while-building`

A self-triggered Claude Code / Codex skill that folds a short comprehension
check into the work you're already doing, instead of opening a separate
teaching workspace.

- **Self-judged.** No slash command to remember — it fires only when
  something genuinely non-obvious *to you* just came up, and is likely to
  matter again.
- **Calibrated to you, not a fixed bar.** No history yet in a domain →
  defaults generous. Confirmed history → the bar can rise. You're visibly
  surprised by something it didn't flag → that's treated as a live miss and
  the bar drops for that domain. You can also just state your level once
  ("I'm junior at Android build tooling") — no re-explaining needed after
  that, via an optional `LEARNING_LEVEL.md` file.
- **Batched, not interrupting.** Flagged concepts are held and checked
  together at the next natural pause — a slice finishing, a build passing —
  not one quiz per sentence. The one exception: a concept that blocks the
  very next step gets checked immediately.
- **Confirm-or-correct, not a blind quiz.** Every question states the
  agent's own expected answer alongside it, so you're confirming or
  correcting, not performing under a spotlight.
- **Keeps only what's durable.** Confirmed concepts land in a short
  `LEARNING_LOG.md`, written in your own words — a real reference, not a
  transcript. Nothing gets logged unless the check actually confirmed it.

```
❓ Why did the implicit bindService() call crash only on Android 5.0+?
➡️ Android 5.0 banned implicit Intents for bindService() — you have to set
   an explicit package on the Intent now.
```

Full behavior contract: [`SKILL.md`](.agents/skills/teach-while-building/SKILL.md).

## Install

**Claude Code**

```bash
claude plugin marketplace add https://github.com/cloudhsu/CloudSkill.git
claude plugin install cloudbox-skills@cloudbox-marketplace --scope user
```

**Codex / ChatGPT**

```bash
codex plugin marketplace add https://github.com/cloudhsu/CloudSkill.git
```

Both install the whole snapshot as a read-only bundle; `teach-while-building`
is model-invoked, so it activates on its own once installed — nothing to run
first. Standalone (non-plugin) install and full options: [INSTALL.md](INSTALL.md).

<details>
<summary><strong>What else is in this snapshot</strong></summary>

The rest of this repository is the CloudBox architecture/quality/governance
skill pack as it stood at the last full sync — frozen, not actively updated
here. It covers things like cross-platform engine and application
architecture, safe incremental refactoring, document governance, and
AI-agent product development.

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

```text
CloudSkill/
├── .codex-plugin/           # Codex and ChatGPT plugin manifest
├── .claude-plugin/          # Claude Code plugin manifest and marketplace
├── assets/                  # CloudBox logo and icon
├── .agents/plugins/         # Codex and ChatGPT marketplace
├── .agents/skills/          # Canonical skill source
├── AGENTS.md                # Codex/shared architecture guidance
├── CLAUDE.md                # Claude Code adapter importing AGENTS.md
├── INSTALL.md                # Codex and Claude Code installation
├── PLANS.md                 # ExecPlan convention
├── docs/                    # Profile, evidence, governance, audit, references
├── evals/                   # Routing and behavior evaluation contracts
├── config/                  # Local configuration template
├── scripts/                 # Install, capture, validation, and documentation audit
├── CHANGELOG.md
└── VERSION
```

</details>

<details>
<summary><strong>Interaction-derived Eval capture (snapshot content)</strong></summary>

A local CloudSkill clone can be registered during installation. The installer
stores only local paths and safe defaults; it does not store credentials.
After configuration, the phrases `整理成正向案例` and `整理成負向案例` create
sanitized candidates under the private Eval Inbox. Candidates do not modify
formal Evals, skills, commits, or remote branches until a separate
review/import task is explicitly requested.

CloudBox 6.1 also provides versioned manual bundles and token-free Git source
discovery. Use `從專案提煉優化案例` for an initial bounded pass and
`同步優化來源` for incremental discovery. Actual URLs, credentials,
candidates, and provenance remain in ignored/private storage; see
[CloudBox evolution sources](docs/AUTOMATIC_EVOLUTION_SOURCES.md).
Import first verifies bundle/exporter/candidate schema, declared CloudBox
version, host/runtime, filename/manifest identity, and payload hashes;
contract drift is retained as unsupported evidence before candidate routing.

</details>

<details>
<summary><strong>Documentation policy (snapshot content)</strong></summary>

- Git commits and annotated tags are the authoritative version history.
- `history/` contains only a release index; it does not duplicate full source snapshots.
- Root documents are entry points. Detailed material lives under `docs/` or inside each skill.
- Each concern has one authoritative document; other documents link to it instead of copying it.

See [docs/README.md](docs/README.md) for the document ownership map.

- [Design purpose and flow](docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md)
- [Evolution change history](docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md)
- [Current agent/conversation handoff](CLOUDBOX_SKILLS_AGENT_HANDOFF.md)

</details>

<details>
<summary><strong>Runtime model evaluations (snapshot content)</strong></summary>

CloudBox includes an executable routing Eval harness in `evals/runtime/`.
Static CI validates the suite and grader without calling a model. Local
execution defaults to Ollama and requires no API key; OpenAI execution
remains optional. Private results are written under `.local/runtime-evals/`.

```bash
python3 scripts/validate_runtime_evals.py
python3 scripts/run_runtime_evals.py --provider ollama --model qwen3:4b --dry-run
python3 scripts/run_runtime_evals.py \
  --provider ollama --model qwen3:4b \
  --case-id R06-chinese-translation-no-skill --repeat 1
python3 scripts/grade_runtime_evals.py \
  --input .local/runtime-evals/<result-file>.jsonl \
  --output .local/runtime-evals/<summary-file>.json
```

The grader deterministically checks primary-skill accuracy, required
supporting skills, forbidden selected skills, execution order, no-skill
behavior, valid skill IDs, output shape, and router self-inclusion. It does
not claim to grade the full semantic quality of the final engineering answer.

```bash
python scripts/run_all_checks.py
```

</details>
