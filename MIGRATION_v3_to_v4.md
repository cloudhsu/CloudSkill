# Migration from v3 to v4

## New Skills

- `safe-incremental-refactoring`
- `cross-platform-engine-architecture`

## Routing Change

Use:

- `cross-platform-native-architecture` for Qt/native applications and platform integration.
- `cross-platform-engine-architecture` for Director/Scene, rendering loops, resources, actions/events, and engine platform adapters.

Use:

- `architecture-review` to evaluate architecture options.
- `safe-incremental-refactoring` to move an existing system safely.

## Profile Change

The full-stack and Client/Server experience is now source-verified rather than inferred from design documents.

The pack now records actual evidence from:

- Services and repositories.
- transaction/persistence recovery.
- schema migration.
- historical snapshots.
- RBAC.
- responsive UI.
- tests and release governance.

## Upgrade

Replace:

- Global `AGENTS.md`.
- Skill directories.
- Profile/evidence documents.

Restart the Codex session if skill discovery does not refresh.
