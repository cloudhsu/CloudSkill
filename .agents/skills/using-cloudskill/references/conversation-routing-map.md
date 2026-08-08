# Conversation-derived routing map

Use this reference for recurring engineering scenarios and routing counterexamples. These examples are semantic pressure tests, not keyword-only triggers.

## Routing contract

- `primary_skill` owns the requested deliverable or final decision.
- `supporting_skills` materially change the work.
- `execution_order` records analysis or governance order and may begin with a supporting skill.
- `using-cloudskill` performs routing and is not normally included in the downstream skill list.
- Prompt language is not a routing condition.

## Reusable routing cues

| Recurring engineering pressure | Primary route | Add only when needed |
|---|---|---|
| Duplicate command, stale response, NetworkStream/buffer suspicion, thread safety, callback order, timeout, late response | `code-review` | `equipment-domain-modeling` when the requested correction changes Actual/Desired/Pending or command-attempt semantics |
| Sequence versus Equipment Service, shared robot/aligner, pump/vent, interlock, material location, distributed IPC, reconnect, failover or HA | `equipment-control-architecture` | Add `semiconductor-equipment-domain-knowledge` only when physical process meaning, vacuum/readiness, or component completion evidence must be clarified; do not add it for a generic ownership/recovery topology question. Add `architecture-review` for option comparison or `safe-incremental-refactoring` for migration. |
| Valve/MFC/pump/gauge DTOs, typed commands, union-like payloads, Actual/Desired/Readback, stale snapshots, capability-driven UI | `equipment-domain-modeling` | Add `equipment-control-architecture` when physical completion, timeout/late completion, interlock, sequence/service boundary, or recovery ownership crosses the component model. Add `code-review` for a concrete defect or `framework-design` for a reusable product-line kernel. |
| CEO/management versus engineer/training reports, one source split into multiple views, revision lineage, terminology normalization | `document-governance` | `software-quality-iso25010` for measurable populations, metrics, exclusions, and release gates |
| Field failures or update success rates must correlate to an actual software version; unversioned records remain visible but outside version metrics | `document-governance` | `software-quality-iso25010` to define denominator, exclusions, confidence, and quality interpretation; run quality analysis before document transformation when the metric definition is unresolved |
| Qt/MFC modernization, HID/USB, device hot-plug, firmware update, privileged Windows/macOS integration, installer or Qt version migration | `cross-platform-native-architecture` | `safe-incremental-refactoring`, `framework-design`, or `software-quality-iso25010` only for explicit migration, reuse, or gate concerns |
| Small web/client-server system, API, SQLite, RBAC, concurrent orders, backup, NAS/container deployment | `application-client-server-architecture` | `safe-incremental-refactoring` only for an existing brownfield system |
| AI Agent task contract, tools, autonomy, memory, evaluation, guardrails, approval and operations | `agent-development-process` | `coding-agent-project-governance` only when repository operating rules are also requested |
| ACK versus physical completion where the main deliverable is a component Commanded/Pending/Actual/Readback contract and timeout/recovery also crosses Sequence and Equipment Service | `equipment-domain-modeling` | Add `equipment-control-architecture` for interlock, late-completion and recovery ownership; execute modeling before architecture |
| Local Runtime Eval execution or diagnosis: Python/Ollama discovery, context overflow, missing JSONL/report, Routing versus Behavior grading, or one uploadable review ZIP | `local-runtime-eval-debugging` | Add `developing-skills` only when the requested output also changes skill routing or behavior |
| AGENTS.md, coding-agent worktrees, repository risk routing, release evidence, skill descriptions, Eval mining or plugin packaging | `coding-agent-project-governance` or `developing-skills` | Use `developing-skills` when the requested output changes CloudSkill routing or behavior |

## Language-neutral counterexamples

| Prompt | Expected result |
|---|---|
| `請把「系統已完成更新」翻譯成英文。` | No CloudBox skill; translation is fully specified. |
| `幫我把這句話寫順：系統更新之後目前都正常。` | No CloudBox skill; simple rewriting is not an engineering decision. |
| `Design ownership and restart recovery for chamber IPCs and shared transfer resources.` | `equipment-control-architecture`; English wording does not suppress routing. |
| `Review 這段 C# callback ordering and stale response handling.` | `code-review`; mixed language does not alter the failure boundary. |

## Owner versus execution order

For a version-scoped multi-audience report:

```json
{
  "primary_skill": "document-governance",
  "supporting_skills": ["software-quality-iso25010"],
  "execution_order": ["software-quality-iso25010", "document-governance"]
}
```

The document skill owns the deliverable, while the quality skill may execute first to establish denominator, exclusions, and metric validity.

For historical interaction optimization:

```json
{
  "primary_skill": "developing-skills",
  "supporting_skills": [],
  "execution_order": ["developing-skills"]
}
```

The router selected the skill but is not itself a downstream supporting skill.
