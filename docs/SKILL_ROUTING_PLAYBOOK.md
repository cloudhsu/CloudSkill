# CloudBox Skill Routing Playbook

`docs/SKILL_TAXONOMY.md` answers "what is this Skill?" This document answers
a different question: **given a common software-engineering situation, which
Skill(s) actually fire?** It is a practical routing reference, not a second
classification system — when in doubt, the taxonomy and `SKILL_MANIFEST.json`
descriptions are authoritative; this document explains how they compose in
practice, and states plainly where the current Skill set does not yet cover
a situation.

## Composition order (from `AGENTS.md`, restated here for quick reference)

1. Process and governance
2. Domain and architecture
3. Change and implementation
4. Quality and verification
5. Documentation and handoff

Not every situation pulls from every layer. The tables below name the Skill
that usually anchors layer 2 (domain/architecture) or layer 3
(change/implementation) for each situation, then list what commonly joins it.

## Scenario × domain matrix

Four product domains: equipment software, game, website/web-service, and — a
domain the Skill catalog supports but that a quick domain list easily
forgets — an AI-agent product itself.

| Scenario | Equipment software | Game | Website / web service | AI-agent product |
|---|---|---|---|---|
| **Greenfield / new software** | `equipment-control-architecture` + `equipment-domain-modeling` (architecture and per-device modeling are used together, not as alternatives — see below) | `cross-platform-engine-architecture` | `application-client-server-architecture` | `agent-development-process` |
| **Add a feature to existing software** | same domain skill, + `framework-design` if the feature needs a real extension point, + `safe-incremental-refactoring` if existing responsibility must move first | domain skill, or `indie-game-product-evolution` first if the feature is really a product-scope/monetization decision in disguise | domain skill + `framework-design` when the feature adds a new module boundary | `agent-development-process` (tool/memory/guardrail boundaries change) |
| **Bug fix** | `code-review` (its own description explicitly names device-control/industrial code) | `code-review` | `code-review` | `code-review` |
| **Refactor (same platform, responsibility reshaping)** | `safe-incremental-refactoring`, or `codebase-architecture-discovery` first if the slice isn't known yet | `gameplay-core-modernization` (the game-specialized form of the same skill — extracts a platform-independent core) | `safe-incremental-refactoring`, or `codebase-architecture-discovery` first if the slice isn't known yet | `safe-incremental-refactoring`, or `codebase-architecture-discovery` first if the slice isn't known yet |
| **Migrate / port to a new platform or runtime** | **no dedicated Skill** — assemble `equipment-control-architecture` + `safe-incremental-refactoring` | `cloudbox-game-migration` or `native-ios-game-rewrite` (two dedicated Skills, split by target) | **no dedicated Skill** — assemble `application-client-server-architecture` + `safe-incremental-refactoring` | **no dedicated Skill** |
| **Reconstruct a legacy product with no/weak documentation** | **no dedicated Skill** — assemble `code-review` + `architecture-review` + `document-governance` | `legacy-game-product-archaeology` (dedicated evidence-ledger/characterization methodology) | **no dedicated Skill** | **no dedicated Skill** |
| **Release-readiness / release gates** | **no dedicated Skill** — assemble `software-quality-iso25010` + `development-process-tailoring` | `game-quality-and-release-gates` | **no dedicated Skill** | **no dedicated Skill** |

Bold "no dedicated Skill" cells are real, current gaps, not omissions in this
table — see "Known structural gaps" below.

### Performance and security are not their own row

They are variants of bug fix / refactor with a different risk and process
shape, not a different domain-architecture concern:

- **Performance regression**: usually `code-review` (find the real cause)
  + `architecture-review` (if the fix is architectural, e.g. a wrong
  ownership boundary causing repeated work) + `safe-incremental-refactoring`
  if the fix reshapes responsibility rather than just tightening a loop.
- **Security fix**: `code-review` first, `development-process-tailoring` if
  it must ship faster than the normal release train, and
  `document-governance` if a compliance or audit document must also be
  updated. No CloudBox Skill currently owns security-specific analysis
  (threat modeling, vulnerability classification) as its primary capability
  — this is itself worth naming as a gap if security work becomes frequent.

## Skills that trigger on a different axis (who's doing the work, how it's tracked), not on domain or scenario

These do not belong in the matrix above because they answer "how is this
project being run," not "what kind of software change is this":

| Skill | Fires when |
|---|---|
| `coding-agent-project-governance` | Multiple AI coding agents (or agents + humans) share a repository and need risk routing, worktree rules, or ownership boundaries — regardless of what the underlying software is. |
| `project-management-sync` | Work needs to reconcile with an external backlog/tracker (Vikunja, OpenProject, Redmine). |
| `document-governance` | Multiple documents disagree on authority, version lineage, or source of truth — can co-occur with any scenario above. |
| `teach-while-building` | The user wants to build durable understanding as a side effect of the same work, not a separate course. |
| `using-cloudbox-skills` | The right Skill (or combination) from the tables above is not obvious, or several apply and the smallest sufficient set needs deciding. |

