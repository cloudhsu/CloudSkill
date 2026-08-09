# Host-level task-continuity contract

This suite defines structural fixtures for host-level task-continuity behavior.
It is deliberately independent of routing CSV entries and CloudBox Skills.

`task-continuity.schema.json` is the authoritative structural owner. The
Python adapter interprets its declared JSON-Schema subset and
`x-cloudbox-invariants`; it does not duplicate per-field constraints. Each
case supplies ordered transcript turns, durable parent/source/freshness
evidence, allowed and prohibited authority actions, and expected parent status,
tool attempts, and outcomes. Tool-attempt names share the authority-action
namespace, so every expected attempt must be allowed and not prohibited. The
control cases prevent over-triggering on an
explicit cancellation or pivot, authorized publishing, a deliberately promoted
side question, an already completed parent, missing identity evidence, and
ordinary prose containing “continue”.

Run the static contract check with:

```bash
python3 scripts/validate_task_continuity_evals.py
```

The validator tests structural integrity only. It always reports behavior
execution as `NOT RUN`; a passing result is not host behavior evidence. The
shared result schema also permits future truthful execution states (`PASS`,
`FAIL`, `BLOCKED`, and `MANUAL REQUIRED`), but this static validator never
emits them. Its declared evidence matrix requires clean errors for all-PASS
records, diagnostics for `FAIL`/`BLOCKED`/`MANUAL REQUIRED`, and prohibits a
behavior `PASS` when structural contract validation failed. Every diagnostic
must be trimmed non-empty text; empty or whitespace-only entries are not
evidence.
