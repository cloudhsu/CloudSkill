---
name: coding-agent-project-governance
description: Use when a repository needs coding-agent instructions, risk routing, worktree rules, multi-agent ownership, test evidence, migration controls, release rules, or truthful handoff.
---

# Coding-agent Project Governance

When executing a lifecycle plan, require the current authoritative plan
revision, declared task/artifact ownership, dependency-complete entry, explicit
authority, and completion evidence. A stale agent or worker result cannot
advance the plan. Repository actions remain bounded by worktree, test, commit,
PR, migration, and release controls even when another plugin generated the
detailed task steps.

Read the reference whose condition matches the task at hand, not all four by
default:

- `references/instruction-architecture.md` -- when deciding where a rule
  belongs or resolving a scope conflict between instruction layers: global
  guidance, repository `AGENTS.md`, a nested `AGENTS.md`/override, Skills,
  and how to resolve ambiguous scope between them.
- `references/risk-routing.md` -- when classifying how much autonomy an
  action should get: low/medium/high risk tiers, delegation scope for
  irreversible steps, and when to hold back a large or
  verification-heavy item even though it is technically reversible.
- `references/multi-agent-delivery.md` -- when more than one agent works
  the same repository concurrently: role split (Main/Integrator,
  Architecture, Development, Test) and the concurrency rule governing
  shared state between them.
- `references/artifact-matrix.md` -- when deciding which document should
  hold a given kind of project fact: the suggested artifact (entry order,
  always-on rules, product state, domain invariants, module map,
  engineering workflow, and more) per concern.

Use templates in `assets/`.

## Goal

Create a repository operating model in which coding agents can modify software without relying on hidden conversation context, bypassing domain invariants, fabricating evidence, or corrupting unrelated work.

## Workflow

### 1. Inspect before prescribing

Identify:

- Repository root.
- Existing instruction files.
- Source-of-truth code.
- Build/test commands.
- Deployment targets.
- Data and migration risks.
- Domain invariants.
- Git state.
- Existing release/version policy.
- Host toolchain and environment actually available (installed compilers,
  SDKs, target architecture) when the task involves building, cross-compiling,
  or configuring for a specific platform — verify by inspection, do not
  assume from the task description or from what the task "should" need.

Do not generate generic rules that contradict the actual repository.

### 2. Define instruction layers

Keep global `AGENTS.md` concise.

Use repository and nested instructions for:

- Build/test commands.
- Domain invariants.
- Directory responsibilities.
- Security.
- release.
- local exceptions.

Use references and skills for longer workflows.

### 3. Create a project entry map

Provide:

- `00_START_HERE.md`.
- Canonical repository guidance in `AGENTS.md`.
- A minimal `CLAUDE.md` importing `AGENTS.md` when Claude Code is used.
- `PROJECT_CONTEXT.md`.
- `DOMAIN_INVARIANTS.md`.
- `ARCHITECTURE_AND_FILE_MAP.md`.
- `DEVELOPMENT_STANDARDS.md`.
- API/interface docs where applicable.
- Operations/release/checklist docs.
- Decision and requirement history where necessary.