## The `skill-eval-dev` cluster is for building CloudBox Skills, not for building your software

`developing-skills`, `developing-eval`, `runtime-evaluation-engineering`,
`local-runtime-eval-debugging` govern authoring, evaluating, and releasing
CloudBox Skills themselves (this document and the RED/GREEN evidence in
`docs/releases/` are examples of that work). They never fire because of what
domain or scenario your equipment/game/website/agent project is in — only
because you are changing the Skill catalog. Easy to miss precisely because
their names don't signal that boundary; stated explicitly here so this
playbook doesn't accidentally suggest routing to them for ordinary feature
work.

## Why the equipment-domain cell lists two Skills together, not a choice

`equipment-control-architecture` (sequence/topology/resource/recovery
architecture) and `equipment-domain-modeling` (per-device state/command/
capability modeling: valves, MFCs, gauges, robots) are almost always used
together on greenfield equipment work — one without the other produces
either a control flow with no real device model underneath it, or a set of
well-modeled devices with no sequencing/recovery architecture connecting
them. `semiconductor-equipment-domain-knowledge` is a third, different kind
of thing — physical/process *knowledge* (what EFEM, loadlock, or plasma
readiness actually mean), not a software architecture decision — and joins
the other two only when the equipment is genuinely semiconductor-domain, not
for equipment software in general.

## The noun/verb pattern (useful heuristic, not a formal rule)

Some Skills are domain **nouns** — they own a specific kind of system and do
not overlap across domains by design: `equipment-control-architecture`,
`cross-platform-engine-architecture`, `application-client-server-architecture`,
`agent-development-process`. Zero overlap between these on greenfield work is
expected and healthy.

Other Skills are cross-domain **verbs** — the same skill fires regardless of
domain because the underlying engineering action is the same regardless of
what system it's performed on: `code-review` (bug fix, every domain),
`safe-incremental-refactoring` (refactor, every domain except the
game-specialized `gameplay-core-modernization`), `architecture-review`,
`software-quality-iso25010`, `codebase-architecture-discovery` (discover
what an unfamiliar or suspect codebase area actually contains before any
domain-specific refactor Skill has a defined slice to work with — every
domain, no game-specialized form exists yet). Overlap between verb-shaped Skills, or between a
verb-shaped Skill and a noun-shaped one substituting for it, is not
automatically a problem.

This distinction is why a measured RED/GREEN overlap between two Skills
should be read differently depending on which kind they are — see
`docs/releases/7.6.24-pre-release-evidence.md`'s
`legacy-game-product-archaeology` vs. `gameplay-core-modernization` finding:
both are noun-shaped (own a specific reconstruction/extraction
responsibility), so the measured near-total output overlap on one archetype
was treated as a real question worth a deliberate decision, not waved off as
expected verb-style redundancy. The decision (2026-08-17, recorded in that
same evidence file and in `legacy-game-product-archaeology`'s
`lifecycle.json`): accept the overlap as acceptable redundancy rather than
sharpen either Skill's scope, because the two Skills are sequential
collaborators by design and the measured gap was narrow (one rubric
criterion, one archetype). The noun/verb distinction is still what makes a
future overlap between two noun-shaped Skills worth this same deliberate
check — it just does not always end in narrowing scope.

## Known structural gaps (as of 7.6.24)

Restated plainly from the matrix and `docs/SKILL_TAXONOMY.md`'s own
admission ("the current product taxonomy is intentionally game-oriented"):

1. **No legacy-archaeology Skill outside games.** Equipment software or a
   website handed over with weak/no documentation has no dedicated
   evidence-ledger/characterization methodology to reach for — only the
   generic `code-review` + `architecture-review` + `document-governance`
   combination, which is a materially thinner toolkit than
   `legacy-game-product-archaeology` gives games.
2. **No release-readiness Skill outside games.** Equipment and website
   release gates have to be assembled ad hoc from `software-quality-iso25010`
   + `development-process-tailoring` instead of a purpose-built checklist
   Skill like `game-quality-and-release-gates`.
3. **No dedicated migration/porting Skill outside games.** Games get two
   (`cloudbox-game-migration`, `native-ios-game-rewrite`); equipment and
   website migrations fall back to the generic domain-architecture Skill
   plus `safe-incremental-refactoring`.
4. **The product-domain layer (`config/skill-domain-catalog.json`) has zero
   entries for equipment or website.** All product-domain investment
   (`game-dev`/`cloudbox-dev`/`ios-dev`/`art-dev`/`product-dev`/
   `marketing-dev`/`qa-dev`, and the RED/GREEN evidence built up around
   them) has gone into games. Equipment software only has a *capability*
   category (`equipment-dev`); website has no dedicated category at all,
   generic or not, beyond `architecture-dev`.
5. **No Skill owns security analysis as a primary capability** — noted above
   under performance/security; only relevant if security work becomes a
   recurring pattern rather than an occasional `code-review` case.

None of this is a defect to silently fix — it is a record of where
deliberate investment has (and has not) happened, useful for deciding what
to distil next.
