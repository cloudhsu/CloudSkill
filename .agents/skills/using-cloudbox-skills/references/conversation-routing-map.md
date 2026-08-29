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
| Long-running/multi-session checkpoint or roadmap tracking: forward roadmap of planned stopping points, a current-status snapshot, an immutable dated record per stopping point, or a PLANNED-row identifier scheme | `coding-agent-project-governance` | Do not route this to `document-governance` merely because it is "one source split into multiple views" (row above) -- the checkpoint convention's view split, identifier-collision rule, and PLANNED-vs-completed numbering are this Skill's own artifact-matrix.md content, not a generic document-authority/version-lineage question |
| Dispatching a worktree-isolated or background subagent to read files / investigate and report, including any instruction about where it writes its findings | `coding-agent-project-governance` | A subagent told to keep its only detailed report inside a worktree that may be torn down before retrieval is exactly this Skill's read-only-investigation reporting rule. The instruction being fully specified is why the skill is needed, not why it is not -- do not return no-skill because "the steps are all given". |
| Writing a change-record's status for a requirement that is accepted / implemented but not yet verified or released | `development-process-tailoring` | Add `document-governance` for its separated requirement/implementation/verification/release status model. Producing one flat "Status: implemented" value is the named anti-pattern; do not return no-skill because the field looks like trivial rewriting. |

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
| `Dispatch a worktree-isolated subagent to read 12 files and write its full report to a file in its own worktree, with a short inline summary.` | `coding-agent-project-governance`; the worktree-report retrieval rule applies precisely because the instruction is fully specified, not no-skill. |
| `Write the status field for a change record whose requirement is accepted and implemented but not verified or released.` | `development-process-tailoring` (add `document-governance`); keep the status dimensions separate -- not no-skill "trivial rewriting". |

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
  "supporting_skills": [],
}
```

The router selected the skill but is not itself a downstream supporting skill.
