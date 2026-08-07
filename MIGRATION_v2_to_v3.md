# Migration from v2 to v3

## New Skills

- `application-client-server-architecture`
- `cross-platform-native-architecture`
- `coding-agent-project-governance`

## Behavioral Change

`agent-development-process` now explicitly means building an AI-agent product.

Repository rules for Codex or other coding agents now belong to `coding-agent-project-governance`.

## Profile Change

The architect identity is now explicitly broad:

- Full-stack and Client/Server.
- Cross-platform Qt IC tools.
- Cross-platform OpenGL 2D engine.
- Framework/platform architecture.
- Equipment/industrial architecture.

## Recommended Upgrade

Replace:

- global `AGENTS.md`
- user skill folders

Then restart Codex if skill discovery does not refresh.

Keep project-specific `AGENTS.md` files; they should override global guidance with repository facts.
