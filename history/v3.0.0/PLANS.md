# Execution Plans

Use an execution plan for complex features, architecture migrations, multi-module refactors, agent development, or work expected to span multiple sessions.

An execution plan is a living implementation specification. A new engineer or agent should be able to resume from the plan and the current working tree without relying on hidden conversational context.

## Required Sections

1. Goal and user-visible outcome.
2. Scope and non-goals.
3. Current-system reconstruction.
4. Constraints and assumptions.
5. Architecture or approach.
6. Milestones.
7. Verification and acceptance.
8. Risks and rollback.
9. Progress log.
10. Decision log.
11. Discoveries and deviations.
12. Final outcome and remaining work.

## Rules

- Keep progress current after each meaningful stopping point.
- Record decisions when the plan changes.
- Include commands, files, tests, and observable acceptance results.
- Do not mark a milestone complete without evidence.
- Preserve failed approaches when they explain future constraints.
- Prefer incremental, runnable milestones.
- Define rollback before high-impact changes.
