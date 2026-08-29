---
name: project-management-sync
description: Use when safely auditing, previewing, reconciling, or applying synchronization of plans, tasks, statuses, dates, or project records between a local or internal backlog and external project-management systems such as Vikunja, OpenProject, or Redmine, especially when provider versions/capabilities may drift, duplicate writes must be prevented, credentials must work across macOS/Windows/Ubuntu/CI, or every mutation needs post-write verification.
---

# Project Management Sync

## Core principle

Treat synchronization as an idempotent reconciliation between an authoritative
backlog and an external project-management system. Keep provider API semantics,
version drift, OS secret storage, and remote task identity behind explicit
adapters; never hide uncertainty behind a successful-looking response.

## Decision gates

- If there is no external project-management record set, provider, or remote
  synchronization effect, do not route here; use the narrower architecture,
  API, date/time, or code-review skill.
- If the provider/version/capability cannot be discovered, the target scope
  cannot be enumerated, credentials are available only as prompt text, or
  identity is ambiguous, produce an audit/read-only plan and block writes.
- If a mutation has an unknown outcome, reconcile the remote state before any
  retry. Do not convert an uncertain request into a second create.

## Responsibility split

Keep the canonical reconciliation engine provider-neutral. A provider adapter
owns discovery, authentication transport, pagination, schema/status mapping,
capability checks, mutation calls, and readback. The reconciliation engine owns
authority, identity, field ownership, operation planning, idempotency, and
verification. Do not scatter provider-version branches through the canonical
model.

## Route here when

- Tasks, plans, statuses, dates, or project records must be read or synchronized
  across an internal backlog and Vikunja, OpenProject, Redmine, or another
  project-management provider.
- An existing remote task must be reconciled without duplicating work created by
  another agent, client, or previous sync run.
- A provider API version, capability, pagination, authentication, or timestamp
  difference can affect the operation.
- A cross-platform agent needs safe local credential retrieval and redaction.

## Non-trigger conditions

- Designing a generic web API without an external task-system synchronization
  use case; use `application-client-server-architecture`.
- Reviewing provider client code for a concrete bug; use `code-review`.
- Creating a project roadmap without remote synchronization or API effects.

## Required workflow

1. Declare source authority, target provider/profile, sync direction, write mode,
   scope, and whether create/update/delete are allowed. Default to dry-run;
   delete is disabled unless explicitly authorized.
2. Load only non-secret configuration, then resolve credentials through the
   platform SecretStore. Never accept a token from a prompt, URL, command-line
   argument, repository file, or model context.
3. Discover the provider root, version, schema, pagination rules, permissions,
   and capabilities. Select a versioned adapter; unknown or incompatible
   capabilities are read-only/manual-review conditions.
4. Enumerate the complete target scope with pagination and stable ordering.
   Resolve identity using a persisted source key or remote ID. Title matching is
   only a fallback when exactly one match exists; ambiguity blocks mutation.
5. Normalize only supported canonical fields: title, description, status,
   priority, dates, project key, labels, and provenance. Preserve unknown fields
   and report lossy mappings instead of inventing provider fields.
6. Produce a plan containing `no-op`, `create`, `update`, `ambiguous`, and
   `blocked` operations. Record correlation and idempotency identities before
   external mutation.
7. Apply only approved operations with provider-specific methods and bounded
   retries. A timeout or lost response is `unknown`, not proof of failure;
   reconcile by reading the remote system before retrying.
8. Re-read every mutated record and verify authoritative fields, completion
   timestamps, remote IDs, and unchanged task counts. Report the exact result,
   residual uncertainty, unavailable evidence, and a final privacy audit. Never
   echo an ambient user's email, account, or identity—even to explain that it
   was redacted; use a generic placeholder such as `actor@example.invalid`.

For bidirectional synchronization, declare ownership per field and an explicit
conflict policy before planning. Never use last-write-wins by default. A field
with no owner or conflict rule is read-only until one is defined.

Use these execution modes explicitly:

- `audit`: discover and report provider state; never mutate.
- `dry-run`: produce the reconciliation plan and counts; never mutate.
- `apply`: execute only approved create/update operations after all gates pass.
- `reconcile`: resolve `unknown` operations by remote readback before deciding
  whether a new mutation is safe.

## Required output

1. Provider/version/capability and platform SecretStore used, without secrets.
2. Source and target authority, scope, identity/mapping strategy, and mode.
3. Planned and executed counts for no-op/create/update/ambiguous/blocked.
4. Post-write readback evidence, timestamp interpretation, and reconciliation
   status.
5. Redacted errors, unsupported fields/capabilities, privacy-audit result, and
   next action. The report must contain no real email, account, or credential.

A bundled `vikunja-sync-reminder` hook enforces the end-of-work sync habit
deterministically (mandatory, loop-safe) at session-stop time.

## Common mistakes

- Creating by title before listing and reconciling existing tasks.
- Assuming POST, PUT, PATCH, status names, timestamps, or URL shapes are
  portable across providers or versions.
- Treating a 2xx response as proof of the final remote state.
- Retrying a timeout without checking whether the first mutation committed.
- Logging Authorization headers, tokens, cookies, query credentials, or raw
  provider responses.
- Inventing or echoing a real person's email, account, hostname, project name,
  or other identifying detail when a generic actor or placeholder is enough.
- Storing credentials beside portable configuration or relying on macOS-only
  Keychain APIs when Windows or Ubuntu is supported.

## Human-Readable Description Format

When a task's `description` field is the primary channel a human reads (not
just a sync payload), write it so the human never has to reconstruct state
from chat scrollback:

- Fixed sections: 標題 (or Title), 問題/背景, 建議處理方式 (or an equivalent
  plan section), Acceptance Criteria, Source. Keep this shape even across a
  single language switch mid-project; consistency matters more than which
  language.
- Reference the task by the provider's human-visible identifier (e.g. a
  project-local `#N`, not a bare internal/global ID a human never sees in
  their own UI) once that identifier has been confirmed by reading the task
  back, not guessed from creation order.
- Prefer concrete, checkable evidence over a narrative summary: PR numbers,
  before/after counts or percentages, exact file paths in inline code,
  pass/fail counts -- a claim a reader could verify against the repository
  themselves, not "made good progress."
- For an ongoing task, append a new dated block per update rather than
  rewriting the description -- the description is itself an append-only
  progress record, the same discipline `lifecycle.json`'s `notes` field
  already requires for a Skill (see a private companion capability
  skill-lifecycle-standard.md`). Mark items done with a clear visual/textual
  distinction (a checkmark, a "still open" list) so a skim shows status
  without reading every paragraph.
- Keep the chat reply itself short when a detailed description was just
  written to the task -- point at the task rather than repeating its content
  in the conversation.

## Supporting references

- For a structured Vikunja plan that needs mechanical validation and safe local
  execution, use `scripts/vikunja_sync.py` and read
  `references/vikunja-script.md`. It enforces the fixed human-readable task
  sections, append-only progress blocks, and an explicit `Agent` field; it does
  not infer identity or accept tokens from arguments.
- Read `references/sync-contract.md` for authority, field ownership, identity,
  operation states, conflict policy, and verification rules.
- Read `references/provider-compatibility.md` when selecting or reviewing a
  provider adapter, API version, discovery probe, or capability boundary.
- Read `references/secret-store-and-redaction.md` when configuring credentials,
  local profiles, CI, logging, Eval evidence, or cross-platform deployment.
