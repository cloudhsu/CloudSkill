# Architecture decision elicitation

Use this protocol only when a missing answer can materially change an
architecture conclusion about authority, state, lifecycle, transactions,
deployment, recovery, security, migration, or release compatibility.

## Decide whether to ask

First inspect available repository evidence and user-stated constraints. Do not ask when the evidence already answers the decision, the task is purely
explanatory or diagnostic, or a safe low-risk reversible default is sufficient.
Ask when proceeding would silently invent a consequential boundary or produce
materially different recommendations.

## Question contract

Ask exactly one decision question at a time. Provide two or three mutually exclusive choices. Put the recommended option first, mark it recommended, and
explain the mechanism and material trade-off of every choice in one sentence.
Resume the owning architecture Skill after the answer; do not route all domain
architecture work through `architecture-review`.

## Stop conditions

Do not turn explanation, code review, terminology, or a small reversible change
into a questionnaire. Do not repeat a question already answered in the current
task or repository. If the user delegates all bounded decisions, apply the
recommended safe defaults and record them unless new authority or irreversible
external action is required.