When the repository hosts both a product and a separately-versioned reusable
engine or component library, give product direction (owned by
`document-governance`'s product-direction document role) and visual-artifact
governance (owned by a private companion capability's draft-governance step, when the
repository has one) their own sibling top-level lanes alongside the
development-evidence lane above -- not nested under it. Define what each lane
does and does not have authority over, and require an explicit cross-link
whenever a product or visual decision changes implementation scope, rather
than letting the change land unlinked in only one lane.

Verify the real repo root/branch first; stale pointers are `document-governance` §0.

### 4. Route by risk

Classify work as low, medium, or high risk based on consequence, not code size.

Escalate for:

- Money or balances.
- Authentication/authorization.
- Personal or sensitive data.
- Schema/migration.
- historical data.
- transaction boundaries.
- irreversible external side effects.
- production deployment.
- large architecture changes.
- physical device/process control.

Adopting a new tool-calling/execution-capable dependency (an agent
framework, CLI, plugin marketplace, or similar) as project infrastructure is
itself a security-relevant decision, not just a technology choice.
Independently verify its security track record across multiple authoritative
sources (security-media, vendor advisories, CVE trackers) before recommending
adoption — a single third-party comparison article's summary is not
sufficient evidence, especially when it states a vulnerability count without
detail.

### 5. Assign agent roles only when useful

Possible roles:

- Main/Integrator.
- Architecture.
- Development.
- Test/Adversarial review.
- Security.
- Documentation/release.

Do not use subagents when tasks cannot be isolated or when they will edit the same critical files concurrently. When two or more isolated subagents' inputs do not depend on each other's output, dispatch them in parallel within the same turn rather than serializing work that has no ordering dependency.

### 6. Preserve evidence before it is committed

- Commit product-direction and visual-artifact discussion documents,
  proposal registers, draft images, provenance metadata, and templates once
  they become project evidence -- do not leave the only copy in chat
  history, an ignored worktree, or a generation cache. A commit records
  existence and recoverability, not approval: preserve DRAFT/status
  markers inside the committed artifact itself rather than treating the
  commit event as human sign-off, runtime validation, or release
  readiness. Use versioned filenames or append-only records instead of
  overwriting an earlier draft, and link each checkpoint to its commit.

A dispatched, worktree-isolated subagent's own worktree is not guaranteed to
outlive the subagent's completion -- some are torn down automatically before
the dispatcher retrieves anything from them, others persist, and this is not
predictable in advance. For a read-only investigation/analysis subagent whose
deliverable is a report rather than a commit, require the full findings in
the subagent's own final report message (the channel the dispatcher's task
notification actually preserves), not solely in a file written inside its
own worktree; treat any such file as a best-effort bonus copy the dispatcher
must retrieve immediately if it wants one, never as the only copy of record.

For the git mechanics themselves (branches, worktrees, commit hygiene,
push-auth recovery, shared-checkout detection, release cadence), use
`$coding-agent-git-discipline`.

### 7. Require evidence

Handoff must separate:

- PASS.
- FAIL.
- BLOCKED.
- NOT RUN.
- MANUAL REQUIRED.

Do not claim device, OS, deployment, browser, or external-system tests that were not executed.

Treat an agent's self-reported validation as a claim to verify before using it as acceptance evidence: inspect enough of the checking script to confirm pass/fail fields are computed rather than hard-coded, verify cited files and paths exist, and for work still running confirm an explicit completion signal and the expected repository HEAD before rebuilding, testing, or diagnosing a regression. If provenance or completion is unverified, report the result as NOT RUN and do not treat intermediate working-tree output or clean-looking visual inspection as confirmation; independently measure material claims where practical.

Delegated workers have lifecycles: a worker whose lifecycle has ended or
expired is restarted or replaced, never implied still active. Bind completion
to a verified source tip: record the repository tip that was actually verified,
and do not report completion when a later or late edit is not in that tip.
Agreeing worker reports are claims, not executable proof.

