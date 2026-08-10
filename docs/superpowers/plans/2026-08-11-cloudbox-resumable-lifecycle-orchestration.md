# CloudBox Resumable Lifecycle Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build a composable, planning-capable, interruption-safe process owner that adapts work to risk and resumes long-running AI-agent engineering without repeating side effects or expanding authority.

**Architecture:** Add pure lifecycle/profile and plan contracts, then a durable atomic state store, then feedback/replanning and reconciliation. Integrate Review Assurance through a narrow adapter and reuse existing Task Continuity contracts instead of duplicating them.

**Tech Stack:** Python 3.11 standard library, JSON Schema, atomic filesystem rename, Git CLI fixtures, existing Task Continuity and Review Assurance contracts.

## Global Constraints

- The lifecycle is a graph, not a fixed waterfall.
- development-process-tailoring owns lifecycle and execution planning; technical Skills own technical decisions.
- Defaults are iterative_incremental for development and eval_driven_evolution for Skill evolution.
- Evidence, not iteration count, controls exit.
- Resume begins read-only and never expands authority.
- Timeout is not proof of failure; reconcile late completion before retry.
- One durable work item has one state-transition writer at a time.
- Deterministic no-change and reconciliation paths make zero hosted calls.
- Secrets, private URLs, credentials, and raw transcripts remain outside public state.

---

### Task 1: Freeze lifecycle and interruption RED cases

**Files:**
- Create: evals/agent/lifecycle-orchestration-cases.json
- Create: evals/agent/contracts/lifecycle-profile.schema.json
- Create: evals/agent/contracts/lifecycle-plan.schema.json
- Create: evals/agent/contracts/lifecycle-work-state.schema.json
- Create: scripts/validate_lifecycle_orchestration.py
- Modify: scripts/run_all_checks.py

**Interfaces:**
- Cases expose pressure, expected_profiles, failure, expected_reentry, forbidden_transitions, and expected_invalidations.
- Validator exposes main() -> int.

- [ ] **Step 1: Add profile and re-entry RED cases**

Cover local reversible edit, unstable-feedback feature, unknown-feasibility spike, hardware/software hybrid, urgent hotfix, brownfield migration, test-harness defect, design defect, and state-authority architecture defect.

- [ ] **Step 2: Add planning and interruption RED cases**

Cover risk increase without replan, stale plan execution, unrelated evidence discarded, duplicate external action after restart, timeout/late completion, paused mislabeled blocked, authority expansion, two coordinators, cancellation, budget exhaustion, unsupported schema, and deployment mislabeled operational success.

- [ ] **Step 3: Run RED**

Run: python3 scripts/validate_lifecycle_orchestration.py

Expected: FAIL with missing lifecycle_orchestration_contract.

- [ ] **Step 4: Register and commit RED**

~~~bash
git add evals/agent/lifecycle-orchestration-cases.json evals/agent/contracts/lifecycle-profile.schema.json evals/agent/contracts/lifecycle-plan.schema.json evals/agent/contracts/lifecycle-work-state.schema.json scripts/validate_lifecycle_orchestration.py scripts/run_all_checks.py
git commit -m "test: freeze lifecycle orchestration red cases"
~~~

### Task 2: Implement profile selection and stage contracts

**Files:**
- Create: config/lifecycle-profiles.json
- Create: scripts/lifecycle_orchestration_contract.py
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- load_profiles(path: Path) -> dict
- select_profiles(pressure: dict, profiles: dict) -> list[str]
- compose_stages(profile_ids: list[str], profiles: dict) -> list[dict]
- Each stage exposes input, owner, artifacts, evidence, review_level, exit_gate, handoff, and reentry.

- [ ] **Step 1: Add failing default-selection assertions**

~~~python
assert select_profiles({"work_type":"development","risk":"low"}, profiles) == ["iterative_incremental"]
assert select_profiles({"work_type":"skill_evolution"}, profiles) == ["eval_driven_evolution"]
assert "discovery_spike" in select_profiles({"technical_uncertainty":"high"}, profiles)
assert "stage_gated" in select_profiles({"safety":"high"}, profiles)
~~~

