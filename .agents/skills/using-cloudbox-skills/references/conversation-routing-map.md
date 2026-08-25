# Conversation-derived routing map

Use this reference for recurring engineering scenarios and routing counterexamples. These examples are semantic pressure tests, not keyword-only triggers.

## Routing contract

- `primary_skill` owns the requested deliverable or final decision.
- `supporting_skills` materially change the work.
- `execution_order` records analysis or governance order and may begin with a supporting skill.
- `using-cloudbox-skills` performs routing and is not normally included in the downstream skill list.
- Prompt language is not a routing condition.

## Reusable routing cues

| Recurring engineering pressure | Primary route | Add only when needed |
|---|---|---|
| Concrete code defects involving duplicate command, stale response, NetworkStream/buffer, thread safety, callback order, timeout, or late response | `code-review` | Add `equipment-domain-modeling` when the same request redesigns Commanded/Desired/Pending/Actual/Readback or command-attempt semantics. Do not substitute `equipment-control-architecture` unless Sequence/Equipment Service, interlock, shared-resource, reconnect/restart/failover, or physical recovery ownership is explicitly requested. |
| Sequence versus Equipment Service, shared robot/aligner, pump/vent, interlock, material location, distributed IPC, reconnect, failover or HA | `equipment-control-architecture` | Add `semiconductor-equipment-domain-knowledge` only when physical process meaning, vacuum/readiness, or component completion evidence must be clarified; do not add it for a generic ownership/recovery topology question. Add `architecture-review` for option comparison or `safe-incremental-refactoring` for migration. |
| Valve/MFC/pump/gauge DTOs, typed commands, union-like payloads, Actual/Desired/Readback, stale snapshots, capability-driven UI | `equipment-domain-modeling` | Add `equipment-control-architecture` when physical completion, timeout/late completion, interlock, sequence/service boundary, or recovery ownership crosses the component model. Add `code-review` for a concrete defect or `framework-design` for a reusable product-line kernel. |
| CEO/management versus engineer/training reports, one source split into multiple views, revision lineage, terminology normalization | `document-governance` | `software-quality-iso25010` for measurable populations, metrics, exclusions, and release gates |
| Field failures or update success rates must correlate to an actual software version; unversioned records remain visible but outside version metrics | `document-governance` | `software-quality-iso25010` to define denominator, exclusions, confidence, and quality interpretation; run quality analysis before document transformation when the metric definition is unresolved |
| Qt/MFC modernization, HID/USB, device hot-plug, firmware update, privileged Windows/macOS integration, installer or Qt version migration | `cross-platform-native-architecture` | `safe-incremental-refactoring`, `framework-design`, or `software-quality-iso25010` only for explicit migration, reuse, or gate concerns |
| Small web/client-server system, API, SQLite, RBAC, concurrent orders, backup, NAS/container deployment | `application-client-server-architecture` | `safe-incremental-refactoring` only for an existing brownfield system |
| AI Agent task contract, tools, autonomy, memory, evaluation, guardrails, approval and operations | `agent-development-process` | `coding-agent-project-governance` only when repository operating rules are also requested |
| Component-only Commanded/Pending/Actual/Readback, ACK versus physical completion, and late-readback reconciliation contract; Sequence/service ownership is explicitly out of scope | `equipment-domain-modeling` | Do not add `equipment-control-architecture` or `semiconductor-equipment-domain-knowledge` when physical meaning and completion evidence are already supplied |
| Sequence versus Equipment Service timeout, late-completion, interlock, retry/recovery, or shared-resource responsibility; component DTO/state contract is already defined | `equipment-control-architecture` | Do not add `equipment-domain-modeling` or `semiconductor-equipment-domain-knowledge` when no component redesign or physical-domain interpretation is requested |
| Component state/command contract is the explicit main deliverable and cross-layer timeout/recovery responsibility is a separate secondary deliverable | `equipment-domain-modeling` | Add `equipment-control-architecture`; execute modeling before architecture. Do not add `semiconductor-equipment-domain-knowledge` when physical meaning and completion evidence are already supplied |
| Executable Eval design or review: case validity, context evidence, reproducibility, deterministic versus semantic grading, false positives, score interpretation, or release gates | `runtime-evaluation-engineering` | Add `developing-skills` only when the requested output changes Skill behavior; add `local-runtime-eval-debugging` only when host execution or packaging is also required |
| Local Runtime Eval execution or diagnosis: Python/Ollama discovery, context overflow, missing JSONL/report, Routing versus Behavior grading, or one uploadable review ZIP | `local-runtime-eval-debugging` | Add `runtime-evaluation-engineering` when the task also questions case, metric, rubric, grader, or release-gate validity; add `developing-skills` only when Skill behavior will change |
| AGENTS.md, coding-agent worktrees, repository risk routing, release evidence, skill descriptions, Eval mining or plugin packaging | `coding-agent-project-governance` or `developing-skills` | Use `developing-skills` when the requested output changes CloudSkill routing or behavior |
| Long-running/multi-session checkpoint or roadmap tracking: forward roadmap of planned stopping points, a current-status snapshot, an immutable dated record per stopping point, or a PLANNED-row identifier scheme | `coding-agent-project-governance` | Do not route this to `document-governance` merely because it is "one source split into multiple views" (row above) -- the checkpoint convention's view split, identifier-collision rule, and PLANNED-vs-completed numbering are this Skill's own artifact-matrix.md content, not a generic document-authority/version-lineage question |
| Cross-equipment WPH, cycle-time, utilization, queue, bottleneck, scheduling, product-mix, downtime or capacity simulation | `wph-equipment-simulator-development` | Add the relevant equipment-family Skill for physical topology and custody; WPH is not a product-line identity or physical-interlock owner |
| Individual materials fill Tray pockets, a complete Tray enters descum/plasma cleaning, then unload/return preserves identity | `tray-descum-simulator-development` | Add `wph-equipment-simulator-development` only when capacity analysis is requested; do not infer map-based die sorting or cluster-tool vacuum stages |
| EFEM/load ports, load locks, transfer chamber, atmospheric/vacuum robots and configurable process modules with recipe routes | `cluster-tool-simulator-development` | Add `wph-equipment-simulator-development` for capacity; add control/domain Skills for production interlock or physical semantics |
| Device wafer/carrier preparation, alignment, bonding, debonding, cleaning, pair provenance or combo equipment | `wafer-bonder-debonder-development` | Add WPH for capacity; do not route generic die attach or wire bonding by keyword overlap |

