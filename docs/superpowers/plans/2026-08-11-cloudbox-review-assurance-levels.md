# CloudBox Review Assurance Levels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Replace fixed 2x2 classification with truthful, risk-selected, token-conscious L0-L3 review assurance across architecture, development, documents, security, migration, Skill/Eval, and release work.

**Architecture:** Add one authoritative assurance schema, policy, and pure classifier. Adapt the existing panel contract for new records while preserving historical evidence. Keep required level, achieved level, vetoes, exceptions, validity, and cost separate.

**Tech Stack:** Python 3.11 standard library, repository JSON-schema interpreter, JSON fixtures, existing Runtime Eval and panel tools.

## Global Constraints

- Deterministic checks precede hosted reviewers.
- Repeated calls or aliases resolving to one canonical model count once.
- Blocked or invalid cells do not count toward achieved composition.
- Exceptions authorize decisions but never upgrade achieved evidence.
- Safety, privacy, authority, unsupported claims, and unresolved High findings cannot be outvoted.
- Historical 6.0/6.1 evidence remains readable and immutable.
- Structural implementation requires zero hosted calls.

---

### Task 1: Freeze assurance RED fixtures

**Files:**
- Create: evals/runtime/contracts/review-assurance.schema.json
- Create: evals/runtime/fixtures/review-assurance-red.json
- Create: scripts/validate_review_assurance.py
- Modify: scripts/run_all_checks.py

**Interfaces:**
- Fixtures expose case_id, review_scope, risk_class, required_level, workers, blocking_findings, exception, and expected.
- Validator exposes main() -> int.

- [ ] **Step 1: Add exact RED cases**

Include: four calls to one model reported as L2; two GPT plus two blocked Claude reported as L1; four distinct GPT mislabeled cross-family; L0 below L1 published without exception; exception incorrectly upgrading achieved level; High finding outvoted.

- [ ] **Step 2: Run the validator**

Run: python3 scripts/validate_review_assurance.py

Expected: FAIL with missing review_assurance_contract.

- [ ] **Step 3: Register and commit RED**

~~~bash
git add evals/runtime/contracts/review-assurance.schema.json evals/runtime/fixtures/review-assurance-red.json scripts/validate_review_assurance.py scripts/run_all_checks.py
git commit -m "test: freeze review assurance red cases"
~~~

### Task 2: Implement assurance classification

**Files:**
- Create: scripts/review_assurance_contract.py
- Modify: scripts/validate_review_assurance.py

**Interfaces:**
- canonical_independent_cells(workers: list[dict]) -> set[tuple[str, str]]
- achieved_level(workers: list[dict]) -> str
- level_rank(level: str) -> int

- [ ] **Step 1: Add failing level assertions**

~~~python
assert achieved_level([]) == "L0_NONE"
assert achieved_level([worker("gpt", "a")]) == "L0_SINGLE_REVIEW"
assert achieved_level([worker("gpt", "a"), worker("gpt", "b")]) == "L3_SINGLE_FAMILY_PAIR"
assert achieved_level([worker("gpt", name) for name in "abcd"]) == "L2_SINGLE_FAMILY_QUAD"
assert achieved_level(cross_family_2x2) == "L1_CROSS_FAMILY_2X2"
~~~

- [ ] **Step 2: Implement canonical deduplication and classification**

Count only completed contract-valid cells with canonical identity provenance. L1 requires two families with two models each; L2 four in one family; L3 two in one family; L0 one.

- [ ] **Step 3: Run GREEN and commit**

~~~bash
python3 scripts/validate_review_assurance.py
git add scripts/review_assurance_contract.py scripts/validate_review_assurance.py
git commit -m "feat: classify review assurance levels"
~~~

### Task 3: Bind risk, vetoes, and exceptional authority

**Files:**
- Create: config/review-assurance-policy.json
- Modify: evals/runtime/contracts/review-assurance.schema.json
- Modify: scripts/review_assurance_contract.py
- Modify: scripts/validate_review_assurance.py

**Interfaces:**
- load_review_policy(path: Path) -> dict
- required_level(scope: str, risk_class: str, policy: dict) -> str
- decide_review(required: str, achieved: str, findings: list[dict], exception: dict | None) -> dict

- [ ] **Step 1: Add risk-profile assertions**

Require L1 for authority/security/privacy/irreversible changes, L2 for normal feature/Skill/Eval/persistence changes, L3 for bounded patches and semantic document corrections, and deterministic-only for proven presentation changes.

- [ ] **Step 2: Add exception and veto mutation tests**

Require authorizer, timestamp, exact source hash, scope, required/achieved levels, and residual risk. Reject standing authorization and any exception that changes achieved level.

- [ ] **Step 3: Implement policy and decision functions**

Return PASS, PASS_WITH_EXCEPTION, or BLOCKED. Any unresolved veto or High finding returns BLOCKED.

- [ ] **Step 4: Run GREEN and commit**

~~~bash
python3 scripts/validate_review_assurance.py
git add config/review-assurance-policy.json evals/runtime/contracts/review-assurance.schema.json scripts/review_assurance_contract.py scripts/validate_review_assurance.py
git commit -m "feat: bind review assurance to risk"
~~~

