# Source Evidence — Lunch-ordering System

## Status and privacy

**Evidence level: source-verified.**

The supplied complete Git repository and tests were inspected. Personal records in database/import directories were not enumerated or reproduced.

## Verified baseline

| Item | Result |
|---|---:|
| Product version at review | 1.9.15 |
| Reachable commits | 71 |
| Source JavaScript | 53 files / 5,653 lines |
| Test JavaScript | 35 files / 5,672 lines |
| Repository modules | 20 |
| Application/query/command services | 16 |
| Literal server routes | 66 |
| Current schema tables | 14 |
| Current schema indexes | 8 |

## Architecture evidence

- Employee and administration frontends with desktop/mobile behavior.
- Node.js HTTP server and server-authoritative business rules.
- Authentication, session handling, RBAC, denial audit, and password policy.
- Application services owning use-case and transaction sequencing.
- Capability-restricted query, command, and unit-of-work ports.
- SQLite through `sql.js` with whole-file persistence and explicit recovery.
- Historical snapshots surviving master-record deletion.
- Additive/idempotent migration and schema-version gates.
- Windows and Synology NAS deployment, logging, backup, health, and release controls.
- Compatibility façade supporting incremental extraction rather than rewrite.

## Distinctive persistence behavior

A SQL commit is not the final durable boundary because `sql.js` keeps the database in memory and exports it to a file. The persistence session captures a pre-transaction snapshot, commits, persists through a temporary file/rename path, and restores memory and disk when post-commit persistence fails. It blocks further writes when safe restoration cannot be guaranteed.

## Executed verification

The review environment successfully executed:

- `node tests/core.test.js`
- `node tests/database-version-legacy-upgrade.test.js`
- `node tests/ui-regression.test.js`
- `node tests/integration.test.js`
- `node tests/latest-db-compatibility.test.js`

These covered policy, repository capability, services, transaction/persistence failure, schema compatibility, historical snapshots, RBAC/API integration, UI regression, and latest-database copy compatibility.

## Limitation

A fresh Linux bundle build was not verified because the supplied dependencies contained a Windows esbuild binary and the environment could not restore all Linux dependencies. No Windows executable build, DSM deployment, or physical mobile-device test was claimed.

## Interpretation

This source is evidence of end-to-end Client/Server architecture and controlled brownfield modernization. It is not evidence that the remaining large façade, centralized routing, frontend script size, memory-local sessions, or single-writer topology are final target-state decisions.
