---
name: developing-skills
description: Use when creating, editing, splitting, merging, evaluating, or releasing CloudSkill skills. For mining prior interactions or user corrections into evidence, use developing-eval instead.
---

# Developing CloudSkill Skills

## Core contract

A Skill change succeeds only when it improves repeatable routing or behavior.
More prose, valid Markdown, or a generated package is not evidence of improvement.

Preserve privacy, evidence lineage, the authoritative owner, RED evidence before
behavior change, truthful execution status, and the smallest responsible change.
Never store raw transcripts or claim access, tests, installation, publication,
or model execution that did not occur.

## Load conditional detail

Read only the references required by the active workflow:

- `references/behavior-driven-skill-development.md` for RED/GREEN records,
  evaluation layers, regressions, and result states.
- `references/skill-authoring-sources.md` for external influences, adaptation,
  citations, and third-party project evidence.
- `references/skill-lifecycle-standard.md` before creating or changing a stage,
  preparing release evidence, deprecating, or replacing a Skill. The shared
  lifecycle is `draft -> experimental -> active -> stable -> deprecated`.

Do not load every reference by default. Keep detailed mechanics in one
authoritative reference rather than copying mutable checklists into this file.

Use the matching assets and repository commands named by those references.
Create new Skills with `scripts/manage_skill.py new`; before commit refresh and
audit lifecycle evidence, then run the complete repository checks.

Before finalizing a new skill id, plugin identifier, or other product-facing name,
check whether it collides with an unrelated product or identity already in scope
(a different codebase, plugin, or project the same user works on) — a same-session
collision is easy to miss until many files already reference the name. Surface a
collision immediately and drive an explicit disambiguation decision before
propagating the name across files, rather than discovering it after adoption and
paying for a full rename later.

## Conversation mining is a different skill

Turning prior interactions, user corrections, or project history into
sanitized Eval evidence (including the `整理成正向案例` / `整理成負向案例` /
`從專案提煉優化案例` triggers, the private Eval Inbox, and disconnected
export/import) is owned by `developing-eval`, not this skill. That skill's
output -- a reviewable, sanitized candidate -- is an input to the Evolution
workflow below, same as any other RED evidence source.

## Evolution workflow

### 1. Inventory and classify evidence

List only sources actually available. Mark unavailable history and distinguish
observed, inferred, and unknown evidence. Classify the pressure as routing,
missing behavior/artifact, prohibited action, unsupported claim, duplication,
wrong ownership, or a mechanical rule better enforced by tooling.

Sanitize before synthesis. Generalize organizations, people, projects,
products, equipment, sites, accounts, addresses, paths, URLs, schedules,
recipes, safety limits, credentials, and other identifying details.

### 2. Locate the authoritative owner

Search existing descriptions, Skills, references, assets, routing cases, and
repository rules. Expand an owner when trigger, audience, and lifecycle match.
Split only when the work is independently routable. Keep project conventions in
repository instructions and enforce mechanical consistency in scripts or CI.

For multiple candidates, deterministically filter byte-identical or equivalent
records before model synthesis. Cluster common pressure and do not modify every
Skill merely because several domains appeared in the source.

### 3. Establish RED evidence

Create or select the smallest repeatable routing, recognition, application,
counterexample, discipline, or reference case. Run current behavior without the
proposed instruction and record the exact omission. If no observable failure
exists, use `NO_CHANGE_JUSTIFIED`; do not invent a fix.

Type every RED and GREEN by evidence layer: case/contract, deterministic
implementation, Skill/agent behavior, adjacent composition, runtime/provider,
or release/field effectiveness. A RED authorizes correction only at its failed
layer and authoritative owner; implementation RED cannot substitute for Skill
behavior RED. Re-run the same case at the same layer for GREEN, then add only
the adjacent and higher-layer evidence required by lifecycle stage and risk.
Never promote a lower-layer GREEN into a higher-layer claim. A RED note
itself starts flat/short and escalates to the formal JSON case shape only
once it needs to be machine-checked, not by default (see
`../safe-incremental-refactoring/references/evidence-checklist.md`'s
"Escalating Evidence Shape as Complexity Grows").

### 4. Define and implement the minimum contract

Specify trigger/non-trigger conditions, required and forbidden behavior,
artifact, evidence, stop conditions, companions, and the baseline failure.

Prefer, in order: description correction; routing/counterexample case; one
decision rule; one safeguard or stop condition; a supporting reference/asset;
then a new Skill only when independent routing is proved. Keep decision flow in
`SKILL.md`; keep conditional detail and reusable mechanics in references,
scripts, or assets.

For an authoritative-contract pattern, match the closest existing instance's
positive propagation and negative drift-injection tests, not only its layout.

### 5. Verify GREEN and adjacent behavior

Re-run the same cases and verify routing, behavior, artifacts, forbidden-action
absence, evidence truth, and reasonable context cost. Regress adjacent owners,
negative controls, simple tasks, and multi-Skill composition. Close only
demonstrated loopholes.

Use exact source/diff hashes for review. Reuse evidence only when scope, source,
contract, rubric, environment, and risk are equivalent. Stop additional model
calls after a blocking finding until it is corrected. Do not repeat unchanged
waiting status.

### 6. Report execution truthfully and control release

Report accessible evidence, unavailable sources, owner/overlap decision,
sanitization/deduplication, contract, RED result, minimal change, GREEN and
adjacent regression, structural/install checks, delivery form, release status,
and remaining limitations.

When reporting what changed in a Skill release, or when asked what a
Skill optimization changed, use a table with one row per case/rule added
(id, owner Skill, one-line summary of the pressure it closes, RED
evidence layer) rather than prose paragraphs — prose buries which
specific case closed which specific gap, and makes it hard to tell one
release's changes from another's at a glance.

Before releasing any change that touches a `SKILL.md`, run
`scripts/validate_skill_context_budget.py`. It enforces a hard per-skill byte
budget (default 10,500 bytes; a short, dated list of frozen ceilings exists
for skills that were already over budget when this check was introduced --
those get zero further growth room, not a standing exemption). A failure is
not something to note and defer: consolidate repeated rules into fewer,
more general statements, or move conditional detail into `references/`,
before release. Never raise the default budget or a grandfathered ceiling to
make a failing skill pass -- shrink the skill instead.

When any structural validator (context budget, portability, description
hygiene) fails, read its actual detection source before responding -- the
exact string or pattern it matched, not just the failure message. Fix a
genuine false positive by rewording the flagged prose so it no longer
matches, then re-run the same validator to confirm; do not "fix" a false
positive by reclassifying the skill into a stricter tier or otherwise
changing something the validator did not actually flag.

A local validator pass is not release evidence by itself when the repository
has CI. After pushing, check the actual CI run for that commit (e.g. `gh run
list` / `gh run view`) before calling the release done -- do not infer CI
result from the local run alone. A CI-configured check that was never
observed to run is `NOT RUN`, not `PASS`, regardless of local results.

Before any stage or release decision, follow
`references/skill-lifecycle-standard.md`. Distinguish structural validation,
semantic or provider-backed execution, repository writes, installation,
host/plugin reload, push, merge, tag, and Release. Record each as PASS, FAIL,
BLOCKED, NOT RUN, or MANUAL REQUIRED as applicable.

## Stop conditions

Stop or route to manual review when privacy cannot be established, authority is
missing, evidence cannot reproduce the claimed failure, a reference split hides
a mandatory safeguard, or recovery/rollback is undefined. Do not trade required
behavior for a smaller context file.

When optimizing Skills, preserve priorities in this order: lifecycle and its
dynamic feedback loop, then evidence and verification, then token/context cost.
