---
name: developing-skills
description: Use when creating, editing, splitting, merging, evaluating, releasing, or conversation-mining CloudSkill skills, including turning available prior interactions and user corrections into sanitized routing and behavior evidence or a reviewable replacement package.
---

# Developing CloudSkill Skills

## Core principle

A skill change is successful only when it improves agent routing or behavior on repeatable cases. More documentation is not evidence of improvement.

Read:

- `references/behavior-driven-skill-development.md`
- `references/skill-authoring-sources.md` when reviewing external influences or attribution.
- `references/interaction-eval-capture.md` when converting a live interaction into a private Eval candidate or reviewing an Eval Inbox.
- `references/conversation-derived-optimization.md` when mining multiple available interactions or producing an optimized overlay, branch, or release candidate.
- `references/skill-lifecycle-standard.md` when creating, promoting, reviewing, deprecating, or evolving a Skill.

Use:

- `assets/SKILL_CONTRACT.template.md`
- `assets/BEHAVIOR_EVAL_CASE.template.json`
- `assets/INTERACTION_EVAL_CANDIDATE.template.json`
- `assets/export_eval_candidate.py` when no CloudSkill repository is reachable on this machine.
- `assets/EVAL_MINING_REPORT.template.md`
- `assets/SKILL_PROPOSAL.template.md`
- `assets/SKILL_LIFECYCLE.template.json`
- `assets/SKILL_RELEASE_EVIDENCE.template.md`

## Interaction capture shorthand

## Standardized lifecycle

Use one lifecycle for every Skill:

`draft -> experimental -> active -> stable -> deprecated`

- `draft`: ownership and non-trigger boundaries are still being defined.
- `experimental`: RED evidence and minimum routing/behavior cases exist, but release evidence is incomplete.
- `active`: the same cases are GREEN, adjacent regressions pass, and executable evidence exists.
- `stable`: the Skill has remained unambiguous across releases and its context/maintenance cost is acceptable.
- `deprecated`: new routing moves to an explicit replacement or ordinary workflow.

Use the repository command rather than hand-building inconsistent folders:

```bash
python scripts/manage_skill.py new \
  --name example-skill \
  --description "Use when ..." \
  --display-name "Example Skill" \
  --short-description "..." \
  --case-prefix EXAMPLE
```

Before commit:

```bash
python scripts/manage_skill.py refresh --all
python scripts/manage_skill.py audit --check
python scripts/run_all_checks.py
```

A stage change is a release decision. It requires the gates in
`references/skill-lifecycle-standard.md`; Markdown validity alone cannot promote a Skill.


Treat these user phrases as explicit capture requests:

- `整理成正向案例` — preserve a successful route and the behaviors that made the result useful.
- `整理成負向案例` — preserve the observed failure, user correction, and future required/forbidden behavior.

For either phrase:

1. Capture only the turns needed to understand the task, result, and correction; do not save the raw or complete transcript.
2. Apply mandatory sanitization before writing. Generalize organization, customer, person, project, product, equipment, site, account, address, path, URL, schedule, recipe, safety-limit, and other identifying data.
3. Distinguish observed skill loading from inferred or unknown routing. Do not claim hidden runtime traces.
4. Read project `.cloudskill/config.local.json`, then user `~/.cloudskill/config.json`. Do not guess an output path when no valid configuration exists.
5. Create a draft from `INTERACTION_EVAL_CANDIDATE.template.json`. If a configuration resolves to a reachable CloudSkill repository, use its `scripts/capture_eval_candidate.py` helper. If none resolves (a disconnected/external session with no reachable CloudSkill repository on this machine), use this Skill's own `assets/export_eval_candidate.py` instead — see `references/interaction-eval-capture.md` for the export/transfer/import flow.
6. Save a sanitization-safe record to the private candidate queue. Route uncertain records to `manual-review`.
7. Do not modify formal Evals, skills, commits, tags, branches, or remotes during capture.

A captured candidate is evidence to review, not proof that routing or behavior passed. Batch conversion requires deduplication, owner analysis, a repeatable prompt, required and forbidden behavior, and an explicit RED/GREEN decision.

## Historical interaction mining and optimization requests

Use this path when the user asks to optimize one or more skills from past conversations, previous corrections, memories, exported transcripts, or an Eval Inbox.

1. **Inventory accessible evidence.** List the current conversation, available memory/context, uploaded exports, configured Eval Inbox, and connected repository evidence that were actually read. Mark unavailable history explicitly.
2. **Sanitize before synthesis.** Remove or generalize organization, customer, person, project, product, equipment, site, account, address, local path, URL, schedule, recipe, safety limit, credential, and other identifying data.
3. **Extract reusable pressure.** Preserve failure boundaries such as state ownership, timeout, late completion, retry safety, stale state, lifecycle, evidence denominator, audience transformation, release control, or overengineering. Do not preserve incidental names.
4. **Cluster and deduplicate.** Merge semantically equivalent corrections. Separate routing failures, behavior omissions, artifact problems, unsupported claims, and project-only preferences.
5. **Locate the authoritative owner.** Update the smallest existing skill, router, reference, or validator that owns the pressure. Do not modify every skill merely because the source conversation mentioned several domains.
6. **Establish RED evidence.** Add routing, recognition, application, counterexample, or discipline cases that reproduce the observed failure before changing skill instructions.
7. **Make the smallest responsible change.** Prefer routing metadata, one decision rule, one safeguard, or one reference over a broad rewrite.
8. **Regress adjacent routes.** Verify that code review does not become process tailoring, equipment modeling does not become resource architecture, agent product design does not become repository governance, and trivial tasks do not invoke CloudBox.
9. **Produce a reviewable delivery.** Use a branch/PR only when write access is available and the user authorized it. Otherwise produce a deterministic overlay or patch that preserves repository paths.
10. **Report execution truthfully.** Distinguish structural validation, model behavior execution, repository write, installation, and host/plugin reload. A generated package is not proof that ChatGPT loaded the updated skill.

