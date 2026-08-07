---
name: using-cloudskill
description: Use when starting a task that may require one or more CloudSkill skills, especially when routing, ordering, or composing process, domain-knowledge, architecture, change, quality, and handoff skills is non-obvious.
---

# Using CloudSkill

## Purpose

Select only the skills that materially change how the task should be approached. Skills are operating instructions, not labels to mention after the work is already underway.

## Selection rule

Before substantial analysis, repository exploration, design, modification, or release work:

1. Identify the task's actual decision or failure boundary.
2. Check whether an installed skill has a concrete trigger for that boundary.
3. Load the smallest sufficient skill set.
4. Follow process/governance skills before domain knowledge, architecture, implementation, quality, and handoff skills.
5. Record executed checks and unresolved evidence truthfully.

Do not force a skill onto casual conversation, translation, trivial arithmetic, or a task whose answer is already fully determined by supplied text.

## Composition order

Use this order when multiple skills apply:

1. **Process and governance** — how work is controlled.
2. **Domain knowledge** — what the physical/business concepts mean.
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
- Equipment platform migration: add `safe-incremental-refactoring`, process, quality, or documentation skills only when those concerns are explicitly in scope.

## Routing safeguards

- An explicitly requested skill takes priority unless it conflicts with higher-level instructions.
- Do not load adjacent skills merely because they share vocabulary.
- Do not use an architecture skill for an isolated terminology or process-principle question.
- Do not use domain knowledge alone when the task requires state ownership, event lifecycle, resource arbitration, or recovery design.
- Do not use equipment architecture for a component DTO question unless sequence, physical readiness, resource, interlock, topology, or recovery semantics are material.
- Do not use equipment-domain modeling to invent process recipes or safe hardware limits.
- Do not use a repository-governance skill to design the AI-agent product itself.
- Do not use process tailoring to replace code review, ownership decisions, or technical verification.
- If no skill applies, proceed normally instead of inventing a match.

## Handoff

State which skills materially governed the work when that information helps review or continuation. Do not claim a skill's required tests, builds, device checks, deployments, process verification, or behavior evaluations were performed unless they actually ran.
