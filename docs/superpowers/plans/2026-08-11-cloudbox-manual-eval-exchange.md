# CloudBox Manual Eval Exchange Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Withdraw unreleased controlled execution and make versioned multi-ZIP manual Eval exchange the single supported workflow.

**Architecture:** Export creates a manifest-bound deterministic filename. Import scans a private Inbox batch, validates filename/manifest/version/payload identity, and routes candidates without model or repository mutation. Controlled execution research remains future-only documentation.

**Tech Stack:** Python 3.7-compatible standard library, ZIP/JSON bundle contract, repository-native validators.

## Global Constraints

- Do not delete user ZIPs automatically.
- Import never modifies formal Evals, Skills, Git, or external systems.
- Preserve manual importer and Git evolution-source synchronization from 6.1/6.2.
- Remove every executable and routing surface introduced only for controlled tools.
- Use `apply_patch` for repository edits and retain review history in handoff/change history.

### Task 1: Filename and batch RED/GREEN

- [ ] Add a renamed-supported-bundle RED to `scripts/validate_interaction_capture.py`.
- [ ] Require `zip_path.name == bundle_filename(manifest)` before payload extraction.
- [ ] Persist/reuse `export_agent_name` beside `export_project_name` and verify exporter parity.
- [ ] Cover a mixed multi-ZIP batch and confirm deterministic queue totals and no model calls.
- [ ] Run `validate_eval_bundle_contract.py` and `validate_interaction_capture.py`; commit.

### Task 2: Withdraw unreleased controlled execution

- [ ] Delete new registry, tool schemas, broker/action/adapter code, fixtures, validators, Behavior cases, and controlled-tool product docs/plans/specs.
- [ ] Revert controlled-tool-only additions in lifecycle profiles, orchestration, Skills, README/INSTALL/docs, and `run_all_checks.py` to `origin/main` semantics.
- [ ] Replace future adapter notes with a concise research record including immutable targets, OS locking, secure staging, NAS limits, and the fault matrix.
- [ ] Preserve this manual-exchange spec/plan and truthful handoff/change history.

### Task 3: Regression and review

- [ ] Run focused importer/exporter validators and `git diff --check`.
- [ ] Run `python3 scripts/run_all_checks.py` twice.
- [ ] Review the exact diff for any remaining executable controlled-tool symbol or product claim.
- [ ] Commit the manual-only candidate and start fresh release assurance; do not version or publish until PASS.
