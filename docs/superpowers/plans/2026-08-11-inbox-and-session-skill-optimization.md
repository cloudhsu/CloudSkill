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

- [x] Add RED cases proving an old-tip PASS and version-only update cannot authorize release.
- [x] Record baseline behavior separately for evaluation validity and repository publication governance.
- [x] Add exact-tip invalidation/accumulated-finding closure to the Eval owner and PR/CI/merge/tag/Release/post-record closure to repository governance.
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

- [x] Add RED cases for repeatedly patching an undefined authority/concurrency/filesystem boundary, repetitive unchanged waiting updates, full rereads of large unchanged handoffs, model review before deterministic filtering, and continuing a panel after a blocking finding.
- [x] Add a manual-fallback/redesign stop condition to the agent-product owner.
- [x] Add transition-only monitoring/reporting and checkpoint-summary guidance to the lifecycle owner while retaining requested status responses.
- [x] Require deterministic filtering, candidate clustering, source/diff hashes, exact-tip review, equivalent-evidence reuse, and stop-on-blocker before additional model calls in the Eval/Skill-evolution owners.
- [x] Require progressive context loading: current checkpoint/index first, then only the referenced section/file needed for the active failure layer; full rereads remain allowed when authority or lineage cannot otherwise be established.
- [x] Verify counterexamples for bounded safe automation, materially changed status, genuinely changed evidence, and a small handoff whose full read is cheaper than routing overhead.
- [x] Commit the increment.

### Task 4: Host/plugin and continuation provenance (O08–O09, O26)

**Files:**
- Modify: `evals/behavior/cases/coding-agent-project-governance.json`
- Modify: `evals/behavior/cases/using-cloudskill.json`
- Modify: `.agents/skills/coding-agent-project-governance/SKILL.md`
- Modify: `.agents/skills/using-cloudskill/SKILL.md` or its routing reference only when RED proves a gap

- [x] Add RED cases distinguishing checkout, installed cache, active session, branch/worktree, remote, and generic-versus-specific Skill routing.
- [x] Add only missing provenance/reload and routing rules; reuse existing plugin-coexistence guidance.
- [x] Verify no false completion claim and no router over-selection.
- [x] Commit the increment.

### Task 5: Native/code/framework clusters (O11–O20, O24–O25, O29)

**Files:**
- Modify only affected existing Skill Behavior case files and owner references after per-owner RED.
- Candidate owners: `code-review`, `cross-platform-native-architecture`, `framework-design`, `software-quality-iso25010`, `development-process-tailoring`.

- [x] Deduplicate request identity, parser validation, worker shutdown, readiness/completion, transport capability, emulator evidence, registry drift, design-host ABI, real-time alignment, release-matrix, process identity, escape-sensitive editing, and OS-integration ownership candidates.
- [x] Run one RED/GREEN cycle per owner Skill, not per source record.
- [x] Keep protocol constants, product topology, platform secrets, and local paths out of reusable content.
- [x] Commit each owner independently after adjacent regression.

### Task 6: Brownfield and durable-state clusters (O21–O22, O27–O28)

**Files:**
- Modify only affected cases/references for `safe-incremental-refactoring`, `application-client-server-architecture`, `document-governance`, and optionally `software-quality-iso25010` after RED.

- [x] Consolidate extraction seam/test-shape/bootstrap/auth boundaries into a compact refactoring decision table.
- [x] Keep durability divergence, schema-versus-product version, immutable history/compensation, and post-commitment lifecycle as four distinct architecture Evals.
- [x] Add historical container-versus-observation version governance and proportional pre-completion self-audit cases.
- [x] Commit each owner independently after GREEN and adjacent regression.

### Task 7: Inbox accounting, full regression, and review

**Files:**
- Modify: `CLOUDSKILL_AGENT_HANDOFF.md`
- Modify: `docs/CLOUDSKILL_CHANGE_HISTORY.md`
- Add: release/evolution evidence appropriate to the eventual version decision

- [x] Record each source candidate as promoted, merged, held, reassigned, or rejected without deleting the private source evidence.
- [x] Run structural, routing, Behavior contract, install, packaging, and full deterministic checks twice.
- [x] Run behavior execution for every changed Skill; record PASS/FAIL/BLOCKED/NOT RUN truthfully.
- [ ] Obtain exact-tip independent review selected by risk; correct findings through new RED/GREEN increments. (First review returned four Medium evidence/lineage findings; corrections are in progress.)
- [ ] Present the candidate and evidence for user approval before version, push, or release.
