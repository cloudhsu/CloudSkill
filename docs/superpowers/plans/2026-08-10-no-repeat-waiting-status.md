# No-repeat Waiting Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent coding agents from repeatedly reporting unchanged waiting, paused, or blocked states and from asking again about small, already-authorized work.

**Architecture:** Keep the rule in the repository-wide `AGENTS.md`, the authoritative always-loaded instruction layer. Do not duplicate it in the current-session handoff or a Skill.

**Tech Stack:** Markdown repository instructions and the existing Python documentation validator.

## Global Constraints

- Report evidence truthfully; do not hide a real state change or required user decision.
- Automatic continuation alone is not a state change.
- Small, unambiguous, already-authorized work proceeds without reconfirmation.

---

### Task 1: Add the collaboration rule

**Files:**
- Modify: `AGENTS.md`
- Verify: `scripts/validate_evolution_handoff.py`

**Interfaces:**
- Consumes: the collaboration-position rules in `AGENTS.md`.
- Produces: one repository-wide communication rule for all coding-agent work.

- [x] **Step 1: Add the approved rule**

Add a concise paragraph under `## Collaboration position` requiring one-time
waiting-state reporting, defining real state changes, and allowing direct
execution of small already-authorized work.

- [x] **Step 2: Verify documentation and diff integrity**

Run:

```bash
/usr/local/bin/python3.13 scripts/validate_evolution_handoff.py
git diff --check
```

Expected: validator success and no whitespace errors.

- [x] **Step 3: Commit**

```bash
git add AGENTS.md docs/superpowers/plans/2026-08-10-no-repeat-waiting-status.md
git commit -m "docs: avoid repeated waiting status updates"
```
