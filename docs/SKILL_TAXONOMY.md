# CloudBox Skill taxonomy

The repository keeps the routing manifest flat. Classification is metadata for
navigation, ownership, and distillation; it does not replace routing cases.

## Three separate questions

1. **Capability layer** — what kind of engineering work does the Skill govern?
2. **Product-domain layer** — where is that capability applied?
3. **Distribution layer** — who may receive it? `core` is public/generalized;
   every other tier is private, split by content kind as of 2026-08-18:
   `private-meta` (self-referential skill/eval tooling), `private-game`,
   `private-equipment`, `private-operation`, and `private-art` (held or
   product-derived content, split by domain).

The distribution authority is only `config/skill-distribution.json`. Do not
copy distribution values into a second mutable ledger.

## Capability layer

| Category | Skills |
|---|---|
| `agent-dev` | `agent-development-process` |
| `architecture-dev` | `application-client-server-architecture`, `architecture-review`, `framework-design` |
| `integration-dev` | `project-management-sync` |
| `game-engine-dev` | `cloudbox-game-migration`, `cross-platform-engine-architecture`, `gameplay-core-modernization`, `legacy-game-product-archaeology` |
| `platform-native-dev` | `cross-platform-native-architecture`, `native-ios-game-rewrite` |
| `equipment-dev` | `cluster-tool-simulator-development`, `equipment-control-architecture`, `equipment-domain-modeling`, `semiconductor-equipment-domain-knowledge`, `tray-descum-simulator-development`, `wafer-bonder-debonder-development`, `wph-equipment-simulator-development` |
| `code-change-dev` | `code-review`, `codebase-architecture-discovery`, `safe-incremental-refactoring` |
| `quality-dev` | `game-asset-resolution-audit`, `game-quality-and-release-gates`, `software-quality-iso25010` |
| `governance-dev` | `coding-agent-project-governance`, `coding-agent-git-discipline`, `development-process-tailoring`, `document-governance`, `indie-game-product-evolution` |
| `skill-eval-dev` | `developing-eval`, `developing-skills`, `local-runtime-eval-debugging`, `runtime-evaluation-engineering`, `using-cloudbox-skills` |
| `learning-dev` | `teach-while-building` |

## Product-domain layer

The current product taxonomy is intentionally game-oriented:

- `game-dev`: legacy products, gameplay, state, levels, and modernization.
- `cloudbox-dev`: CloudBox-first runtime and migration.
- `ios-dev`: native iOS rewrite and platform compatibility.
- `art-dev`: asset source, resolution, redraw/upscale, and export.
- `product-dev`: scope, priority, economy, and product evolution.
- `marketing-dev`: store, IAP framing, promotion, and evidence-backed claims.
- `qa-dev`: characterization, replay, device/viewport, runtime, and release gates.

The four 7.6.22 additions are private `evolution-pack` Skills. Their
capability ownership is `game-engine-dev` for gameplay-core and CloudBox
migration, `platform-native-dev` for native iOS rewrite, and `quality-dev` for
game release gates.

Most general engineering Skills have no product domain yet; they remain
available as cross-domain capabilities. A Skill may have one primary
capability and multiple supporting capabilities or product domains.

## Future game-product distillation

Planned game Skills must first be candidates. They require owner/overlap review,
sanitization, RED evidence, same-case GREEN, adjacent regression, lifecycle
evidence, and private distribution review before becoming formal Skills.
