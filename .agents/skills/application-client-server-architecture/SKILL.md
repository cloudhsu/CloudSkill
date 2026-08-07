---
name: application-client-server-architecture
description: Design or review full-stack, frontend/backend, web, desktop-client/server, API, persistence, authentication, responsive UI, deployment, and operational architecture. Use when authority, transactions, contracts, state ownership, data history, or client/server boundaries matter. Do not use for native rendering-engine portability.
---

# Application and Client/Server Architecture

Read:

- `references/full-stack-boundaries.md`
- `references/client-server-checklist.md`
- `references/production-small-system-case.md`

## Workflow

### 1. Establish system topology

Identify:

- Client types and trust levels.
- Server processes and deployment nodes.
- External systems.
- Persistence technology.
- Network and process boundaries.
- Online/offline behavior.
- Scale and concurrency envelope.
- Operational ownership.

Do not infer that a small user count makes correctness, security, migration, or recovery unimportant.

### 2. Define authority and ownership

For each business fact and state, state whether the authority is:

- Client.
- Server/application service.
- Database.
- External service.
- Device or physical process.

Client-side validation may improve interaction but must not become the only enforcement for price, permission, identity, workflow state, or data integrity.

### 3. Model use cases and invariants

Define:

- Actor.
- Preconditions.
- Command/query.
- State transitions.
- Side effects.
- Transaction boundary.
- Idempotency.
- Failure behavior.
- Audit/history requirements.
- Acceptance evidence.

### 4. Design API and protocol contracts

For each operation define:

- Identity and authorization.
- Method/path or message type.
- Request schema and validation.
- Response schema.
- Stable error codes.
- Concurrency/version behavior.
- Retry semantics.
- Correlation identity.
- Compatibility policy.

### 5. Design persistence and consistency

Determine:

- Source of truth.
- Transaction ownership.
- Unique constraints.
- Snapshot versus live join behavior.
- Migration strategy.
- Backup/restore.
- Multi-writer assumptions.
- Crash and partial-save recovery.
- Retention and audit.

### 6. Design client architecture

Evaluate:

- State source and refresh.
- Optimistic versus authoritative updates.
- Desktop and mobile information architecture.
- Accessibility and keyboard/touch interaction.
- Error, empty, loading, and recovery states.
- Safe rendering.
- Session and identity handling.
- View-model boundaries.

### 7. Security and privacy

Review:

- Authentication.
- Server-enforced authorization.
- IDOR and owner spoofing.
- Replay and duplicate submission.
- Session/cookie/token handling.
- Password storage.
- Audit.
- Input limits.
- Logging redaction.
- Trust boundaries.

### 8. Deployment and operations

Define:

- Build artifact.
- Configuration source.
- Version source.
- Health/readiness.
- Logging.
- Backup.
- Upgrade/migration.
- Rollback.
- Single/multi-process limits.
- Reverse proxy/TLS.
- Operational runbook.

### 9. Verify quality

Map system-specific scenarios to ISO/IEC 25010 where useful.

Test:

- Domain policies.
- Transactions.
- API integration.
- RBAC negatives.
- UI regression and narrow layouts.
- Migration and old-data compatibility.
- Restart and persistence recovery.
- Packaging and deployment.

## Output Format

1. System topology
2. Authority and state ownership
3. Use cases and invariants
4. Client/server and API contracts
5. Persistence and consistency
6. Frontend architecture
7. Security
8. Deployment and operations
9. Quality scenarios and tests
10. Migration risks and recommendation

## Brownfield and Embedded Persistence

When the application uses an embedded or memory-exported database:

- Treat process count and writer topology as architecture.
- Distinguish SQL commit from durable file persistence.
- Define post-commit persistence failure behavior.
- Test source-database copies rather than modifying production evidence.
- Use schema-version gates before migration.
- Fail before writes when a database is newer than supported.
- Preserve historical snapshots when master records may be deleted.

When modernizing an existing façade, use `$safe-incremental-refactoring` together with this skill.
