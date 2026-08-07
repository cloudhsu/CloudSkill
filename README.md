# Software Architect Codex Pack

Version: **2.0.0**

This pack provides persistent architecture guidance, reusable Codex/ChatGPT skills, engineering standards, and templates.

## Contents

```text
software-architect-codex-pack/
├── AGENTS.md
├── AGENT_DEVELOPMENT_STANDARD.md
├── DOCUMENT_STANDARD.md
├── PLANS.md
├── REFERENCES.md
├── CHANGELOG.md
├── VERSION
└── .agents/
    └── skills/
        ├── architecture-review/
        ├── framework-design/
        ├── code-review/
        ├── document-governance/
        ├── software-quality-iso25010/
        ├── development-process-tailoring/
        └── agent-development-process/
```

## Skills

### `$architecture-review`

Architecture alternatives, state ownership, failure/recovery, migration, and verification.

### `$framework-design`

Framework, platform, engine, plug-in, cross-platform, and product-line design.

### `$code-review`

Production code review emphasizing correctness, concurrency, lifecycle, communication, and recovery.

### `$document-governance`

Engineering document creation and review, including multi-audience reports, specifications, traceability, and change control.

### `$software-quality-iso25010`

ISO/IEC 25010-based quality requirements, quality scenarios, metrics, test objectives, dashboards, and release gates.

Defaults to ISO/IEC 25010:2023 unless a project explicitly declares the 2011 edition.

### `$development-process-tailoring`

Selection and tailoring of waterfall, iterative, agile, XP, and hybrid lifecycles.

### `$agent-development-process`

AI-agent task contract, autonomy, tools, data, harness, evaluations, hardening, release, and continuous improvement.

## Repository Installation

Copy these into the repository root:

- `AGENTS.md`
- `.agents/skills/`
- `PLANS.md`
- Standards/templates required by the project

Commit them to Git when they are intended as shared team rules.

## Personal Global Installation

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex"
New-Item -ItemType Directory -Force "$HOME\.agents\skills"

Copy-Item ".\AGENTS.md" "$HOME\.codex\AGENTS.md" -Force
Copy-Item ".\.agents\skills\*" "$HOME\.agents\skills\" -Recurse -Force
```

Keep project-specific rules in each repository instead of placing all details in the global `AGENTS.md`.

## Invocation

In Codex CLI or IDE:

```text
/skills
$architecture-review
$framework-design
$code-review
$document-governance
$software-quality-iso25010
$development-process-tailoring
$agent-development-process
```

Skills may also be selected automatically when the task matches their descriptions.

## Recommended Agent Development Workflow

```text
Need / problem
  → agent task contract
  → autonomy and risk classification
  → evaluation plan
  → harness architecture
  → minimum vertical slice
  → trace and failure review
  → controlled improvement
  → regression and quality gates
  → reviewed release
  → production feedback loop
```

Use `AGENT_DEVELOPMENT_STANDARD.md` as the governance document and the `agent-development-process` templates as working artifacts.

## ISO/IEC 25010 Note

The pack summarizes a practical application method. It does not reproduce or replace a licensed copy of ISO/IEC 25010. The organization's declared edition, approved mappings, contractual requirements, and licensed standards remain authoritative.
