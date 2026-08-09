# Conversation-derived skill optimization

Use this reference when several available interactions, user corrections, or Eval candidates must be converted into a reusable CloudSkill improvement.

## Evidence boundary

The optimization may use only evidence that is actually accessible in the current task:

- Current conversation turns.
- Explicit memory or personal-context summaries made available to the agent.
- User-uploaded conversation exports or documents.
- A configured private Eval Inbox.
- Connected repository files, issues, pull requests, and release history.

Record unavailable sources. Do not imply access to all chats, deleted turns, hidden runtime traces, local files, or private systems unless a tool actually returned them.

## Sanitization boundary

Before any repository write or deliverable:

- Remove organization, customer, person, project, product, equipment, site, account, address, path, URL, credential, schedule, recipe, safety-limit, and hardware-identifier details.
- Replace exact values with the engineering pressure they demonstrate.
- Preserve distinctions such as observed, inferred, and unknown.
- Keep confidential operational procedures and current controlled specifications out of public skills.

A local path may appear in a one-time application script supplied to its owner, but it must not become a reusable global skill rule.

## Extraction model

For each correction or successful pattern, capture:

1. Original task category.
2. Observed wrong route or missing behavior.
3. User correction.
4. Reusable engineering pressure.
5. Correct skill owner.
6. Required behavior.
7. Forbidden behavior.
8. Counterexample or adjacent-skill boundary.
9. Evidence confidence.
10. Candidate routing or behavior Eval.

## Common reusable pressure patterns

These are generalized examples, not user-specific rules:

- **Duplicate send, stale response, timeout or callback ordering:** usually `code-review`; add domain modeling only when state and command semantics must change.
- **Transport acknowledgement versus physical readback:** `equipment-domain-modeling` or `equipment-control-architecture`, depending on whether the problem is component state or process/resource execution.
- **Sequence, shared resources, distributed IPC and restart recovery:** `equipment-control-architecture`; add domain knowledge when physical readiness is uncertain.
- **Executive, engineering and training views from one source:** `document-governance`; derived views must share evidence and statistical definitions.
- **Version-correlated field quality:** `software-quality-iso25010` plus `document-governance`; exclude unversioned records from version metrics and report them separately.
- **Qt/native device, HID/USB, firmware and installer boundaries:** `cross-platform-native-architecture`.
- **Small client/server system with API, identity, SQLite, concurrency and NAS deployment:** `application-client-server-architecture`.
- **Agent task contract, tools, autonomy, memory and Evals:** `agent-development-process`; repository instructions remain `coding-agent-project-governance`.
- **Skill routing, descriptions, behavior cases or plugin packaging:** `developing-skills`.

## Owner selection

Prefer this order:

1. Existing skill description when the failure is routing-only.
2. Existing skill body when a decision rule or safeguard is missing.
3. Supporting reference for heavy reusable detail.
4. Eval case for a known regression.
5. Deterministic validator for syntax or consistency.
6. New skill only when the trigger and lifecycle are independently routable.

Do not copy the same mutable rule into the router, domain skill, quality skill, and repository guidance. Put the full rule in its authoritative owner and keep routing cues concise.

## Delivery modes

- **Writable repository:** single-purpose branch, commit, and draft PR.
- **Read-only repository:** overlay ZIP or unified patch preserving repository paths.
- **No repository:** a proposed file tree and replacement contents.
- **Insufficient or unsafe evidence:** `MANUAL_REQUIRED`.

Every delivery must identify:

- Files changed.
- Files added.
- Structural checks run.
- Behavior evaluations run or not run.
- Installation or host reload run or not run.
- Remaining limitations.

A successful package build is not a successful skill behavior evaluation.

## Project-history mining

Use this path when the evidence source is a project's commit history,
architecture/design documents, and code -- not a live interaction. Triggered
by `從專案提煉優化案例` (see `developing-skills/SKILL.md`). Same extraction
model, sanitization boundary, and delivery modes above; this section covers
what differs for a whole-project source.

### Auto-bounded scope

Do not read an entire commit history in detail. Identify significant nodes
first, then read details only for those:

1. Get the cheap overview: total commit count, tags/releases,
   `CHANGELOG.md`/release notes, `README`/`ARCHITECTURE`/ADR documents if
   present.
2. Rank candidate commits by signal: message keywords (refactor, redesign,
   fix, breaking, deprecate, migrate), large diffstat, or explicit mention in
   CHANGELOG/release notes/ADRs.
3. Cap detailed diff reading to a manageable count (a few dozen), prioritized
   in this order: commits the project's own release notes call out, then
   most-recent significant commits, then largest remaining diffs until the
   cap is reached. State the cap and what was excluded rather than silently
   truncating.
4. The user may override auto-bounding at any point with an explicit time
   range, tag range, or subdirectory; honor that instead of the default.

### Confidence discipline

Mark every extracted candidate `inferred` or `unknown` confidence, never
`observed`. Commit history and diffs show what changed, not what an agent or
human actually reasoned through, which Skill (if any) was in play, or
whether the change was even AI-assisted. Do not upgrade confidence based on
a plausible-sounding commit message alone.

### Third-party project caution

Analyzing someone else's public repository (a downloaded open-source
project) or the user's own private project both require the same
sanitization boundary above, plus `skill-authoring-sources.md`'s citation
rule: extract only the generalized engineering pressure, never copy source
text, code, or proprietary business logic as a rule. If a finding later
becomes a formal Skill reference, attribute the source project explicitly
rather than presenting the pattern as CloudSkill's own original discovery.

### Output

Same pipeline as interaction capture: `scripts/capture_eval_candidate.py`
when a CloudSkill repository is reachable, or
`.agents/skills/developing-skills/assets/export_eval_candidate.py` plus a
zip otherwise. Additionally produce one
`EVAL_MINING_REPORT.template.md`-based summary per mining pass (not one per
candidate) covering what was in scope, what was excluded by the cap, and
the candidate accounting -- bundle it alongside the candidate JSON files in
the same export. Prefix each candidate's `task_summary` with
`[project-history]` so a later batch reviewer can immediately distinguish
project-mined candidates from live-interaction candidates without opening
every file.
