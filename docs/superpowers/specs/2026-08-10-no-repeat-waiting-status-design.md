# No-repeat waiting-status governance design

## Pressure

When an agent has already reported that work is waiting, paused, or blocked,
automatic continuation turns can cause it to repeat the same status despite no
new user input or external-state change. The repetition adds no evidence or
decision value and consumes tokens.

## Decision

Add one concise repository-wide rule to the collaboration guidance in
`AGENTS.md`:

- report entry into a waiting, paused, or blocked state once;
- do not repeat the same status when there is no new user input, external-state
  change, or newly available action;
- do not treat an automatic continuation by itself as a state change;
- communicate again only when work resumes, state changes, or a user decision
  becomes necessary.

This is an always-on coding-agent collaboration rule, so `AGENTS.md` is the
authoritative owner. `CLOUDSKILL_AGENT_HANDOFF.md` remains the owner of the
current 6.0 execution state and must not duplicate the general rule.

## Alternatives rejected

- Handoff-only wording would govern only the current evolution session.
- A Skill/Eval change would add routing and behavior-evidence overhead for a
  repository interaction rule that belongs in always-loaded instructions.

## Verification

This is human-facing instruction prose, not executable product behavior. Review
the diff for scope and ambiguity, run the repository documentation/handoff
validator, and include the normal full release verification later in Task 8.
