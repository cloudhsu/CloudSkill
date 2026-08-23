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

When a milestone's acceptance criterion is ambiguous or only implied by a
broad instruction, state the criterion explicitly and distinguish it from
the cheapest verifiable proxy (e.g. "compiles") before scoping work to that
proxy -- a proxy can be a necessary but far smaller subset of the actual
goal (e.g. the requester's real bar is opening the generated project,
building it, and running it themselves). When narrowing scope under
delegated/unsupervised authority because a full milestone is large, disclose
the narrowing explicitly as a scope decision rather than silently treating
the narrower proxy as equivalent to the requester's actual goal. When the
requester corrects the acceptance bar, retarget the milestone to the real
criterion rather than continuing to report against the earlier proxy.

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

## Holding Back Large or Verification-Heavy Items, Even When Reversible

Risk classification above is by consequence, not code size — but a
large-but-reversible item can still need to be held back from unattended
execution for a different reason: it cannot be safely completed and
verified within one unattended session. Hold back such an item even when
every individual step is reversible, and explicitly record what was held
back and why (too large to verify unattended, not too risky to attempt) —
do not let scale alone silently justify skipping verification instead of
justifying a pause.

## Host-Machine-Global Changes Under Repo-Scoped Delegation

When delegated autonomous authority is scoped to a repository/branch, and a
fix requires changing shared host-machine state outside the repository (a
globally-installed compiler, SDK, or package-manager-managed tool), treat
that as a distinct category of action from ordinary branch-scoped work and
record it explicitly and separately, even when the change is reversible and
no project files are affected. State plainly in the record what was
changed, why the in-repo fix was insufficient, and that it is reversible
via the same package manager -- do not fold it silently into the list of
repository file changes. Confirm the host change did not silently alter
behavior for any other project or workspace that also depends on the same
globally-installed tool before treating it as fully low-risk.

## Full-Screen Capture Risk During Visual Verification

Prefer a scoped/targeted capture mechanism (a specific window, a specific
app's bundle/rendered surface) over a full-screen capture when gathering
visual verification evidence, since a full-screen capture can incidentally
include unrelated windows or private content outside the scope of the
check. If a capture mechanism unintentionally captures out-of-scope
content, delete it immediately and do not describe, summarize, or act on
what it contained. After such an incident, disclose the limitation
explicitly rather than silently repeating the same risky capture method for
a later, similar verification need in the same session -- substitute a
narrower verification method and hand off the remaining visual confirmation
to the user when no safe scoped-capture method is available. Report
reduced-scope verification honestly (what was actually confirmed versus
deferred) rather than presenting a file-level check as equivalent to a full
visual confirmation.

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
