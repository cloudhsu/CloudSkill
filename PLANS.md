# Execution Plans

Use an ExecPlan for multi-module, multi-session, architecture-migration, or high-risk work.

The plan must be resumable from the working tree and document alone. It must include:

1. Goal and observable outcome.
2. Scope and non-goals.
3. Current-system reconstruction.
4. Constraints and assumptions.
5. Architecture/approach.
6. Incremental milestones.
7. Verification and acceptance evidence.
8. Risk, rollback, and stop conditions.
9. Progress log.
10. Decision log.
11. Discoveries/deviations.
12. Final outcome and remaining work.

Rules:

- Keep progress current after each meaningful stopping point.
- Leave the repository runnable at each milestone where practical.
- Do not mark work complete without evidence.
- Record failed approaches when they explain future constraints.
- Define rollback before high-impact changes.

Use `.agents/skills/agent-development-process/assets/EXEC_PLAN.template.md` as the detailed template.
