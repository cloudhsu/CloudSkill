# CloudSkill design purpose and evolution flow

## Design purpose

CloudSkill is the repository behind the CloudBox skill set. Its purpose is to make architecture, equipment-control, modeling, quality, documentation, and agent-governance knowledge executable as versioned Skills rather than leaving it as informal prompt advice.

The system is designed so that a user, ChatGPT/Codex session, Claude Code session, or another coding agent can:

- select the smallest sufficient Skill set;
- load authoritative Skill instructions and declared references;
- produce an engineering deliverable;
- evaluate routing and behavior with reproducible evidence;
- evolve Skills without losing history, safety, or decision boundaries.

## Problems it is intended to solve

### Ambiguous Skill selection

Adjacent Skills overlap in vocabulary. Examples include communication code review versus equipment state modeling, component state/command contracts versus cross-layer recovery, semiconductor domain interpretation versus software architecture, and document transformation versus quality-metric definition.

CloudSkill routes by deliverable ownership and failure boundary rather than by isolated keywords.

### Knowledge that cannot be maintained

Prompt-only guidance becomes duplicated, stale, and difficult to test. CloudSkill gives each concern one authoritative Skill or document owner and validates the repository structure.

### Improvements without evidence

A plausible edit can improve one Eval while regressing another. The repository therefore requires deterministic validators, routing cases, behavior rubrics, local Runtime Eval evidence, and explicit interpretation before claiming improvement.

### Local execution fragility

Python paths, Ollama/Codex availability, context budgets, interrupted model runs, missing reports, and uncommitted work can invalidate an evaluation. The local tooling separates infrastructure failure, context failure, routing failure, behavior failure, refinement failure, and packaging failure.

### Multi-session continuity

Long evolution work can span conversations or agents. Root handoff and history documents preserve current state, open problems, commands, evidence, and safety rules.

## Simple end-to-end flow

```text
User request
  -> using-cloudskill routes by decision/failure boundary
  -> selected Skill instructions and references are loaded
  -> model produces a structured final deliverable
  -> deterministic routing and behavior graders evaluate explicit evidence
  -> local runner packages source hashes, reports, environment, raw output, and status
  -> reviewer classifies the earliest failing layer
  -> developing-skills governs the smallest Skill or Eval change
  -> static checks run
  -> Ollama and/or Codex Runtime Eval runs
  -> cloudskill-resume commits, pushes, updates the Draft PR, and watches CI
  -> handoff and change history are updated
```

## Skill lifecycle

Every Skill uses:

```text
draft -> experimental -> active -> stable -> deprecated
```

A stage change is an evidence decision, not a Markdown edit. See `.agents/skills/developing-skills/references/skill-lifecycle-standard.md`.

## Runtime Eval layers

1. Repository/static layer — file contracts, manifests, lifecycle metadata, prompt assembly, graders, and packaging.
2. Provider layer — Ollama, Codex CLI, or optional OpenAI execution.
3. Routing layer — primary owner, supporting boundaries, forbidden Skills, and execution order.
4. Behavior layer — final engineering deliverable and required evidence.
5. Refinement layer — optional rewrite that must preserve the raw answer and satisfy a stricter final-output contract.
6. Review-bundle layer — source inventory, status, reports, raw/refined JSONL, environment, and logs.
7. Release layer — Draft/ready/merge decision based on stated criteria.

## Provider roles

- Ollama `qwen3:4b` tests the local small-model path and is expected to expose prompt and boundary weaknesses.
- Codex CLI provides a higher-capability GPT comparison using the same cases, prompts, schemas, and graders.
- Claude Code CLI (`claude -p`, headless/non-interactive) provides a higher-capability Claude comparison through the same harness, isolated with `--safe-mode --tools "" --permission-mode acceptEdits --no-session-persistence --strict-mcp-config` and an explicit "do not inspect the workspace, do not use any tool" prompt framing, so it sees only the assembled Eval prompt, not this repository's own CloudBox skills. `--permission-mode acceptEdits` avoids the non-interactive session stalling on a permission prompt it cannot answer; the ephemeral empty directory has nothing real for an accepted edit to affect.
- Results remain provider-specific. A stronger provider must not hide a weak local path, a weak local model must not automatically invalidate deterministic infrastructure work, and Ollama/Codex/Claude scores are never averaged together.

## Provider registry

The authoritative Runtime Eval provider list is:

```text
evals/runtime/contracts/providers.json
```