### Task 4: Adapt the existing panel contract

**Files:**
- Modify: scripts/multimodel_panel_contract.py
- Modify: evals/runtime/contracts/multimodel-panel.schema.json
- Modify: scripts/run_multimodel_panel.py
- Modify: scripts/validate_multimodel_panel.py

**Interfaces:**
- Preserve classify_panel(workers) for historical records.
- Add classify_assurance(record: dict) -> dict delegating to the new contract.
- New records carry review_scope, risk_class, required_level, achieved_level, and review_decision.

- [ ] **Step 1: Add compatibility RED assertions**

Historical four-cell records remain COMPLETE_2X2; four independent GPT cells become L2; no copied level algorithm may appear in the adapter.

- [ ] **Step 2: Implement version-compatible adapter**

Read schema version 1 unchanged; emit version 2 for new records; never rewrite historical evidence.

- [ ] **Step 3: Run and commit**

~~~bash
python3 scripts/validate_review_assurance.py
python3 scripts/validate_multimodel_panel.py
git add scripts/multimodel_panel_contract.py evals/runtime/contracts/multimodel-panel.schema.json scripts/run_multimodel_panel.py scripts/validate_multimodel_panel.py
git commit -m "feat: integrate assurance with review panels"
~~~

### Task 5: Add evidence validity and token-aware scheduling

**Files:**
- Modify: scripts/review_assurance_contract.py
- Modify: scripts/run_multimodel_panel.py
- Modify: scripts/validate_review_assurance.py
- Modify: evals/runtime/contracts/review-assurance.schema.json

**Interfaces:**
- evidence_applicable(record, *, source_hash, contract_hash, packet_hash, rubric_hash, risk_class) -> bool
- next_review_cells(record, policy, budget) -> list[dict[str, str]]

- [ ] **Step 1: Add RED cases**

Cover no-change zero calls, changed source/rubric, canonical model drift, expired policy, blocker stop, saturation, and exhausted token/cost/provider-call budgets.

- [ ] **Step 2: Implement minimum scheduling**

Reuse only hash-valid evidence; prefer efficient models; reserve frontier escalation for required composition, ambiguity, veto adjudication, or disagreement. Budget exhaustion pauses or degrades truthfully, never passes.

- [ ] **Step 3: Run and commit**

~~~bash
python3 scripts/validate_review_assurance.py
python3 scripts/validate_multimodel_panel.py
git add scripts/review_assurance_contract.py scripts/run_multimodel_panel.py scripts/validate_review_assurance.py evals/runtime/contracts/review-assurance.schema.json
git commit -m "feat: minimize review cost with valid evidence reuse"
~~~

### Task 6: Connect Skills, behavior cases, and docs

**Files:**
- Modify: .agents/skills/runtime-evaluation-engineering/SKILL.md
- Modify: .agents/skills/developing-skills/references/conversation-derived-optimization.md
- Modify: .agents/skills/architecture-review/SKILL.md
- Modify: .agents/skills/document-governance/SKILL.md
- Modify: .agents/skills/software-quality-iso25010/SKILL.md
- Modify: relevant evals/behavior/cases/*.json
- Create: docs/REVIEW_ASSURANCE_LEVELS.md
- Modify: README.md

**Interfaces:**
- Skill prose references but does not duplicate the classifier.
- Behavior cases cover truthful degradation, architecture veto, low-risk token conservation, and deterministic-only document edits.

- [ ] **Step 1: Add behavior cases before Skill edits**

Record current behavior as RED or NOT RUN; include application, discipline, and counterexample cases.

- [ ] **Step 2: Add minimal Skill rules and operator docs**

State that assurance measures reviewer independence, not build/test/device correctness.

- [ ] **Step 3: Refresh and verify**

~~~bash
python3 scripts/manage_skill.py refresh --all
python3 scripts/validate_pack.py
python3 scripts/run_all_checks.py
git diff --check
~~~

Expected: PASS without fabricating reviewed-version fields.

- [ ] **Step 4: Commit**

~~~bash
git add .agents/skills evals/behavior/cases docs/REVIEW_ASSURANCE_LEVELS.md README.md SKILL_MANIFEST.json
git commit -m "docs: apply review assurance across CloudBox"
~~~

### Task 7: Execute bounded behavior evidence and release gates

**Files:**
- Create: docs/releases/evidence/<version>-review-assurance-red-green.md
- Modify: docs/CLOUDSKILL_CHANGE_HISTORY.md
- Modify: CLOUDSKILL_AGENT_HANDOFF.md
- Modify version/plugin surfaces only after gates pass.

**Interfaces:**
- Produces exact source, contract, packet, rubric, model, token, and cost lineage.

- [ ] **Step 1: Execute frozen cases at the risk-required minimum**

Stop on blockers; do not run L1 for lower-risk work.

- [ ] **Step 2: Record PASS/FAIL/BLOCKED/NOT RUN/MANUAL_REQUIRED truthfully**

- [ ] **Step 3: Run exact-tip verification**

Run: python3 scripts/run_all_checks.py && git diff --check

- [ ] **Step 4: Synchronize the approved release version and commit**

~~~bash
git commit -m "feat: prepare CloudBox review assurance release"
~~~

