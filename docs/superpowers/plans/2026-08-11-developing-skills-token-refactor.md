# Developing Skills Token Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the default-loaded size of `developing-skills` while preserving its behavior, and clarify how the CloudBox Plan Owner proportionally delegates detailed planning without surrendering authority.

**Architecture:** Keep universal decisions and safeguards in `SKILL.md`; place conditional mechanics in direct, explicitly routed references. A deterministic validator measures the main file and proves every moved contract remains reachable from a named workflow before semantic and full-suite regression.

**Tech Stack:** Markdown Skills/references, JSON Behavior cases and lifecycle records, Python 3 repository validators, Git.

## Global Constraints

- Do not change the Skill name, description, lifecycle stage, public routing contract, or manual ZIP/legacy support.
- Do not version, push, merge, or release in this increment.
- Preserve privacy, evidence-truth, RED/GREEN, authoritative-owner, and stop conditions in default-loaded text when they apply to every workflow.
- Report provider-backed Runtime Eval as `NOT RUN` unless it is actually executed.
- Treat token counts as comparative estimates, not provider billing measurements.
- Keep `development-process-tailoring` as the only lifecycle/plan authority; generic planning tools produce bounded details only.

---

### Task 1: Baseline and refactor contract

**Files:**
- Modify: `evals/behavior/cases/developing-skills.json`
- Modify: `.agents/skills/developing-skills/lifecycle.json`
- Create: `scripts/validate_skill_context_budget.py`
- Modify: `scripts/run_all_checks.py`

**Interfaces:**
- Consumes: canonical Skill path and its Markdown direct-reference links.
- Produces: deterministic size metrics and required-workflow/reference assertions used by Tasks 2–3.

- [ ] **Step 1: Record the pre-change baseline**

Run a small read-only measurement using UTF-8 bytes, whitespace-delimited words,
physical lines, and `ceil(bytes / 4)` as an explicitly approximate token value.
Save the result in the eventual evidence record, not in mutable Skill metadata.

- [ ] **Step 2: Add failing structural cases**

Create `scripts/validate_skill_context_budget.py` so it requires the main Skill
to route these conditional workflows to direct references: interaction capture,
multi-interaction/project-history mining, and lifecycle/release evidence. Require
universal privacy, RED/GREEN, authoritative-owner, and evidence-truth invariants
to remain in `SKILL.md`. Set the maximum main-file byte budget below the current
baseline but only after identifying content that can be moved without loss.

- [ ] **Step 3: Verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_skill_context_budget.py
```

Expected: FAIL because the current main file exceeds the new budget or lacks
the explicit lifecycle/release reference route. Confirm the failure is caused
by the intended refactor contract.

- [ ] **Step 4: Register the validator**

Add the validator to `scripts/run_all_checks.py` and add focused Behavior cases
that require correct conditional-reference selection without leaking the
expected answer into prompts. Register those case IDs in the lifecycle record.

- [ ] **Step 5: Commit the RED increment**

```bash
git add scripts/validate_skill_context_budget.py scripts/run_all_checks.py evals/behavior/cases/developing-skills.json .agents/skills/developing-skills/lifecycle.json
git commit -m "test: define developing skill context budget"
```

### Task 2: Progressive-disclosure refactor

**Files:**
- Modify: `.agents/skills/developing-skills/SKILL.md`
- Modify: `.agents/skills/developing-skills/references/interaction-eval-capture.md`
- Modify: `.agents/skills/developing-skills/references/conversation-derived-optimization.md`
- Modify: `.agents/skills/developing-skills/references/skill-lifecycle-standard.md`
- Modify: `SKILL_MANIFEST.json`

**Interfaces:**
- Consumes: Task 1 workflow/reference assertions and size budget.
- Produces: a smaller default Skill whose direct references own conditional procedures.

- [ ] **Step 1: Move only conditional mechanics**

Keep the core principle, reference router, universal safeguards, owner decision,
RED/GREEN loop, minimal-change order, adjacent regression, and truthful release
boundary in `SKILL.md`. Move detailed capture steps, mining delivery formats,
and lifecycle/release mechanics into their existing authoritative references.

- [ ] **Step 2: Remove duplicated mutable text**

For each moved rule, retain one authority. Use a short imperative link in
`SKILL.md` that says when the reference is mandatory; do not preserve a second
full checklist in the main file.

- [ ] **Step 3: Verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_skill_context_budget.py
python3 scripts/validate_behavior_evals.py
python3 scripts/manage_skill.py audit --check
python3 scripts/validate_pack.py
```