- [ ] **Step 2: Implement deterministic pressure routing**

Allow concurrent profiles by workstream. Do not apply stage_gated globally merely because one interface baseline requires it.

- [ ] **Step 3: Add anti-oscillation rule**

Recomposition requires a new evidence hash and declared trigger; record old/new topology and exit condition.

- [ ] **Step 4: Run and commit**

~~~bash
python3 scripts/validate_lifecycle_orchestration.py
git add config/lifecycle-profiles.json scripts/lifecycle_orchestration_contract.py scripts/validate_lifecycle_orchestration.py
git commit -m "feat: select composable lifecycle profiles"
~~~

### Task 3: Implement versioned lifecycle and execution plans

**Files:**
- Create: scripts/lifecycle_plan_contract.py
- Modify: evals/agent/contracts/lifecycle-plan.schema.json
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- create_plan(work_id: str, profiles: list[str], stages: list[dict], source_hash: str) -> dict
- validate_plan(plan: dict) -> list[str]
- replan(plan: dict, trigger: dict, risk: dict, impact: dict) -> dict
- Execution tasks expose task_id, owner, dependencies, inputs, outputs, risk_class, evidence, review_level, checkpoint, retry, rollback, and authority.

- [ ] **Step 1: Add RED assertions for plan creation**

Reject missing owners, dependency cycles, duplicate task IDs, undefined outputs, absent rollback for consequential tasks, and architecture decisions embedded as unexplained implementation assumptions.

- [ ] **Step 2: Add risk-driven replan RED assertions**

A changed authority boundary must increment revision, invalidate affected architecture/downstream tasks, raise review level, preserve unrelated evidence, and request new authority for expanded side effects.

- [ ] **Step 3: Implement immutable revision lineage**

Every plan has plan_id, revision, based_on_revision, trigger, source/risk hashes, added/removed/invalidated tasks, reused evidence, and authority_required. Reject execution from superseded revisions.

- [ ] **Step 4: Run and commit**

~~~bash
python3 scripts/validate_lifecycle_orchestration.py
git add scripts/lifecycle_plan_contract.py evals/agent/contracts/lifecycle-plan.schema.json scripts/validate_lifecycle_orchestration.py
git commit -m "feat: plan and replan lifecycle work by risk"
~~~

### Task 4: Implement earliest-failure classification and evidence invalidation

**Files:**
- Modify: scripts/lifecycle_orchestration_contract.py
- Modify: scripts/lifecycle_plan_contract.py
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- classify_failure(observation: dict) -> str
- invalidate_evidence(plan: dict, changed_layer: str, changed_hashes: set[str]) -> dict

- [ ] **Step 1: Add one RED case per re-entry owner**

A grader defect returns to verification_system; component interface defect to design; state-authority/recovery defect to architect; invalid acceptance criterion to analyze; wrong problem context to explore.

- [ ] **Step 2: Implement mechanism-based classification**

Require observed_behavior, expected_contract, failed_mechanism, and source_hash. Reject evidence that only says “test failed.”

- [ ] **Step 3: Implement dependency-scoped invalidation**

Preserve unrelated evidence. Authority, safety, persistence, and recovery architecture changes invalidate all declared downstream dependents.

- [ ] **Step 4: Run and commit**

~~~bash
python3 scripts/validate_lifecycle_orchestration.py
git add scripts/lifecycle_orchestration_contract.py scripts/lifecycle_plan_contract.py scripts/validate_lifecycle_orchestration.py
git commit -m "feat: route feedback to the earliest failed layer"
~~~

### Task 5: Add durable versioned work state

