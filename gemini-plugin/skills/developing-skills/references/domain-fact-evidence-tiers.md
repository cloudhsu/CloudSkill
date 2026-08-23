# Domain-fact Evidence Tiers

When a Skill states an external domain fact, statistic, benchmark, or figure
as a rule (not CloudSkill's own methodology -- see `skill-authoring-sources.md`
for citing external skill-authoring influences, a different concern), tag it
with how authoritative and corroborated its source is. Three Skills
(`game-audio-design`, `game-narrative-design`, `game-marketing-and-monetization`)
each independently invented an evidence-tier vocabulary for this before this
file existed, with incompatible labels for the same underlying distinction.
Use this canonical scale instead of inventing a new one.

## The scale

- **Tier A -- official/institutional first-party source.** A platform
  vendor's own official guideline, primary documentation, or a regulatory/
  standard body's published requirement. State as a direct requirement in
  `SKILL.md`, no hedging needed.
- **Tier B -- single credible case study, survey, or specialist source.**
  One shipped-project postmortem, one industry survey (note its sampling
  method and any self-selection bias), or one named domain expert's
  documented account. Hedge in `SKILL.md`; detail the source and its limits
  in a `references/` file.
- **Tier C -- aggregated/secondhand estimate, or a single unaudited
  project's convention.** Industry figures aggregated without a named
  primary source, a secondhand analyst's write-up of someone else's work, or
  one third-party project's documented convention presented as a structural
  pattern rather than a statistical claim. Use for hypotheses and checklists,
  not as a proven rule; never state as an unhedged `SKILL.md` requirement.

## Composes with, does not replace, observed/inferred confidence

This tier is orthogonal to the `observed` / `inferred` / `unknown` evidence
classification already used throughout this Skill and repository-wide (see
Evolution workflow step 1 above): observed/inferred asks whether *this
Skill's own candidate/pressure* was directly witnessed or mined from
indirect signals; the tier above asks how authoritative *the external source
a stated domain fact cites* is. A rule can be `inferred` confidence and
Tier B at the same time -- crossing both axes, not merging them into one
label, is correct. `game-narrative-design/references/evidence-lineage.md`
is the reference example of doing this composition correctly (its per-rule
table crosses observed/inferred against a tier), and other Skills should
follow that shape rather than inventing a third, single-axis vocabulary.

## Rule for future edits

Before adding a new domain-fact rule to any Skill, classify its evidence
tier using the scale above and state that tier alongside the rule (in
`SKILL.md` if the rule is a direct requirement, in the relevant
`references/` file if it needs a fuller hedge). Do not add a specific
statistic to `SKILL.md` itself when its source flags the statistic as
needing periodic re-verification; keep that statistic in supporting notes
only. Do not upgrade a lower tier to read as settled fact merely because it
has been repeated in the Skill for a while.
