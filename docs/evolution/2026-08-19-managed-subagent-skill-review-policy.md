# Managed sub-agent Skill review policy — 2026-08-19

## Decision

Semantic review of new or materially changed Skills uses the host's managed,
model-selected sub-agent interface when available. Runtime Eval provider CLIs
remain case-execution and adapter-diagnostic tools; they are not substitutes for
the independent reviewer panel.

| Host family | Preferred independent reviewers | Allowed fallback |
|---|---|---|
| Codex | GPT-5.6 Luna + GPT-5.6 Sol | none without a versioned policy change |
| Claude Code | Sonnet 5 + Opus 5 | matching 4.8 generation only when 5 is unavailable |

Every review records exact selected or provider-returned model identity and
agent/run identity. A generic label such as `GPT` or `Claude` is insufficient.

Execution and final review use two immutable identities. The candidate packet
contains the base HEAD and all changed/untracked semantic inputs while excluding
its own output evidence. Behavior runs bind to that ID. A review packet then
adds the candidate manifest and GREEN evidence; final reviewers bind to the
second ID. Reviewer reports remain outputs, avoiding a self-referential hash.

## Brownfield scope boundary

The review packet records whether the source product already exists or has been
refactored. Skill distillation does not authorize rewriting that implementation.
For a brownfield target, reviewers require a current responsibility/contract
map, characterization baseline, compatibility preservation and the smallest
coherent slice. A whole rewrite is a blocking finding unless the user separately
and explicitly authorized it.

## Observed process RED

During the 2026-08-19 equipment Skill increment, the integrator initially tried
to reach Luna/Sol through `codex exec` model overrides. One attempt used an
unsupported CLI argument; the corrected attempt then failed in the local
in-process app-server with `Operation not permitted`. No model execution
occurred. The managed sub-agent selector was available but had not been checked.

Failure layer: Skill-development workflow discipline. The repository described
preferred model families but did not make the managed sub-agent transport,
model mapping, independence, identity evidence or CLI non-substitution rule a
fixed lifecycle contract.

## GREEN mechanism

- `config/skill-lifecycle-policy.json` now declares the transport, Codex and
  Claude model pairs, Claude 4.8 availability fallback, same-packet parallelism,
  read-only authority, exact identity requirement and blocking verdicts.
- `developing-skills` documents the workflow and transport boundary.
- `DEVSK-BEH-022` preserves the observed mistake as a permanent discipline case.
- `DEVSK-BEH-023` preserves the no-unapproved-rewrite boundary for existing,
  previously refactored products.
- `scripts/validate_skill_lifecycle.py` rejects policy or documentation drift.

This deterministic GREEN proves that the rule is retained and packaged. It does
not by itself prove model behavior; per-candidate sub-agent results remain
separate release evidence.

## Handoff-size rule

Full review evidence belongs in a dated evolution or release artifact. The live
handoff keeps only a short pointer and current gate state; it must not absorb raw
review output or repeat the full policy.