Expected: all PASS; manifest refresh is committed if content hashes change.

- [ ] **Step 4: Run focused semantic GREEN**

Execute the new cases plus `DEVSK-BEH-011` through `DEVSK-BEH-014` against the
refactored Skill and direct references. Record case-level PASS/FAIL and state
that provider-backed corpus execution is `NOT RUN` unless actually invoked.

- [ ] **Step 5: Commit the refactor**

```bash
git add .agents/skills/developing-skills SKILL_MANIFEST.json
git commit -m "refactor: reduce developing skill context cost"
```

### Task 3: Proportional planning composition

**Files:**
- Modify: `evals/behavior/cases/development-process-tailoring.json`
- Modify: `.agents/skills/development-process-tailoring/SKILL.md`
- Modify: `.agents/skills/development-process-tailoring/lifecycle.json`
- Modify: `SKILL_MANIFEST.json`

**Interfaces:**
- Consumes: existing lifecycle plan, risk/replan, resume, and review-assurance contracts.
- Produces: one authoritative proportional-planning rule and focused Behavior evidence.

- [ ] **Step 1: Add RED behavior cases**

Add cases requiring lightweight planning for small stable work, bounded detailed
planning for an approved medium increment, and lifecycle-first stage planning
for uncertain/high-risk work. Require new risk to invalidate only affected
detailed steps while preserving unaffected evidence. Forbid dual plan authority.

- [ ] **Step 2: Verify RED**

Run the cases without the proposed Skill change and record the exact omission.
If baseline behavior already satisfies every case, mark the change
`NO_CHANGE_JUSTIFIED` and do not add duplicate prose.

- [ ] **Step 3: Make the minimum GREEN change**

Only if RED is demonstrated, add one compact proportional-planning section to
`development-process-tailoring` and register its cases in lifecycle evidence.

- [ ] **Step 4: Verify and commit independently**

```bash
python3 scripts/validate_behavior_evals.py
python3 scripts/manage_skill.py audit --check
python3 scripts/validate_pack.py
git add .agents/skills/development-process-tailoring evals/behavior/cases/development-process-tailoring.json SKILL_MANIFEST.json
git commit -m "feat: tailor detailed planning by risk"
```

### Task 4: Evidence, full regression, and review

**Files:**
- Create: `docs/evolution/2026-08-11-developing-skills-token-refactor-evidence.md`
- Modify: `CLOUDSKILL_AGENT_HANDOFF.md`
- Modify: `docs/CLOUDSKILL_CHANGE_HISTORY.md`
- Modify: `docs/superpowers/plans/2026-08-11-developing-skills-token-refactor.md`

**Interfaces:**
- Consumes: before/after metrics, structural results, semantic verdicts, and exact source tip.
- Produces: reviewable candidate evidence and continuation state for both independent increments.

- [ ] **Step 1: Record comparative evidence**

Record before/after lines, bytes, words, approximate tokens, percentage change,
moved authorities, focused semantic results, full-suite status, and explicit
`NOT RUN` items. Do not claim provider billing savings from the estimate.

- [ ] **Step 2: Run the complete deterministic suite**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_all_checks.py
git diff --check
```

Expected: PASS and clean diff formatting.

- [ ] **Step 3: Obtain independent exact-tip review**

Review `origin/main...HEAD` for information loss, hidden mandatory safeguards,
reference-routing ambiguity, duplicated authority, privacy regression, and
misleading token claims. Correct every High/Medium finding through a focused
RED/GREEN increment.

- [ ] **Step 4: Update handoff and execution status**

Record exact commit/evidence state without marking intentionally skipped or
`NO_CHANGE_JUSTIFIED` work as performed.

- [ ] **Step 5: Commit evidence and present candidate**

```bash
git add docs/evolution/2026-08-11-developing-skills-token-refactor-evidence.md CLOUDSKILL_AGENT_HANDOFF.md docs/CLOUDSKILL_CHANGE_HISTORY.md docs/superpowers/plans/2026-08-11-developing-skills-token-refactor.md
git commit -m "docs: record developing skill token refactor"
```

Present the candidate for user approval. Do not version, push, merge, or release.
