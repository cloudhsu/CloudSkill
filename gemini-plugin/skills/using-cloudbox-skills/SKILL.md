---
name: using-cloudbox-skills
description: Use when a non-trivial engineering task may require one or more CloudBox skills, especially when it refers to prior corrections or interactions, spans architecture, equipment, code, process, quality, documents, or AI agents, or has ambiguous routing and skill composition.
---

# Using CloudBox

## Purpose

Select only the skills that materially change how the task should be approached. Skills are operating instructions, not labels to mention after the work is already underway.

## Selection rule

Before substantial analysis, repository exploration, design, modification, or release work:

1. Identify the task's actual decision or failure boundary.
2. Check whether an installed skill has a concrete trigger for that boundary.
3. Load the smallest sufficient skill set.
4. Follow process/governance skills before domain knowledge, architecture, implementation, quality, and handoff skills when that order is materially required.
5. Record executed checks and unresolved evidence truthfully.

Do not force a skill onto casual conversation, translation, rewriting, trivial arithmetic, inspection-only requests, or a task whose answer is already fully determined by supplied text. Prompt language alone is never a routing condition.

A request's small or mechanical surface phrasing — "just verify," "just add a few rows," "just confirm this edit is fine" — is not by itself evidence that no skill applies. Judge routing by whether the concrete action matches a risk boundary an installed skill's own content already documents (a build stage that alone cannot validate the changed artifact, a capture action that can expose unrelated windows, an addition that can collide with an existing identifier), not by how procedurally small the request sounds. A confirmation request is only genuinely out of scope when every fact the confirmation needs is already supplied, not merely when the requested action is short.

A settled design or scope decision is not the same as an answer already fully determined by supplied text. When the remaining work still carries real behavior, contract, transaction, or state-preservation risk — for example, an already-approved move of a responsibility across a service boundary — the execution itself is exactly what an execution-shaped skill such as `safe-incremental-refactoring` governs, not evidence that no skill applies.

## Routing decision contract

When the task asks for an explicit routing result, use this structure:

```json
{
  "primary_skill": "skill-id-or-null",
  "supporting_skills": [],
  "rejected_skills": [],
  "execution_order": [],
  "reason": "",
  "confidence": "high | medium | low"
}
```

Interpret the fields as follows:

- `primary_skill`: the skill that owns the requested deliverable or final decision.
- `supporting_skills`: additional skills that materially change the work; do not add adjacent skills for vocabulary overlap.
- `rejected_skills`: plausible alternatives that were intentionally excluded.
- `execution_order`: the order in which skill instructions should govern the work. The primary owner does not have to execute first.
- `reason`: the concrete decision or failure boundary, not a keyword explanation.
- `confidence`: confidence in routing based on available evidence.

`using-cloudbox-skills` is the router. Never list it as `primary_skill` or in `supporting_skills` — the routing decision is this skill's own output, not one of its entries. When the requested deliverable is itself a change to routing policy, skill composition, or a skill's own content, the owner is `developing-skills`, not this router.

## Composition order

Use this default order when multiple skills apply, then adjust it when evidence or analysis dependencies require a different sequence:

1. **Process and governance** — how work is controlled.
2. **Domain knowledge** — what the physical or business concepts mean.
3. **Domain architecture and modeling** — what boundaries, state, and contracts matter.
4. **Change and implementation** — how responsibility or code is changed safely.
5. **Quality and verification** — what evidence proves acceptance.
6. **Documentation and handoff** — how decisions, evidence, and remaining work are preserved.

Examples:

- Legacy Qt migration: `coding-agent-project-governance` -> `cross-platform-native-architecture` -> `safe-incremental-refactoring` -> `software-quality-iso25010`.
- Agent product: `agent-development-process`; add repository governance only when the repository operating model is also in scope.
- Versioned specification conflict: `document-governance`; add process tailoring only when release planning or lifecycle control is also requested.
- Equipment terminology or PVD/vacuum explanation: `semiconductor-equipment-domain-knowledge` only, unless design or implementation is also requested.
- Pump/vent, material transfer, readiness, or PVD execution architecture: `semiconductor-equipment-domain-knowledge` -> `equipment-control-architecture`.
- MFC/gauge/valve state and command model: `semiconductor-equipment-domain-knowledge` when physical semantics need clarification, then `equipment-domain-modeling`.

## Conversation-derived routing cues

Read `references/conversation-routing-map.md` when recurring engineering scenarios, prior corrections, language-neutral counterexamples, or primary-owner versus execution-order distinctions are relevant.

Treat examples as semantic pressure tests, not keyword rules. Keep detailed cases in references and Evals rather than expanding this router indefinitely.

## Historical-context discipline

When the user asks to optimize skills from prior conversations:

- Route the downstream work to `developing-skills`.
- Use only conversation context, memory, uploaded exports, or connected sources that are actually available.
- State unavailable history explicitly; never imply complete account-wide transcript access.
- Generalize reusable engineering pressure and remove company, customer, project, person, path, URL, machine, recipe, schedule, and safety-limit identifiers.
- Prefer a small owner-specific change and regression cases over rewriting every skill.
- If repository write access is unavailable, produce a reviewable overlay or patch and report the limitation truthfully.

## Routing safeguards

- An explicitly requested skill takes priority unless it conflicts with higher-level instructions.
- Do not load adjacent skills merely because they share vocabulary.
- Do not use an architecture skill for an isolated terminology or process-principle question.
- Do not use domain knowledge alone when the task requires state ownership, event lifecycle, resource arbitration, or recovery design.
- Do not use equipment architecture for a component DTO question unless sequence, physical readiness, resource, interlock, topology, or recovery semantics are material.
- Do not use equipment-domain modeling to invent process recipes or safe hardware limits.
- Do not use a repository-governance skill to design the AI-agent product itself.
- Do not use process tailoring to replace code review, ownership decisions, or technical verification.
- Do not infer routing from Chinese, English, or mixed-language wording; route by decision boundary.
- If no skill applies, proceed normally instead of inventing a match.

## Plugin coexistence

Read `references/plugin-coexistence.md` when CloudBox is installed with Superpowers or another workflow plugin.

- Use only one top-level routing or orchestration skill for a task.
- An explicit CloudBox-only request excludes other optional workflow plugins from the current task, but does not prove their host setting was changed.
- Do not modify another plugin's enabled state unless the user explicitly requests that host-level action and the result can be verified.
- In hybrid mode, assign generic implementation workflow to the external plugin and domain, architecture, modeling, migration, quality, or evidence decisions to CloudBox.
- Do not enable both the CloudBox plugin and a standalone copy of the same CloudBox skills in one host.

## Handoff

State which skills materially governed the work when that information helps review or continuation. Do not claim a skill's required tests, builds, device checks, deployments, process verification, or behavior evaluations were performed unless they actually ran.
