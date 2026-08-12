# Coding-agent Risk Routing

## Low Risk

Examples:

- Documentation wording.
- Formatting.
- isolated UI polish with no behavior change.
- test-only clarification.

Default:

- One main agent.
- Focused checks.
- No unnecessary subagent overhead.

## Medium Risk

Examples:

- Read-only API.
- Query/read model.
- Isolated component.
- Small compatible behavior extension.

Default:

- Main/Development.
- Independent test or review angle.
- Focused and regression tests.

## High Risk

Examples:

- Money/balance.
- authentication/RBAC.
- personal data.
- schema/migration.
- historical records.
- transaction.
- production deployment.
- security.
- irreversible external action.
- physical equipment control.
- broad refactor crossing ownership boundaries.

Default:

1. Architecture/risk analysis.
2. Approved acceptance criteria.
3. Isolated implementation.
4. Independent adversarial testing.
5. Integrator review.
6. Human approval for deployment/data conversion.

## Delegation Scope for Irreversible Steps

Refines High Risk item 6 ("Human approval for deployment/data conversion")
when the approval itself was already given as a short, ambiguous phrase
rather than a fresh explicit instruction for each step.

- When a short delegation phrase for a release/publish task is ambiguous
  about whether it covers only preparation or also the irreversible publish
  steps, treat the user's established pattern of delegation trust earlier in
  the same session as real evidence about scope. Do not discount it in favor
  of a generic default level of caution when real, recent, in-session
  evidence points the other way.
- Distinguish, explicitly, which remaining steps are still fully reversible
  (editing files on a branch, opening a pull request) from which are not
  (merging to the default branch, pushing a tag, publishing a release). The
  delegation-scope question binds to the irreversible steps specifically,
  not to the sequence as a whole.
- Proceeding autonomously through delegated irreversible steps never waives
  the project's own verification gates. Run the same checks the project's CI
  runs and confirm each result before the next irreversible step, rather
  than treating delegation as license to skip verification along with the
  extra confirmation prompts.
- Counterexample: if the same short delegation phrase arrives as the first
  request of a session, with no established track record of unsupervised
  delegation, the safer reading is to prepare fully and pause once for
  explicit confirmation before the first irreversible step.
- Stop condition: if the delegated task would touch a resource or audience
  beyond the requesting user (a shared repository with other maintainers, a
  registry with external consumers who auto-pull updates), pause before the
  irreversible steps regardless of established in-session trust — the
  audience for the irreversible action is no longer only the person who
  delegated it.

## Tool-permission Allowlist Tiers

When narrowing a broad tool-permission wildcard into a curated rule set, use
three tiers rather than a binary allow/deny split — a middle confirmation
tier more precisely separates "safe to auto-run" from "a human should see
this before it runs":

- **ALLOW**: read-only, idempotent, or trivially-reversible operations.
- **ASK**: operations reversible in principle but consequential, or that
  touch shared/remote state.
- **DENY**: genuinely irreversible one-way-door operations, or operations a
  project's own rules explicitly forbid.

Tie DENY entries to explicit project rules where one exists (for example, a
rule against fabricating commit/author history maps directly to a hard deny
on commands that rewrite authorship or provenance), not just to a general
irreversibility judgment.

Disclose the limitations of pattern-based matching honestly and completely:
a prefix-anchored pattern misses the same flag placed later in the argument,
an alternate flag/syntax achieving the same effect, a command alias that
wraps the dangerous command under a different name, and reaching the same
destructive outcome through a different tool or a direct API call that
bypasses the pattern-matched tool entirely. Do not claim a narrowed
pattern-based permission set eliminates risk without this disclosure.

Apply the same three-tier classification consistently across every settings
file/scope the user names. Do not let a narrower scope's ALLOW rule silently
override a broader scope's DENY rule without the user's explicit approval.

Counterexample: if the underlying permission system genuinely has no middle
confirmation tier (only allow/deny exist as mechanisms), the binary split is
the correct fallback — the three-tier requirement applies when the tooling
actually supports an ask/confirm tier.

## Escalation

Escalate when:

- Requirements conflict.
- Data could be lost.
- Recovery is undefined.
- Existing tests disagree with documents.
- A change alters public contracts or historical meaning.