## Language-neutral counterexamples

| Prompt | Expected result |
|---|---|
| `請把「系統已完成更新」翻譯成英文。` | No CloudBox skill; translation is fully specified. |
| `幫我把這句話寫順：系統更新之後目前都正常。` | No CloudBox skill; simple rewriting is not an engineering decision. |
| `Design ownership and restart recovery for chamber IPCs and shared transfer resources.` | `equipment-control-architecture`; English wording does not suppress routing. |
| `Review 這段 C# callback ordering and stale response handling.` | `code-review`; mixed language does not alter the failure boundary. |
| `Review retransmission/callback/stale-response code and redesign Commanded/Pending/Actual/Readback plus timeout-late-response semantics; Sequence/service recovery is not requested.` | `code-review` plus `equipment-domain-modeling`; do not replace the modeling support with `equipment-control-architecture`. |
| `Define only the Valve Commanded/Pending/Actual/Readback contract; Sequence recovery is out of scope.` | `equipment-domain-modeling` only. |
| `Allocate Sequence/Equipment Service timeout and recovery ownership; the component contract is already fixed.` | `equipment-control-architecture` only. |
| `The component contract is the main deliverable, then allocate cross-service recovery responsibility; physical semantics are already known.` | `equipment-domain-modeling` plus `equipment-control-architecture`, in that order; no domain-knowledge skill. |
| `Estimate capacity for three different equipment families.` | `wph-equipment-simulator-development` plus each relevant equipment-family Skill; WPH owns simulation mechanics. |
| `Sort dies by wafer map into output bins; there is no descum process.` | Do not use `tray-descum-simulator-development`; visual Tray similarity is insufficient. |
| `A fixed atmospheric Tray-loading line has one descum PM and no load lock.` | `tray-descum-simulator-development`, not `cluster-tool-simulator-development`. |
| `Perform die attach and wire bonding.` | Do not use `wafer-bonder-debonder-development` unless wafer/carrier pair semantics exist. |

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
