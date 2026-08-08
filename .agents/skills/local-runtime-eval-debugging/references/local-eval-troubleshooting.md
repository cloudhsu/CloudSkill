# Local Runtime Eval troubleshooting

## Stage signatures

| Stage | Typical evidence | Interpretation | Next action |
|---|---|---|---|
| Python discovery | `python=not-selected` | Model execution never started | Install or select Python 3.10+ |
| Ollama check | local API unavailable or model absent | Model execution never started | Start Ollama or install exact model |
| Context preflight | `overflow_tokens > 0` | Required prompt does not fit | Select larger context; do not truncate required Skill files |
| Routing execution | JSONL missing or record has `error` | Routing call failed | Inspect request/runtime error and latency |
| Routing grading | Contract valid but wrong owner/supporting set | Model routing quality issue | Refine case boundary or Router evidence |
| Behavior execution | `behavior_status != completed` | Second call did not produce a deliverable | Inspect route validity and selected-skill context |
| Behavior grading | Low score with completed output | Engineering evidence or final-answer discipline is weak | Refine output while preserving raw answer |
| Packaging | Reports exist but ZIP missing | Evidence exists; handoff failed | Repackage current run only |

## Context budget rule

Use the smallest candidate that fits every selected case. A practical candidate sequence is:

```text
4096, 6144, 8192, 12288, 16384, 24576, 32768
```

Static validation must use a capacity that matches the current catalog, not the historical default.

## Routing ambiguity rule

A Canary case must state distinct deliverables when it expects multiple skills. For ACK-versus-completion composition:

- component command/state/readback contract belongs to `equipment-domain-modeling`,
- Sequence/Equipment Service timeout, late completion, interlock, and recovery ownership belongs to `equipment-control-architecture`.

If the prompt only asks broadly for “state, completion, timeout, and recovery,” a model may reasonably choose only the architecture owner. Make the component-model deliverable explicit before treating that route as a model defect.

## Behavior refinement rule

A refinement pass is justified when the raw answer contains internal planning or is cut off before the final deliverable. Preserve both outputs and grade both. The refined answer must explicitly cover only task-relevant engineering boundaries and label assumptions rather than inventing facts.