**Files:**
- Create: scripts/lifecycle_state_store.py
- Modify: evals/agent/contracts/lifecycle-work-state.schema.json
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- load_state(path: Path) -> dict
- save_state_atomic(path: Path, state: dict, expected_revision: int) -> dict
- migrate_state_copy(state: dict, target_version: int) -> dict

- [ ] **Step 1: Add atomicity and schema RED cases**

Inject failure before rename and assert the old checkpoint survives. Reject duplicate JSON members, unknown schema, partial migration, and stale revision writes.

- [ ] **Step 2: Implement strict load and copy migration**

Validate a deep copy, write a temporary file, fsync where supported, replace atomically, and increment revision exactly once.

- [ ] **Step 3: Bind work state to current plan revision**

SAFE_TO_RESUME is prohibited when the action references a superseded plan.

- [ ] **Step 4: Run and commit**

~~~bash
python3 scripts/validate_lifecycle_orchestration.py
git add scripts/lifecycle_state_store.py evals/agent/contracts/lifecycle-work-state.schema.json scripts/validate_lifecycle_orchestration.py
git commit -m "feat: persist versioned lifecycle state"
~~~

### Task 6: Add leases, cancellation, and reconciliation

**Files:**
- Create: scripts/lifecycle_reconciliation.py
- Modify: scripts/lifecycle_state_store.py
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- acquire_lease(state, owner_id, now, ttl_seconds) -> dict
- assert_fence(state, owner_id, fencing_token) -> None
- reconcile_action(state, inspector: Callable[[dict], dict]) -> str
- cancel_work(state, reason: str, inspector) -> dict

- [ ] **Step 1: Add two-writer and stale-worker RED cases**

A newer lease increments fencing token; the old coordinator cannot advance state or publish worker completion.

- [ ] **Step 2: Add timeout, late-completion, and cancellation RED cases**

Timeout calls inspector before retry. Completed external action returns ALREADY_COMPLETED; uncertainty returns RECONCILIATION_REQUIRED. Cancellation preserves completed evidence and reconciles running actions.

- [ ] **Step 3: Implement stable action semantics**

Require action_id, deduplication_key, target, authority, attempt, timeout, expected artifacts, completion evidence, and compensation. Never infer completion from elapsed time.

- [ ] **Step 4: Run and commit**

~~~bash
python3 scripts/validate_lifecycle_orchestration.py
git add scripts/lifecycle_reconciliation.py scripts/lifecycle_state_store.py scripts/validate_lifecycle_orchestration.py
git commit -m "feat: reconcile interrupted lifecycle actions"
~~~

### Task 7: Integrate budgets and Review Assurance

**Files:**
- Create: scripts/lifecycle_review_adapter.py
- Modify: scripts/lifecycle_orchestration_contract.py
- Modify: evals/agent/contracts/lifecycle-work-state.schema.json
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- Consumes review_assurance_contract.evidence_applicable, next_review_cells, and decide_review.
- plan_review(state, review_record, policy) -> dict
- consume_budget(state, kind: str, amount: int | float) -> dict

- [ ] **Step 1: Add cell-reuse and invalidation RED cases**

Identical hashes schedule no completed cell again; changed source invalidates dependents; repeated one-model calls never raise achieved level.

- [ ] **Step 2: Add token/time/cost/retry RED cases**

Exhaustion returns paused or truthful degradation, never PASS.

- [ ] **Step 3: Implement a narrow adapter**

Persist required/achieved level, decision, vetoes, degradation, exception, lineage, and separated usage/cost. Do not copy assurance algorithms.

- [ ] **Step 4: Run and commit**

~~~bash
python3 scripts/validate_review_assurance.py
python3 scripts/validate_lifecycle_orchestration.py
git add scripts/lifecycle_review_adapter.py scripts/lifecycle_orchestration_contract.py evals/agent/contracts/lifecycle-work-state.schema.json scripts/validate_lifecycle_orchestration.py
git commit -m "feat: resume risk-based lifecycle reviews"
~~~

### Task 8: Add deployment and operational closure