`scripts/providers_contract.py` is the only executable adapter for that data
(`PROVIDER_IDS`, `LOCAL_PROVIDER_IDS`, `HOSTED_AGENT_PROVIDER_IDS`,
`get_provider`, `refinement_default`). `scripts/run_runtime_evals.py`,
`scripts/run_local_eval_review.py`, and `cloudskill-resume` must read the
provider ID set from this contract rather than hand-copying a literal tuple or
case statement. `scripts/validate_providers_contract.py` checks the contract
shape, that every registered hosted-agent adapter exports the expected
`<name>_preflight`/`call_<name>_cli` functions, that every registered local
adapter's `call_site` function exists, and that every required consumer
(including the shell-based `cloudskill-resume`, checked by literal scan since
shell cannot import Python) actually reaches every registered provider ID.
It also runs the same two mutation-test categories used for the Behavior
output contract: a positive propagation check (AST-parses each Python
consumer's `--provider` `choices=` expression and requires it to reference
`PROVIDER_IDS` symbolically, not a copied tuple, so a contract edit
propagates without editing the consumer) and a negative drift-injection scan
(every other script and `cloudskill-resume`'s case statement must not
contain a hand-typed provider tuple/pattern that bypasses the registry).

Two provider families exist:

- `local` — a locally hosted model server called directly over HTTP (today:
  Ollama's `/api/chat`). Adding a second local backend means adding
  `scripts/local_providers/<name>_adapter.py` with the same call signature as
  `call_ollama`, and registering it with `"family": "local"`.
- `hosted-agent` — an authenticated CLI tool invoked non-interactively in an
  isolated, read-only, no-tool-access context (Codex CLI, Claude Code CLI).
  Adding a new one means adding `scripts/<name>_eval_adapter.py` mirroring
  `scripts/codex_eval_adapter.py` or `scripts/claude_eval_adapter.py`, and
  registering it with `"family": "hosted-agent"`.

Adding either kind of provider always ends with running
`scripts/validate_providers_contract.py` before commit.

## Behavior output contract authority

The authoritative Behavior-output definition is:

```text
evals/runtime/contracts/behavior-output-contract.json
```

`scripts/behavior_output_contract.py` is the only executable adapter for that
data. It supplies:

- contract ID and SHA-256 fingerprint;
- Behavior and refinement minimum final lengths;
- JSON schemas;
- Runtime and Refiner prompt requirements;
- structured `{ "final": "..." }` extraction;
- strict terminal `<final>` legacy compatibility;
- internal-planning detection patterns.

The Runtime Prompt, Refiner Prompt, providers, extractors, and Validators must
import this adapter. They must not copy individual prompt sentences as separate
validation contracts.

`scripts/validate_behavior_contract.py` validates the actual assembled Runtime
and Refiner prompts and the executable extraction behavior. A change to the
contract therefore propagates through one source instead of requiring synchronized
manual edits across multiple files.

The Review ZIP records the contract ID and fingerprint so a future conversation
or agent can determine exactly which output contract produced the evidence.

### Consumer registry

The authoritative contract also owns `required_consumer_paths`. Every listed
Runtime, Refiner, or Validator module must import
`scripts/behavior_output_contract.py`.

`scripts/validate_behavior_contract.py` parses each registered Python module and
checks:

- the module imports the shared adapter;
- exported contract IDs and fingerprints match;
- retired function names and Prompt-marker literals are absent;
- other Validators do not duplicate Behavior-output semantics.

The release package also performs two mutation tests:

1. add a Prompt requirement to the authoritative JSON contract and verify that
   Runtime and Refiner Prompt assembly still validates without editing either
   consumer;
2. inject a retired literal into an adjacent Validator and verify that the
   anti-drift Validator fails.

This closes the gap between centralizing the contract and proving that every
consumer actually uses it.

## Evolution rule

Always modify the earliest proven failing layer.

Examples:

- Missing source evidence -> fix the bundle or prompt assembly.
- Ambiguous case -> fix the case before the Skill.
- Correct case but repeated wrong boundary -> fix Router/Skill composition.
- Good raw deliverable but bad extraction -> fix the parser, not the Skill.
- Good structure but missing engineering evidence -> improve the selected Skill or behavior contract.
- Authentication/quota failure -> classify as provider availability, not Skill quality.

## Required artifacts per increment

- executable overlay or patch;
- static validation result;
- latest Runtime Eval review ZIP, or a clear deferred-run reason;
- design/flow documentation;
- reverse-chronological change history;
- current agent handoff;
- interruption-safe application and resume command.
