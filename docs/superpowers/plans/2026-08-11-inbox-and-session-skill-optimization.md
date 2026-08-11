# Inbox and Session Skill Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the 45 manual-review records and current-session findings into deduplicated, behavior-tested improvements owned by existing CloudBox Skills while retaining the manual review workflow.

**Architecture:** Formal Behavior cases are the RED authority. Each candidate cluster is assigned to one primary Skill; shared routing cues remain in `using-cloudskill`, heavy rules remain in owner references, and mechanical archive/config rules remain in executable validators. Work proceeds in independently reviewable increments, beginning with the observed CloudBox evolution/release failures and then the domain/refactoring clusters.

**Tech Stack:** Markdown Skills/references, JSON Behavior cases and lifecycle records, Python deterministic validators, repository Runtime Eval tooling.

## Global Constraints

- Preserve `manual-review/`, unsupported retention, and manual legacy recovery until the user separately approves a stable replacement format.
- Never copy raw transcripts, identifying data, private endpoints, credentials, or project-specific implementation into formal Evals or Skills.
- Project-history evidence remains `inferred` or `unknown`; current-session executed failures may be `observed`.
- Add no new Skill unless an independently routable trigger remains after owner analysis.
- Every materially changed Skill gets its own RED, GREEN, adjacent regression, lifecycle evidence update, and review gate.
- Mechanical archive/config behavior is implemented and tested in scripts; Skills own judgment and stop/escalation rules.

### Task 1: CloudBox evolution intake discipline (O01–O03, O06)

**Files:**
- Modify: `evals/behavior/cases/developing-skills.json`
- Modify: `.agents/skills/developing-skills/SKILL.md`
- Modify: `.agents/skills/developing-skills/references/interaction-eval-capture.md`
- Modify: `.agents/skills/developing-skills/references/conversation-derived-optimization.md`
- Modify: `.agents/skills/developing-skills/lifecycle.json`
- Test: `scripts/validate_behavior_evals.py`, `scripts/validate_interaction_capture.py`

- [x] Add RED cases for producer/consumer bundle parity, whole-archive prevalidation, untrusted publication paths/resources, and explicit-Inbox private-term policy.
- [x] Run structural validation and one behavior baseline without the proposed Skill text; record exact omissions without claiming model GREEN.
- [x] Add the minimum owner rules: validate with the real consumer, plan an archive before publication, treat every imported name/path/resource as untrusted, and preserve config policy or disclose conservative fallback.
- [x] Re-run the same cases plus adjacent manual-review/legacy controls; update lifecycle evidence truthfully.
- [x] Commit the independently reviewable increment.

### Task 2: Exact-tip review and release closure (O04–O05)

**Files:**
- Modify: `evals/behavior/cases/runtime-evaluation-engineering.json`
- Modify: `.agents/skills/runtime-evaluation-engineering/SKILL.md`
- Modify: `evals/behavior/cases/coding-agent-project-governance.json`
- Modify: `.agents/skills/coding-agent-project-governance/SKILL.md`
- Modify: affected lifecycle records

- [x] Added exact-tip/release-closure regression cases; the no-Skill baseline already passed, so this is regression-only rather than claimed RED.
- [x] Record baseline behavior separately for evaluation validity and repository publication governance.
- [x] Audited both owners; baseline already contained the required closure, so no Skill prose was changed (`NO_CHANGE_JUSTIFIED`).
- [x] Verify adjacent documentation-only and bounded-patch controls do not trigger full release machinery.
- [x] Commit the increment.

### Task 3: Automation scope reduction and token-budget policy (O07, O10, O30)

**Files:**
- Modify: `evals/behavior/cases/agent-development-process.json`
- Modify: `.agents/skills/agent-development-process/SKILL.md`
- Modify: `evals/behavior/cases/development-process-tailoring.json`
- Modify: `.agents/skills/development-process-tailoring/SKILL.md`
- Modify: `evals/behavior/cases/runtime-evaluation-engineering.json`
- Modify: `.agents/skills/runtime-evaluation-engineering/SKILL.md`
- Modify: `.agents/skills/developing-skills/references/conversation-derived-optimization.md`
- Modify: affected lifecycle records

