---
name: developing-skills
description: Use when creating, editing, splitting, merging, evaluating, or releasing CloudSkill skills, descriptions, references, assets, routing cases, or behavior tests.
---

# Developing CloudSkill Skills

## Core principle

A skill change is successful only when it improves agent routing or behavior on repeatable cases. More documentation is not evidence of improvement.

Read:

- `references/behavior-driven-skill-development.md`
- `references/skill-authoring-sources.md` when reviewing external influences or attribution.

Use:

- `assets/SKILL_CONTRACT.template.md`
- `assets/BEHAVIOR_EVAL_CASE.template.json`

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

## Required output

1. Observed failure and evidence
2. Existing owner and overlap decision
3. Skill contract
4. RED baseline case and result
5. Minimal change
6. GREEN result
7. Adjacent-skill regression
8. Structural and install checks
9. Release and remaining limitations
