---
name: using-cloudskill
description: Use when a non-trivial engineering task may require one or more CloudBox skills, especially when the prompt is in Chinese, refers to prior corrections or conversations, spans architecture, equipment, code, process, quality, documents, or AI agents, or has ambiguous skill routing and composition.
---

# Using CloudBox

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

## Conversation-derived routing cues

Treat these as semantic cues, not keyword-only rules. Select a skill only when its decision boundary is material.

| Recurring user pressure | Primary route | Add only when needed |
|---|---|---|
| Duplicate command, stale response, NetworkStream/buffer suspicion, thread safety, callback order, timeout, late response | `code-review` | `equipment-domain-modeling` when the issue also requires an Actual/Desired/Pending or command-attempt model |
| Sequence versus Equipment Service, shared robot/aligner, pump/vent, interlock, material location, distributed IPC, reconnect, failover or HA | `equipment-control-architecture` | `semiconductor-equipment-domain-knowledge` for physical meaning; `architecture-review` for option comparison; `safe-incremental-refactoring` for migration |
| Valve/MFC/pump/gauge DTOs, typed commands, union-like payloads, Actual/Desired/Readback, stale snapshots, capability-driven UI | `equipment-domain-modeling` | `code-review` for a concrete defect; `framework-design` for a reusable product-line kernel |
| CEO/management versus engineer/training reports, one source split into multiple views, revision lineage, terminology normalization | `document-governance` | `software-quality-iso25010` for measurable metrics and release gates |
| Field failures or update success rates must be correlated to an actual software version; unversioned records must be isolated rather than silently included | `software-quality-iso25010` + `document-governance` | `development-process-tailoring` when the result drives release-train or corrective-action governance |
| Qt/MFC modernization, HID/USB, device hot-plug, firmware update, privileged Windows/macOS integration, installer or Qt version migration | `cross-platform-native-architecture` | `safe-incremental-refactoring`, `framework-design`, or `software-quality-iso25010` only for explicit migration/reuse/gate concerns |
| Small web/client-server system, API, SQLite, RBAC, concurrent orders, backup, NAS/container deployment | `application-client-server-architecture` | `safe-incremental-refactoring` only for an existing brownfield system |
| AI Agent task contract, tools, autonomy, memory, evaluation, guardrails, approval and operations | `agent-development-process` | `coding-agent-project-governance` only when repository operating rules are also requested |
| AGENTS.md, coding-agent worktrees, repository risk routing, release evidence, skill descriptions, Eval mining or plugin packaging | `coding-agent-project-governance` or `developing-skills` | Use `developing-skills` when the requested output changes CloudSkill routing or behavior |

## Historical-context discipline

When the user asks to optimize skills from prior conversations:

- Route to `developing-skills`.
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