A batch (tens of items) visual- or content-judgment self-report that lands
on a single uniform conclusion across every item (e.g. "all N flagged files
are false positives," "all N pass") is itself a red flag, not reassurance
-- a real distribution across that many independently-generated items
rarely comes back unanimous. Spot-check at least a few concrete items from
such a report, including their file timestamps against the task's actual
run window, before accepting it; a real batch of ~40 flagged files was
reported as "all false positives, nothing modified" while several,
independently re-opened, showed an unambiguous, unmodified real defect.
When a spot-check contradicts a uniform-conclusion report, treat the whole
report as unreliable rather than asking the same agent to re-run the same
self-audit -- hand the next attempt a pre-confirmed item list instead of
asking it to re-judge which items are real.

Evidence status: directional experiment evidence, n=1-per-arm at the
`skill_behavior` layer; it is not proven or validated at a higher layer.
The batch-uniform-conclusion case is separately evidenced, also
`skill_behavior`, n=1.

Do not fabricate an attribution, author, submitted-by, or other identity
field that the task never supplied, even when a report-style deliverable
"looks like" it should carry one -- see `references/no-fabricated-identity.md`
for the rule, why it recurs across unrelated skills, and how it differs from
the separate known-identity redaction case. A bundled `identity-leak-backstop`
hook enforces this deterministically at commit time.

A CI/PR status-check polling command (or a background task wrapping one) can
report a nonzero exit code or a "failed"-labeled status purely because a check
is still pending, not because it actually failed -- read the command's real
per-check output before classifying the result. Re-run the exact status
command directly to confirm real pass/fail/pending state before reporting a
result to the user or beginning failure diagnosis; do not treat "pending" as
FAIL.

### 8. Stop escalation on repeated failure

After a small fixed number of repeated failures on the same gate/check (for
example, the same push, review, validation, or login/auth step failing again
in essentially the same way), stop and diagnose the cause instead of
continuing:

- Determine whether the blocker is environmental (sandbox/permission denial,
  authentication, network, quota) rather than a code defect. Do not "fix" an
  environment block by rewriting application logic.
- Do not silently retry the identical failing command a fourth, fifth, or
  further time hoping the result changes. A repeated identical failure is
  itself the signal to stop, not evidence that one more attempt is warranted.
- Report BLOCKED with the exact repeated error and the suspected cause, and
  stop there, rather than silently continuing to attempt new workarounds.
- Do not rewrite a core mechanism (security, trust, verification, transport)
  more than once in response to the same repeated failure without an
  explicit user checkpoint. A defensive change made to satisfy one review
  pass must not introduce a new conflict with the agent's own prior changes.

Tool-use discipline: a tool whose name or description ties it to a specific
session mode (for example self-paced loop wakeups) is used only after checking
the current context matches that mode. While a background task or subagent is
running and the only goal is to avoid polling, do nothing further and rely on
the harness's completion notification; do not schedule a fallback. Before
calling any stop/cancel action, read that tool's documented scope to confirm
it does not also affect other live work (a cancel can terminate a running
subagent), and do not assume an undo call is harmless or repeat it "once more"
without that check.

For a failed GitHub `git push` or any other git-mechanics failure, use
`$coding-agent-git-discipline`.

### 9. Release safely

Define:

- Version source.
- Artifact source.
- Build process.
- Migration.
- backup.
- rollback.
- health/version verification.
- changelog.
- requirement/test documentation.
- artifact hash/tag policy.

Checkpoint (commit/tag) scoped exactly to the evidence boundary already
established — not ahead of it, not behind it. Merge only after the target
branch is clean and the tag is reachable from it. When a step remains that
the agent cannot complete itself (a remaining push, an external approval),
leave a precise operator handoff naming exactly what is left and why,
rather than an ambiguous "done" that omits it.

"Version" is two facts, not one: the released source marker (VERSION file /
latest tag) and the version the consumer actually has — a deployed build, or
a package/plugin installed from a directory or path source, which is a
pinned copy that does not advance when its source does. When asked whether
something is "on the latest version," check both and report the gap
(releases / commits behind) and the update step, not "yes" from the source
marker alone; a mid-session update applies only after the consumer reloads
or restarts. A source-side release completing is not evidence that deployed
or installed consumers are on it (this is the §7 unverified-external-state
rule applied to version claims).

When an increment writes to a size-budgeted living document (an agent
handoff, a change log, a decision log) whose budget a check enforces, and
the write leaves it within a small margin of the ceiling, do the archival
compaction in the same increment: compress fully-superseded sections to
short pointers into the durable record they already cite (release notes,
plan files, change history), leave the current increment and any
contract/authority section untouched, re-run the document's validators, and
report the before/after size. Do not leave it at the ceiling for the next
contributor, and do not delete history that has no other durable record.

Before rebuilding a GUI or other long-running executable, verify no relevant
process still holds the target output and remind the operator to close it
first. Treat that lock as a stop condition for the operator to resolve —
never force-close a user's running process merely to unblock a build.

## Output Format

1. Repository operating model
2. Instruction hierarchy
3. Entry/read order
4. Domain invariants and authority
5. Risk-routing table
6. Agent roles and concurrency model
7. Git/worktree rules
8. Test and evidence contract
9. Documentation synchronization
10. Release/rollback checklist

## Source-derived Evidence Discipline

For compatibility-sensitive repositories:

- Preserve public method/API inventories as executable contract tests where valuable.
- Preserve database/source hashes during migration tests.
- Test old database copies and future-version refusal.
- Separate product version changes from pure internal refactoring.
- Do not commit regenerated bundles merely because tests rebuilt them unless the release requires it.
- Keep known behavior fixes separate from structural refactoring.
