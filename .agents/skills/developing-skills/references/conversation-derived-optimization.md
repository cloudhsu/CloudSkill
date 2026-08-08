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
