# Agent-Governance Section Template

A structural checklist, not a shared content core. This came out of a real
architecture discussion (2026-08-23): `coding-agent-project-governance`
governs coding-agent behavior; `document-governance`'s product-direction
role and `game-art-pipeline`'s Draft Governance step each govern agent
behavior for a different domain (product decisions, art production). The
temptation is to extract one shared "agent governance core" all three
compose from -- resist it. The user's correct pushback: product, art, and
code risk taxonomies, evidence definitions, and stop-conditions are
genuinely different by domain, not accidental duplication to be collapsed.

## What is shared: the shape, never the content

When a domain skill needs its own agent-governance section, check it
covers these four slots. What goes IN each slot is expected and correct to
differ by domain -- these are prompts to self-check completeness, not text
to copy.

1. **Domain-specific risk taxonomy.** What actually goes wrong here, and
   what makes one instance worse than another? Not a generic
   "low/medium/high" label -- the real consequence categories for this
   domain.
   - Coding: system breakage, security, data loss, backward compatibility,
     production blast radius.
   - Art: IP/licensing exposure, brand-consistency drift, generation-cost
     waste, provenance/traceability loss.
   - Product: user-facing scope creep, external stakeholder commitment,
     irreversible business/legal decisions.
   These are not the same list wearing different domain names -- they do
   not map onto each other one-to-one.

2. **Domain-specific evidence definition.** What counts as proof this
   domain's work actually happened and is correct? A code change's
   evidence (a diff, a passing test, a CI run) is not interchangeable with
   an art candidate's evidence (a rendered image, a provenance record, a
   style-authority citation) or a product decision's evidence (a decision
   record, a stakeholder sign-off, a stated stop condition).

3. **A stop/escalation condition.** What does "stuck" look like in this
   domain, and what is the bounded response before escalating to a human?
   A repeated git-push auth failure is not the same shape of "stuck" as
   repeated aesthetic rejection of generated art, which is not the same
   shape as repeated stakeholder disagreement on product scope -- but
   every domain needs an answer to "when do we stop retrying and ask."

4. **A release-safety check.** What has to be true before this domain's
   work is treated as done/shippable/final, as opposed to draft/candidate?

## What this is not

Not a runtime-composed shared reference -- a domain skill's governance
section does not need to cite this file at runtime, and existing sections
(`document-governance`'s product-direction role,
`game-art-pipeline`'s Draft Governance step) are not being retrofitted to
point here. This is an authoring-time checklist: when writing a new
domain's agent-governance section, or materially revising an existing one,
self-check it against these four slots before treating it as complete.
