# Source Verification — Lunch-ordering System

## Evidence Scope

The supplied source archive was inspected as a complete Git repository and software package.

Archive reference:

- File: `source.zip`
- Size: 57,537,592 bytes
- SHA-256: `5c4e6d5528100c697ec8da76131c2cc867dfd73a5f3126f5ca4356be9ef37cc4`

Privacy handling:

- Personal records inside `db/` and `import/` were not enumerated or reproduced.
- No employee, account, store, password, token, or transaction content is copied into this pack.
- Source, tests, structure, schemas, and engineering documents were used as architecture evidence.

## Verified Repository Facts

At the reviewed baseline:

| Item | Verified result |
|---|---:|
| Product version | `1.9.15` |
| Git commits reachable from current branch | 71 |
| Source JavaScript files | 53 |
| Source JavaScript lines | 5,653 |
| Test JavaScript files | 35 |
| Test JavaScript lines | 5,672 |
| Repository modules | 20 |
| Application/query/command services | 16 |
| Literal HTTP routes in server | 66 |
| Database tables in current schema bootstrap | 14 |
| Explicit indexes in current schema bootstrap | 8 |
| Markdown files under `docs/` | 65 |
| Version changelog documents | 41 |

Large compatibility surfaces still present:

- `src/core/database.js`: 1,237 lines.
- `src/server/index.js`: 874 lines.
- Employee client script: 668 lines.
- Administration client script: 1,386 lines.

This confirms an active brownfield modernization, not a claim that the system is already fully decomposed.

## Source-verified Architecture

### 1. End-to-end Client/Server design

The implementation contains:

- Employee Web UI.
- Administration Web UI.
- Employee APIs.
- Administration APIs.
- Authentication/session handling.
- Server-enforced RBAC.
- Application/domain logic.
- SQLite persistence.
- Excel import/export.
- Backup, logging, health, build, and NAS deployment.

The browser does not own authoritative price, balance, selected store, deadline, order legality, or permission decisions.

### 2. Compatibility façade with incremental extraction

`BentoDatabase` remains the compatibility façade while responsibilities are progressively extracted into:

- Pure policy modules.
- Restricted repositories.
- Query services.
- Command services.
- Persistence session.
- Schema/migration components.

Tests explicitly preserve the historical public prototype contract while allowing internal responsibility migration.

### 3. Capability-restricted ports

Repositories do not receive the full database/session object by default.

The code constructs frozen ports such as:

- Query port: `all/get`.
- Command port: `run`.
- Unit-of-work port: `transaction`.

This is a concrete least-capability design. It prevents repositories from silently taking ownership of transaction, save, close, or raw-session behavior.

### 4. Application-service transaction ownership

Order, balance, settlement, and processing use cases own transaction sequencing.

Examples include:

- Employee order create/update/cancel.
- Administrator append/cancel/transfer.
- Daily order processing.
- Top-up.
- Balance adjustment.
- Reversal.
- Account settlement/delete.
- System balance event creation.

The service controls business ordering; repositories expose narrower persistence primitives.

### 5. Persistence recovery beyond ordinary SQL rollback

The `sql.js` database is memory-resident and exported to a file.

`SqlJsDatabaseSession`:

1. Exports a pre-transaction snapshot.
2. Executes `BEGIN IMMEDIATE`.
3. Runs work.
4. Commits.
5. Persists through a temporary file and rename.
6. Restores both disk and in-memory state when post-commit file persistence fails.
7. Enters a write-blocked fatal state when safe restoration cannot be guaranteed.

This is a source-verified response to the specific consistency risk created by `sql.js` whole-file persistence.

### 6. Historical semantics

The system preserves snapshots for:

- Employee identity.
- Store identity and phones.
- Menu item names/prices.
- Balance events.
- Administrative actions.

Master-record deletion does not erase the historical meaning of prior transactions.

### 7. Migration and compatibility

The implementation includes:

- Static schema bootstrap.
- Schema inspection.
- Additive-column migration.
- Metadata/settings bootstrap.
- `PRAGMA user_version` gate.
- Supported legacy-version adoption.
- Future-version fail-closed behavior.
- Reopen/idempotency tests.
- Latest-database compatibility tests against a copy.

### 8. Responsive frontend and server authority

The employee and administration clients implement desktop and narrow/mobile behavior.

Frontend validation improves interaction, but permission and business invariants are enforced on the server.

### 9. Deployment topology is explicit

The documented and implemented persistence model is single-process/single-writer.

The system explicitly warns against multiple Node.js processes or containers writing the same file because each process holds an independent in-memory `sql.js` database.

This is an example of treating operational topology as an architecture constraint.

## Executed Verification

The following commands were executed successfully in the analysis environment:

- `node tests/core.test.js`
- `node tests/database-version-legacy-upgrade.test.js`
- `node tests/ui-regression.test.js`
- `node tests/integration.test.js`
- `node tests/latest-db-compatibility.test.js`

Observed results included successful verification of:

- Domain policies.
- Repository capability contracts.
- Application-service behavior.
- Transaction and persistence safety.
- Schema-version compatibility.
- Historical snapshots.
- RBAC and API integration.
- UI regression conditions.
- Existing bundled-server integration.
- Latest-database copy compatibility and source-file preservation.

## Verification Limitation

A fresh `npm test` including `npm run bundle:web` could not complete in the Linux analysis environment because the supplied `node_modules` contained the Windows esbuild binary and the available package registry could not restore the Linux `xlsx` dependency.

Therefore:

- Source-level, policy, repository, service, migration, UI-regression, existing-bundle integration, and latest-database tests passed.
- A fresh Linux rebuild of `build/web-server-bundle.cjs` was **not** verified.
- No Windows executable build, DSM deployment, browser-device test, or mobile-device test was claimed.

## Source-verified Strengths

- Architecture decisions tied to actual failure modes.
- High-risk changes sliced by use case.
- Compatibility-preserving modernization.
- Strong data/history invariants.
- Test count and source count are of comparable scale.
- Explicit negative and fault-injection tests.
- Honest handling of deployment and verification limitations.
- Documentation synchronized with code, release, and agent workflows.

## Remaining Technical Boundaries

The source also demonstrates conscious limitations:

- Large compatibility façade still exists.
- Server routing remains centralized.
- Frontend scripts remain relatively monolithic.
- Sessions are memory-local.
- Persistence is single-writer and whole-file export based.
- Horizontal scale and HA are outside the current topology.
- Runtime capability ports are JavaScript contracts, not compile-time type guarantees.

These are not hidden. They should be treated as migration context and future decision points.
