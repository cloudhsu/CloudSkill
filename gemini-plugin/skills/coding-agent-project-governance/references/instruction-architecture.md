# Instruction Architecture

## Global Guidance

Use for durable personal preferences and cross-repository working agreements.

Keep small because it is loaded broadly.

## Repository AGENTS.md

Use as the canonical cross-agent repository guidance for rules that apply to every task:

- Start files.
- Build/test commands.
- Source-of-truth directories.
- Non-negotiable invariants.
- safety/security.
- release expectations.
- evidence rules.

## Nested AGENTS.md or Override

Use near specialized code for:

- Module-specific commands.
- platform-specific constraints.
- sensitive subsystem rules.
- alternate test suites.

## Skills

Use for repeatable workflows such as:

- Release.
- migration.
- architecture review.
- client/server design.
- documentation.
- risk review.

## Reference Documents

Use for detailed domain and project knowledge that should be loaded only when relevant.

Avoid duplicating mutable facts across instruction layers.

## Claude Code adapter

When a repository supports both Codex and Claude Code, keep the full guidance in `AGENTS.md` and make `CLAUDE.md` a small adapter:

```text
@AGENTS.md
```

Add only Claude-specific behavior below the import. Do not maintain parallel copies of the same project rules.

## Skill source

Keep one canonical skill source. CloudSkill uses `.agents/skills/` and installs copies to `.claude/skills/`. Generated/installed copies must not become independently edited sources.
