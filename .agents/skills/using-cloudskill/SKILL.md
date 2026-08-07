---
name: using-cloudskill
description: Use when starting a task that may require one or more CloudSkill skills, especially when routing, ordering, or composing process, domain, change, quality, and handoff skills is non-obvious.
---

# Using CloudSkill

## Purpose

Select only the skills that materially change how the task should be approached. Skills are operating instructions, not labels to mention after the work is already underway.

## Selection rule

Before substantial analysis, repository exploration, design, modification, or release work:

1. Identify the task's actual decision or failure boundary.
2. Check whether an installed skill has a concrete trigger for that boundary.
3. Load the smallest sufficient skill set.
4. Follow process/governance skills before domain and implementation skills.
5. Record executed checks and unresolved evidence truthfully.

Do not force a skill onto casual conversation, translation, trivial arithmetic, or a task whose answer is already fully determined by supplied text.

## Composition order

Use this order when multiple skills apply:

1. **Process and governance** — how work is controlled.
2. **Domain and architecture** — what system boundaries and semantics matter.
3. **Change and implementation** — how responsibility or code is changed safely.
4. **Quality and verification** — what evidence proves acceptance.
5. **Documentation and handoff** — how decisions, evidence, and remaining work are preserved.

Examples:

- Legacy Qt migration: `coding-agent-project-governance` -> `cross-platform-native-architecture` -> `safe-incremental-refactoring` -> `software-quality-iso25010`.
- Agent product: `agent-development-process`; add repository governance only when the repository operating model is also in scope.
- Versioned specification conflict: `document-governance`; add process tailoring only when release planning or lifecycle control is also requested.
- Equipment platform: `equipment-control-architecture` for sequence/topology/resource/recovery; add `equipment-domain-modeling` for state/command/capability/configuration; compose framework, refactoring, process, quality, or documentation skills only when those concerns are in scope.

## Routing safeguards

- An explicitly requested skill takes priority unless it conflicts with higher-level instructions.
- Do not load adjacent skills merely because they share vocabulary.
- Do not use an architecture skill for an isolated syntax defect.
- Do not use a repository-governance skill to design the AI-agent product itself.
- Do not use process tailoring to replace code review, ownership decisions, or technical verification.
- Do not route a component state/command question to distributed equipment architecture unless sequence, resource, interlock, topology, or recovery semantics are material.
- If no skill applies, proceed normally instead of inventing a match.

## Handoff

State which skills materially governed the work when that information helps review or continuation. Do not claim a skill's required tests, builds, device checks, deployments, or behavior evaluations were performed unless they actually ran.
