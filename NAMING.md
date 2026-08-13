# CloudBox Naming Convention

Status: **decided, not yet executed.** This document defines the naming rule for the
CloudBox product family. It does not itself rename anything — `marketplace.json`,
`plugin.json`, this repository's own name, and every project's `settings.json`
`enabledPlugins` entries still say `cloudbox`/`cloudbox-marketplace` today. Executing
the rename is a separate, explicitly-confirmed step (see "Migration checklist" below).

## Why this exists

"CloudBox" is both the brand for this skill/agent framework (marketplace owner name,
plugin id, versioned since ~v6.x) and, unrelated, the name of an older 2D game engine
product the brand's owner also built. The collision is real, not hypothetical — see the
2026-08-13 session that prompted this document. Rather than resolve it as a one-off
rename, this defines a rule general enough that new products and agent roles never
recreate the same ambiguity.

## The pattern

```
cloudbox-<domain>[-<role-or-subtype>]
```

All lowercase, hyphen-separated. No version numbers in the name — versioning lives in
each product's own `VERSION`/`CHANGELOG.md`.

## Domain words (the part that should almost never change)

Everything new gets routed to exactly one domain by asking these questions **in
order** and stopping at the first "yes":

| # | Question | Domain | What lives here |
|---|---|---|---|
| 1 | Does it have a persona, job title, or decision authority? | `cloudbox-agent-<role>` | AI team members |
| 2 | Does it ship as, or become part of, a runnable end product for players/users? | `cloudbox-engine[-<subtype>]` | The engine and its shippable derivatives |
| 3 | Is it a body of instructions/knowledge an agent reads, not a running program? | `cloudbox-skills[-<discipline>]` | The skill library |
| 4 | Is it developer/operator tooling with no persona that doesn't ship? | `cloudbox-tools[-<name>]` | Internal scripts/CLIs/CI |
| — | None of the above | no domain suffix | Brand-level meta (marketplace manifest, org-wide docs) |

## Adding a new domain word (rare — do this deliberately)

Only introduce a fifth domain when a candidate satisfies **both**:
1. Its consumer/audience differs from all four domains above.
2. It is expected to grow its own family of variants (a category, not a one-off).

Otherwise it is a `-<subtype>` suffix on an existing domain, not a new domain.

## Role/subtype suffixes (cheap — add anytime)

- `cloudbox-agent-*`: short, single-word job titles where possible (`core`, `dev`,
  `producer`, `art`, `skill-builder`).
- `cloudbox-engine-*`: the main repo is simply `cloudbox-engine`, no suffix — suffixes
  (`editor`, `web-runtime`, `asset-pipeline`) are added only when the family actually
  grows, so the primary repo never needs a second rename.
- `cloudbox-skills-*`: stays one repo (`cloudbox-skills`) by default; split by
  discipline suffix only if it becomes too large to review or ships independently.
- `cloudbox-tools-*`: one suffix per independent utility.

## Current mapping

| Thing | Name |
|---|---|
| This repository (skill/agent framework, currently `cloudskill` / plugin id `cloudbox`) | `cloudbox-skills` |
| The 2D game engine repository | `cloudbox-engine` |
| Marketplace | `cloudbox-marketplace` (unchanged; owner name updates from `CloudBox` to reflect the brand, not a product) |
| Future: orchestrator agent | `cloudbox-agent-core` |
| Future: programmer agent | `cloudbox-agent-dev` |
| Future: skill-authoring agent | `cloudbox-agent-skill-builder` — wraps this repo's existing capture / optimize / create-skill capability (`developing-skills` and its conversation-mining, RED/GREEN evidence, and lifecycle workflow) as a standing, self-optimizing closed loop, rather than a one-off workflow invoked manually |
| Future: game producer agent | `cloudbox-agent-producer` |
| Future: art agent | `cloudbox-agent-art` |

## Migration checklist (for when the rename is actually executed — not done yet)

- [ ] `.claude-plugin/marketplace.json`: `name` (`cloudbox-marketplace` — likely
      unchanged) and `owner.name`.
- [ ] `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`: plugin `name`.
- [ ] This repository's own name/remote (`cloudskill` → decide whether the directory
      and GitHub repo also rename to match `cloudbox-skills`, or only the plugin id
      changes).
- [ ] Every project's `settings.json` `enabledPlugins` key
      (`"cloudbox@cloudbox-marketplace"` → `"cloudbox-skills@cloudbox-marketplace"`).
- [ ] Skill invocation prefixes referenced in docs/memory (`cloudbox:developing-skills`
      → new prefix).
- [ ] Internal worktree/branch naming conventions that currently embed `cloudbox-X.Y`
      as this product's own version scheme (e.g. `cloudbox-6.2-adaptive-lifecycle`) —
      decide whether these keep meaning "this repo's version" (fine, now unambiguous
      once the repo is `cloudbox-skills`) or need their own prefix.
- [ ] `CHANGELOG.md` / release notes: record the rename itself as a versioned change,
      not a silent edit.
- [ ] The separate `cloudbox` game-engine repository: its own rename to
      `cloudbox-engine` is tracked in that repository, not here.

Do not execute this checklist without explicit confirmation — it touches published
plugin identity and every consuming project's configuration.
