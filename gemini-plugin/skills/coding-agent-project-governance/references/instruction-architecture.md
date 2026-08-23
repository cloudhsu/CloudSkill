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

## Resolving Ambiguous Scope

When a plan instruction or a short user decision phrase admits more than
one reasonable scope reading (a refactor plan's wording could mean "add a
queue" or "also collapse two dispatch mechanisms into one"; "schedule it
for removal" could mean "hide the UI trigger" or "delete the whole
integration"), implement the narrowest reading that satisfies the literal,
stated acceptance criteria or request. Explicitly record the broader
reading(s) not implemented as a disclosed, named follow-up -- what it would
require and why it was not done now -- rather than guessing which reading
was intended and expanding scope unilaterally. When the narrower
implementation still leaves a coupling risk under the broader reading (two
mechanisms that could double-fire once a currently-unused hook is later
implemented), name that residual risk explicitly rather than letting the
narrow fix imply the whole concern is closed. Re-verify that the narrowly-
scoped fix did not silently leave the broader-reading trigger still
reachable (confirm a removed trigger is truly gone from the running build,
not just from the file most obviously associated with the decision).

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
