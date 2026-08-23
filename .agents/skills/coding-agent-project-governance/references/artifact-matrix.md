# Project Artifact Matrix

| Concern | Suggested artifact |
|---|---|
| Entry/read order | `00_START_HERE.md` |
| Always-on rules | `AGENTS.md` |
| Product/system state | `PROJECT_CONTEXT.md` |
| Non-negotiable business rules | `DOMAIN_INVARIANTS.md` |
| Modules and responsibilities | `ARCHITECTURE_AND_FILE_MAP.md` |
| Engineering workflow | `DEVELOPMENT_STANDARDS.md` |
| API contract | `API.md` or OpenAPI |
| Decisions | `DECISION_LOG.md` / ADRs |
| Requirements/change history | requirement records/changelog |
| Test evidence | `TEST_REPORT.md` / CI artifacts |
| Operations | `OPERATIONS_RUNBOOK.md` |
| Release | `RELEASE_CHECKLIST.md` |
| Complex work | ExecPlan following `PLANS.md` |
| Security gaps | threat/risk register |
| Long-running/multi-session progress | a checkpoint convention: one append-only forward roadmap of planned stopping points, one always-current status snapshot, and one immutable dated record per stopping point (never rewritten after the fact — corrections land as new entries in the living docs, with a pointer back) |

Not every repository requires every file. Include an artifact only when it has a clear consumer and maintenance owner.

For the long-running/multi-session checkpoint artifact specifically: report evidence per stopping point as PASS, FAIL, BLOCKED, or NOT RUN — never silence or an implied pass for something not actually executed. When a later stopping point corrects an earlier one (a wrong assumption, a mistaken claim), edit only the living roadmap/status docs and add a new dated correction entry; leave the earlier immutable record as it was written, so the history of what was believed at each point stays honest and reviewable.

Identify a still-PLANNED or not-yet-started roadmap row by a stable, non-colliding identifier drawn from a different namespace than the sequential checkpoint/record ID (e.g. a phase or slice name), never by a guessed-ahead sequential number — a guessed number shares the same namespace as completed records and can collide once real completion order diverges from the guess. Assign the real sequential ID to a row only at the moment it actually completes with evidence, replacing its placeholder identifier at that point. If a numbering collision is found anyway, fix the identifier scheme itself, not just that one collision, and record in the roadmap why the convention changed so a later reader understands the discontinuity instead of assuming a numbering error.