Never claim complete account-wide conversation access unless an explicit export or source was actually read. Never store raw transcripts in the repository. Never claim a branch, PR, test, install, or release succeeded after a connector or local command failed.

## Workflow

### 1. Define the observed problem

Classify the need as one or more of:

- Skill fails to trigger.
- Skill triggers too broadly.
- Wrong adjacent skill is selected.
- Required analysis or artifact is omitted.
- A prohibited action or unsupported claim occurs.
- Instructions are duplicated or owned by the wrong skill.
- A mechanical rule should be automated rather than documented.
- A live interaction should be preserved as a positive or negative Eval candidate.
- Multiple available interactions should be mined into a sanitized optimization candidate.

Preserve the source evidence and confidence level. A historical project demonstrates a solved pressure; it does not make every historical implementation choice normative.

### 2. Locate the authoritative owner

Before adding a skill:

- Search existing skill names, descriptions, references, assets, routing cases, and repository guidance.
- Expand an existing owner when trigger, audience, and lifecycle are the same.
- Split a skill only when triggers or required behavior have become independently routable.
- Keep project-specific conventions in repository instructions rather than global skills.
- Put enforceable syntax and consistency rules in scripts or CI.

### 3. Establish RED evidence before editing

Create or select repeatable cases before changing the skill:

- **Routing case:** Which skill should or should not load?
- **Recognition case:** Does the agent identify the relevant pressure?
- **Application case:** Does it apply the method to a new scenario?
- **Counterexample:** Does it avoid the skill when another route is correct?
- **Discipline case:** Does it preserve the rule under schedule, authority, sunk-cost, or operational pressure?
- **Reference case:** Can it retrieve and correctly use the required information?

Run or record the current behavior without the proposed change. Capture the exact omission, wrong route, unsupported claim, or rationalization. If no observable failure exists, do not claim the edit fixes behavior.

### 4. Define the skill contract

Specify:

- Trigger and non-trigger conditions.
- Required and forbidden behavior.
- Required output or artifact.
- Evidence and verification expectations.
- Stop or escalation conditions.
- Required and optional companion skills.
- Baseline failure the change is intended to correct.

The frontmatter description is a routing contract. It must begin with `Use when`, describe triggering conditions, and avoid summarizing the workflow.

### 5. Make the smallest responsible change

Prefer this order:

1. Description correction.
2. Routing or counterexample evaluation.
3. One explicit decision rule or safeguard.
4. Common mistake, red flag, or stop condition.
5. Supporting reference or asset.
6. New skill only when independent routing is justified.

Keep judgment and decision flow in `SKILL.md`; move heavy reference material and reusable templates to supporting files. Do not duplicate mutable rules across skills, `AGENTS.md`, and documentation.

### 6. Verify GREEN behavior

Re-run the same cases after the change and verify:

- Correct routing.
- Required behavior and artifacts.
- Absence of forbidden behavior.
- Truthful evidence reporting.
- Reasonable scope and token cost.

A valid Markdown file or passing structural validator is not a behavioral pass.

### 7. Refactor and regress

Test adjacent skills, negative controls, simple tasks, and multi-skill composition. Record new loopholes or rationalizations and close only the ones demonstrated by evidence. Re-run prior cases after every change.

### 8. Release with evidence

Before release:

- Run structural, description, routing, behavior-case, documentation, and install-smoke checks.
- Record behavior execution as PASS, FAIL, BLOCKED, NOT RUN, or MANUAL REQUIRED.
- Update version, changelog, manifest, and release evidence.
- Use a single-purpose branch and reversible commit.

## Common mistakes

- Writing a new skill because one project had a unique folder or class name.
- Editing first and inventing evaluation cases afterward.
- Treating routing coverage as proof that the workflow is followed.
- Copying an external methodology without adapting it to CloudSkill's architecture and governance scope.
- Adding prose for a rule that a validator can enforce deterministically.
- Declaring behavior tests passed when only schemas or case files were validated.
- Claiming all past conversations were read when only current context or summaries were available.
- Claiming a GitHub branch or PR was created after a connector returned an authorization error.
- Embedding a user's local path or organization-specific terms into a reusable global skill.

## Required output

1. Accessible evidence inventory and unavailable sources
2. Observed failure and evidence
3. Existing owner and overlap decision
4. Sanitization and deduplication result
5. Skill contract
6. RED baseline case and result
7. Minimal change
8. GREEN result
9. Adjacent-skill regression
10. Structural and install checks
11. Delivery form: branch/PR, overlay, patch, or MANUAL_REQUIRED
12. Release status and remaining limitations

For interaction capture, the required output is the saved candidate path or a `MANUAL_REQUIRED` result; do not claim that a formal Eval or skill change was completed.
