# Cross-agent multi-model orchestration

Use this protocol when Codex, Claude Code, or another subprocess-capable agent
is the coordinator and must invoke independent agents or CLIs from another model
family.

## Host-neutral authority

The coordinator owns orchestration state, not truth about the evaluated answer.
Its responsibilities are to freeze evidence, assign roles, enforce isolation,
collect raw verdicts, preserve lineage, and adjudicate disagreements. A
coordinator must not weight its own model family more heavily or silently edit a
judge verdict.

The protocol is symmetric:

- A Codex coordinator may use Codex sub-agents and invoke Claude Code CLI for
  independent Claude judges or extractors.
- A Claude Code coordinator may use Claude sub-agents and invoke `codex exec`
  for independent Codex judges or extractors.
- Another host may participate only when it can provide equivalent process,
  file, permission, output, and model-identity evidence.

## Execution contract

Before launching any worker:

1. Create one sanitized, immutable evidence packet and record its SHA-256.
2. Assign one role per invocation: extractor, counterexample author, patch
   author, judge, or adjudicator.
3. Give the worker an explicit file allowlist and the least tool capability it
   needs. Evaluation workers default to read-only and no network.
4. Pin the requested model or record the provider alias plus the canonical model
   actually returned. Never claim a requested alias proves the returned model.
5. Use a unique output path per worker. Only the coordinator writes the combined
   report; workers must not share a mutable `latest` file.
6. Record command/adapter version, prompt hash, evidence hash, exit state,
   latency/token usage when available, raw verdict path, and any fallback.
7. Do not expose one judge's verdict to another judge before both independent
   results are frozen.

Use the repository's existing hosted-agent adapters or equivalent safe flags:
non-interactive execution, no session persistence, explicit sandbox/read-only
scope, disabled unrelated tools/plugins/MCP, and no workspace discovery beyond
the allowlist. Do not copy credentials into prompts or artifacts.

## Coordinator-specific guidance

### Claude Code as coordinator

- Use Claude sub-agents for Claude-family roles when available.
- Invoke Codex through the repository's Codex adapter or a non-interactive
  `codex exec` command with read-only sandboxing and explicit output schema.
- Keep Codex outputs in per-worker paths; do not allow parallel writers to the
  Runtime Eval stable ZIP or a shared report.
- Distinguish Claude Code's requested alias from the canonical Claude model in
  returned metadata, and do the same for Codex.

### Codex as coordinator

- Use Codex sub-agents for Codex-family roles when available.
- Invoke Claude through the repository's Claude adapter or `claude -p` with
  safe mode, no session persistence, strict/empty MCP configuration, and only
  the required read capability.
- Preserve Claude's structured result and canonical returned model separately
  from the coordinator's synthesis.

## Capability and failure handling

First run read-only preflight: executable/version, authentication status without
credential disclosure, model availability when discoverable, writable output
directory, and absence of conflicting writers.

- Missing CLI, authentication, quota, or model access: `BLOCKED` for that worker.
- Unsupported alias with a documented fallback: record both and require the
  coordinator to decide whether the experiment remains comparable.
- No subprocess capability (for example, a sandboxed web/Desktop Skill
  surface): do not claim cross-family execution. Export the frozen packet for
  external execution or use `MANUAL_REQUIRED`.
- Worker crash or malformed output: retain raw stderr/status, do not fabricate a
  verdict, and retry only when the operation is idempotent and the retry policy
  is explicit.

Panel degradation must be truthful. A planned 2x2 with one blocked worker is a
1x2 or 2x1 result, not a completed 2x2. Safety-veto findings remain open until
adjudicated even if the other workers pass.

## Concurrency boundary

Parallelize read-only judging and independent extraction. Serialize any command
that writes a shared stable artifact, modifies a Skill, installs a plugin,
commits, pushes, or changes release state. Use one patch author and one release
coordinator.