- [x] Audited the automation, lifecycle, and runtime-Eval owners; no new cases or owner edits were warranted (`NO_CHANGE_JUSTIFIED`).
- [x] Consolidated only the demonstrated token gap—deterministic filtering/clustering, hashes, exact-tip review, equivalent-evidence reuse, stop-on-blocker, and unchanged-wait suppression—in `developing-skills`.
- [x] The no-Skill baseline already handled manual redesign, transition-only reporting, checkpoint summaries, progressive loading versus cheap full reads, bounded safe automation, and changed status/evidence; these remained `NO_CHANGE_JUSTIFIED` without claiming new owner text.
- [x] Committed the demonstrated `developing-skills` increment; did not create duplicate owner rules.

### Task 4: Host/plugin and continuation provenance (O08–O09, O26)

**Files:**
- Modify: `evals/behavior/cases/coding-agent-project-governance.json`
- Modify: `evals/behavior/cases/using-cloudskill.json`
- Modify: `.agents/skills/coding-agent-project-governance/SKILL.md`
- Modify: `.agents/skills/using-cloudskill/SKILL.md` or its routing reference only when RED proves a gap

- [x] Audited checkout/cache/session, branch/worktree/remote, and generic-versus-specific routing behavior; the no-Skill baseline passed (`NO_CHANGE_JUSTIFIED`).
- [x] Verified no false completion or router over-selection; no Skill/case edit or cluster commit was made.

### Task 5: Native/code/framework clusters (O11–O20, O24–O25, O29)

**Files:**
- Modify only affected existing Skill Behavior case files and owner references after per-owner RED.
- Candidate owners: `code-review`, `cross-platform-native-architecture`, `framework-design`, `software-quality-iso25010`, `development-process-tailoring`.

- [x] Deduplicate request identity, parser validation, worker shutdown, readiness/completion, transport capability, emulator evidence, registry drift, design-host ABI, real-time alignment, release-matrix, process identity, escape-sensitive editing, and OS-integration ownership candidates.
- [x] Ran a pre-change static/manual semantic gap audit per owner and a combined targeted semantic GREEN; no historical model-backed RED is claimed.
- [x] Keep protocol constants, product topology, platform secrets, and local paths out of reusable content.
- [x] Commit each owner independently after adjacent regression.

### Task 6: Brownfield and durable-state clusters (O21–O22, O27–O28)

**Files:**
- Modify only affected cases/references for `safe-incremental-refactoring`, `application-client-server-architecture`, `document-governance`, and optionally `software-quality-iso25010` after RED.

- [x] Consolidate extraction seam/test-shape/bootstrap/auth boundaries into a compact refactoring decision table.
- [x] Keep durability divergence, schema-versus-product version, immutable history/compensation, and post-commitment lifecycle as four distinct architecture Evals.
- [x] Added historical container-versus-observation governance; proportional self-audit was already covered and remained unchanged (`NO_CHANGE_JUSTIFIED`).
- [x] Committed each changed owner independently after focused contract validation and later combined semantic GREEN.

### Task 7: Inbox accounting, full regression, and review

**Files:**
- Modify: `CLOUDSKILL_AGENT_HANDOFF.md`
- Modify: `docs/CLOUDSKILL_CHANGE_HISTORY.md`
- Add: release/evolution evidence appropriate to the eventual version decision

- [x] Record each source candidate as promoted, merged, held, reassigned, or rejected without deleting the private source evidence.
- [x] Run structural, routing, Behavior contract, install, packaging, and full deterministic checks twice.
- [x] Ran targeted semantic GREEN for every changed owner and recorded provider-backed Runtime Eval as `NOT RUN`.
- [ ] Obtain exact-tip independent review selected by risk; correct findings through new RED/GREEN increments. (First review returned four Medium evidence/lineage findings; corrections are in progress.)
- [ ] Present the candidate and evidence for user approval before version, push, or release.