**Files:**
- Modify: config/lifecycle-profiles.json
- Modify: scripts/lifecycle_orchestration_contract.py
- Modify: scripts/validate_lifecycle_orchestration.py

**Interfaces:**
- States: released, deployed, target_verified, observing, operationally_confirmed.
- deployment_decision(state, health_evidence: dict) -> str returns ADVANCE, HOLD, ROLLBACK, or AUTHORITY_REQUIRED.

- [ ] **Step 1: Add release/deployment/verification RED cases**

Successful deployment cannot set operationally_confirmed; missing observation window holds; breached hard gate rolls back or requests authority.

- [ ] **Step 2: Implement staged rollout gates**

Support bounded pilot/canary, observation deadline, evidence source, warning/hard thresholds, rollback target, and owner.

- [ ] **Step 3: Run and commit**

~~~bash
python3 scripts/validate_lifecycle_orchestration.py
git add config/lifecycle-profiles.json scripts/lifecycle_orchestration_contract.py scripts/validate_lifecycle_orchestration.py
git commit -m "feat: distinguish deployment from operational closure"
~~~

### Task 9: Connect Skills, behavior cases, and docs

**Files:**
- Modify: .agents/skills/development-process-tailoring/SKILL.md
- Modify: .agents/skills/agent-development-process/SKILL.md
- Modify: .agents/skills/coding-agent-project-governance/SKILL.md
- Modify: .agents/skills/runtime-evaluation-engineering/SKILL.md
- Modify: .agents/skills/document-governance/SKILL.md
- Modify: relevant evals/behavior/cases/*.json
- Create: docs/RESUMABLE_LIFECYCLE_ORCHESTRATION.md
- Modify: README.md

**Interfaces:**
- development-process-tailoring owns lifecycle planning.
- Generic planning plugins may produce detailed steps only through the CloudBox plan contract.

- [ ] **Step 1: Add behavior cases before Skill edits**

Cover defaults, risk-driven replanning, earliest-layer return, stale-plan rejection, interruption, authority preservation, and low-token evidence reuse. Record behavior as RED or NOT RUN.

- [ ] **Step 2: Add minimal Skill rules and operator docs**

Explain process-owner versus technical-owner boundaries and hybrid planning-plugin compatibility.

- [ ] **Step 3: Refresh and verify**

~~~bash
python3 scripts/manage_skill.py refresh --all
python3 scripts/validate_behavior_evals.py
python3 scripts/validate_pack.py
python3 scripts/run_all_checks.py
git diff --check
~~~

- [ ] **Step 4: Commit**

~~~bash
git add .agents/skills evals/behavior/cases docs/RESUMABLE_LIFECYCLE_ORCHESTRATION.md README.md SKILL_MANIFEST.json
git commit -m "docs: connect resumable lifecycle orchestration"
~~~

### Task 10: Execute behavior and recovery evidence

**Files:**
- Create: docs/releases/evidence/<version>-lifecycle-orchestration-red-green.md
- Modify: docs/CLOUDSKILL_CHANGE_HISTORY.md
- Modify: CLOUDSKILL_AGENT_HANDOFF.md
- Modify release surfaces only after gates pass.

**Interfaces:**
- Produces same-case RED/GREEN results and exact interruption fault-injection evidence.

- [ ] **Step 1: Execute bounded behavior cases at the required assurance level**

- [ ] **Step 2: Inject interruption scenarios**

Stop between artifact/checkpoint writes; stale lease completion; timeout with late completion; cancellation; schema mismatch; budget exhaustion; risk-driven replan.

- [ ] **Step 3: Record evidence truthfully**

Do not claim external deployment, device, or operational verification that did not run.

- [ ] **Step 4: Run exact-tip verification**

Run: python3 scripts/run_all_checks.py && git diff --check

- [ ] **Step 5: Prepare the approved release increment**

~~~bash
git commit -m "feat: prepare CloudBox resumable lifecycle release"
~~~

