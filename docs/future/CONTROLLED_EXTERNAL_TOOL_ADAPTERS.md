# Controlled external tool adapters — future discussion

Status: the controlled local CLI and Git vertical slice is implemented for the
CloudBox 6.3 candidate. MCP, live GitHub mutation, NAS polling, and wider
adapters remain future work. See `docs/CONTROLLED_TOOL_ADAPTERS.md` for the
implemented boundary; this document does not authorize external side effects.

## Pressure

CloudBox Skills currently provide engineering decisions and use repository
scripts for deterministic validation, Eval exchange, provider adapters, and
release support. A later increment should evaluate a reusable execution layer
similar to the CLI-plus-Skill or MCP tool pattern used by agent-oriented
platforms: Skills describe when and why a capability is appropriate, while a
versioned adapter performs the operation and returns verifiable evidence.

This could reduce model context and duplicated host-specific instructions for
Git/NAS intake, Eval execution, build/test, deployment inspection, PR/release,
and other bounded integrations. It must not become an unrestricted shell
escape hidden inside a Skill.

## Required discussion decisions

- Capability manifest and input/output schema, including adapter and protocol
  versions.
- Read-only versus mutating operations, least authority, approval policy, and
  prohibited actions.
- Secret references and private endpoint resolution without storing URLs,
  credentials, or sensitive payloads in public repository content or logs.
- Stable action IDs, idempotency keys, timeout classification, retry ceilings,
  late-result reconciliation, cancellation, and compensation or rollback.
- Durable checkpoints, fencing, concurrent-writer behavior, and integration
  with the lifecycle owner introduced in 6.2.
- Structured evidence: exit state, hashes, external resource identity,
  observed side effects, cost, latency, and redacted diagnostics.
- CLI, MCP, or hybrid transport selection; host portability; offline and
  disconnected operation; compatibility and migration rules.
- Token policy: external deterministic filtering and summaries before model
  context, bounded retrieval, cache validity, and zero-model no-change paths.
- Threat model and sandboxing for third-party executables, supply-chain
  provenance, command injection, confused deputy behavior, and credential
  exfiltration.

## Proposed boundary

`development-process-tailoring` remains the lifecycle/plan owner. Technical
Skills decide what evidence and constraints are required. A future tool adapter
registry exposes only declared capabilities. The host or coordinator owns
authorization and invokes an adapter through the declared contract; the
adapter does not expand authority. Every mutating operation must be resumable
or explicitly non-resumable, and its completion must be reconciled from the
external authoritative system rather than inferred from timeout or transport
acknowledgement.

Before implementation, compare at least direct CLI, MCP server, and a thin
local broker. Select based on actual deployment, secret, offline, and recovery
pressures rather than treating one transport as universally preferable.
