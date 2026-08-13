# Codex Runtime Eval path

## Purpose

Use Codex CLI as a second executable provider for the same CloudSkill Routing and Behavior Eval contracts. This path is intended for comparison against the local Ollama baseline, not as a replacement for deterministic validation.

## Authentication

```bash
codex login status
codex login
```

The local path reuses saved Codex CLI authentication. It does not read, copy, print, or package the authentication cache.

## Commands

Quota-conscious smoke test:

```bash
./cloudbox-skills-eval-codex
```

Three-repeat comparison:

```bash
./cloudbox-skills-eval-codex --repeat 3
```

Optional explicit model override:

```bash
./cloudbox-skills-eval-codex --codex-model <model-name>
```

## Execution contract

The adapter uses:

- `codex exec`
- `--ephemeral`
- `--sandbox read-only`
- `--ask-for-approval never`
- `--ignore-user-config`
- `--ignore-rules`
- `--json`
- `--output-last-message`
- `--output-schema` for Routing JSON

Each request runs in a temporary empty Git repository. The full Router, case, schema, and selected Skill context is supplied in the prompt. This prevents Codex from gaining an unfair result by reading additional files from the CloudSkill checkout.

## Evidence

Record:

- Codex CLI version
- provider and requested model
- thread ID when available
- token usage when emitted by `turn.completed`
- isolated-repository and sandbox settings
- routing and behavior outputs
- deterministic grading reports
- one review ZIP

Do not record authentication details.

## Interpretation

Compare providers separately:

- Ollama measures the local small-model path.
- Codex measures the authenticated higher-capability agent path.
- Static validators prove the harness contract without consuming either provider.
- A Codex authentication or quota error is not a routing or behavior regression.
