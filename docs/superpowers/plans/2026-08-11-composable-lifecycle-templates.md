# Composable Lifecycle Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three pre-qualified, composable lifecycle templates with deterministic applicability/delta checks so matching work avoids repeated full risk calculation without weakening lifecycle or evidence.

**Execution status (2026-08-12):** Tasks 1 through 5, typed JSON identity
correction, no-change owner adjudication, and layer-typed RED/GREEN governance
are implemented and independently reviewed without High/Medium findings.
Version surfaces target 6.4.0. Fresh candidate validation, exact-tip release
review, and every remote publication gate remain pending.

**Architecture:** Add one authoritative versioned template registry and a pure selector/composer beside the existing lifecycle-profile contract. The existing Plan Owner and durable lifecycle runtime remain authoritative; template output is only normalized planning input and never executes work.

**Tech Stack:** Python 3 standard library, JSON contracts, existing lifecycle orchestration and Behavior-Eval validators, Markdown evidence.

## Global Constraints

- Priority is lifecycle/dynamic loop first, evidence/verification second, token/context cost third.
- `development-process-tailoring` remains the sole Plan Owner.
- Implement only `lightweight-change`, `bounded-feature`, and `skill-evolution`.
- Deferred template IDs must return unsupported, not silently fall back.
- No background automation, external tool execution, Git authority, version bump, tag, or Release in this plan.
- Provider-backed Runtime Eval is `NOT RUN` unless actually executed.

---

### Task 1: Authoritative template registry and RED validator

**Files:**
- Create: `config/lifecycle-templates.json`
- Create: `scripts/validate_lifecycle_templates.py`
- Modify: `scripts/run_all_checks.py`

**Interfaces:**
- Registry schema version: integer `1`.
- Implemented template IDs: `lightweight-change`, `bounded-feature`, `skill-evolution`.
- Deferred template IDs: `iterative-discovery`, `architecture-change`, `brownfield-refactor`, `hotfix`, `release`, `hardware-integration`, `incident-recovery`.

- [x] **Step 1: Write the failing registry validator**

Require one registry authority containing implemented/deferred status, contract
version, applicability, exclusions, stages, gates, owners, required evidence,
review level, resume/reconciliation, reuse/invalidation, compatible overlays,
and escalation conditions. Require every registered consumer path to use the
same registry.

- [x] **Step 2: Add positive-propagation and negative-drift mutations**

The validator must prove that adding a synthetic implemented template to the
registry appears through the shared loader/selector, and that a copied or stale
consumer mapping fails. Also mutate away lifecycle ownership, required evidence,
and a deferred status and require failure.

- [x] **Step 3: Verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_lifecycle_templates.py
```

Expected: FAIL because the registry and shared contract do not exist.

- [x] **Step 4: Add the minimum registry**

Create the three complete implemented entries and seven explicitly deferred
entries. Do not add mechanics for deferred templates.

- [x] **Step 5: Register and commit**

Add the validator to `scripts/run_all_checks.py`, verify its intended RED still
names the missing contract, then commit the registry/validator RED increment.

```bash
git add config/lifecycle-templates.json scripts/validate_lifecycle_templates.py scripts/run_all_checks.py
git commit -m "test: define lifecycle template registry"
```

### Task 2: Pure selection and delta-check contract

**Files:**
- Create: `scripts/lifecycle_template_contract.py`
- Modify: `scripts/validate_lifecycle_templates.py`

**Interfaces:**
- `load_templates(path: Path) -> dict`
- `assess_template(template_id: str, facts: dict, registry: dict) -> dict`
- Result status: `selected | escalation_required | unsupported`.
- Delta fields: `external_side_effect`, `authority_or_state`, `sensitive_or_privileged`, `platform_or_compatibility`, `irreversible_or_unreconciled`, `outside_verified_envelope`.

- [x] **Step 1: Add selection RED assertions**

Require exact matches for each implemented template, explicit unsupported for
each deferred template, and no default fallback for unknown IDs.

- [x] **Step 2: Add delta RED assertions**

Require all six values to be literal `true` or `false`. Six literal `false`
values plus matched positive conditions return `selected` and
`full_risk_calculation_required: false`. Any literal `true`, missing,
non-boolean, or unknown value returns `escalation_required` with the exact
reason and `full_risk_calculation_required: true`.

- [x] **Step 3: Implement the minimum pure contract**

Load and validate the authoritative registry, normalize task facts, evaluate
positive/exclusion conditions, and return a deterministic evidence record with
template/version, matched conditions, delta answers, reasons, and status. Do
not execute tasks or call a model.

- [x] **Step 4: Verify GREEN and mutations**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_lifecycle_templates.py
python3 scripts/validate_lifecycle_orchestration.py
```

Expected: PASS, including synthetic propagation and stale-mapping rejection.

- [x] **Step 5: Commit**

```bash
git add scripts/lifecycle_template_contract.py scripts/validate_lifecycle_templates.py
git commit -m "feat: select lifecycle templates deterministically"
```

### Task 3: Composition and lifecycle-plan integration

**Files:**
- Modify: `scripts/lifecycle_template_contract.py`
- Modify: `scripts/lifecycle_plan_contract.py`
- Modify: `scripts/validate_lifecycle_templates.py`
- Modify: `scripts/validate_lifecycle_orchestration.py`

**Interfaces:**
- `compose_templates(..., *, work_id, source_hash, tasks, risk_context) -> dict`
- `create_plan(..., template_resolution=None, template_registry=None, template_facts=None, risk_context=None) -> dict`
- Composition status: `selected | escalation_required | unsupported | conflict`.

- [x] **Step 1: Add composition RED assertions**

Require one base, unique overlays, declared compatibility, strongest review/gate
preservation, and deterministic resolved owners/evidence/stages. Every template
stage partial order must survive a deterministic topological merge; cycles
conflict. Reject unknown, deferred, duplicated, incompatible, or owner-
conflicting overlays.

- [x] **Step 2: Add lifecycle integration RED assertions**

Require a plan created from a selected resolution to persist template IDs,
contract versions, delta evidence hash, composition order, and resolution
status. Selected evidence and the plan snapshot bind work/source/task identity,
normalized facts/risk, and authoritative registry identity. Reject cross-
context replay and escalation/unsupported/conflict as plan input. A replan must
keep the prior resolution as lineage and invalidate affected evidence only.

- [x] **Step 3: Implement minimal composition**

Merge stages with a deterministic topological order and other lists without
duplicates, never weaken gates/review, and fail closed on cyclic stages or
conflicting scalar ownership/completion semantics. Extend `create_plan`
compatibly with optional template context arguments; its legacy four-argument
result remains unchanged. Replan automatically invalidates selected all-false
evidence when source, authority, side-effect, bound facts/risk, or explicit
delta changes contradict it, unless a fresh authoritative resolution is bound
to the new context.

- [x] **Step 4: Verify GREEN**

Run both focused validators and prove existing callers without a template
resolution remain compatible.

- [x] **Step 5: Commit**

```bash
git add scripts/lifecycle_template_contract.py scripts/lifecycle_plan_contract.py scripts/validate_lifecycle_templates.py scripts/validate_lifecycle_orchestration.py
git commit -m "feat: compose lifecycle template plans"
```

### Task 4: Skill behavior and routing evidence

**Files:**
- Modify: `.agents/skills/development-process-tailoring/SKILL.md`
- Modify: `.agents/skills/development-process-tailoring/lifecycle.json`
- Modify: `evals/behavior/cases/resumable-lifecycle-orchestration.json`

**Interfaces:**
- Behavior cases use the registry/template names exactly.
- Skill text routes template selection to the deterministic contract and keeps Plan Owner authority.

- [x] **Step 1: Add Behavior RED cases**

Add cases for each direct selection, no-full-risk fast path, unknown delta
escalation, deferred-template refusal, strongest-gate composition, evidence-led
replan, and the fixed lifecycle/evidence/token priority.

- [x] **Step 2: Record the pre-change semantic result**

Run static/manual independent adjudication without the proposed Skill section.
Record exact omissions and source tip; if a case already passes, mark it
regression-only rather than fabricating RED.

- [x] **Step 3: Add the minimum Skill section**

Describe when template selection is appropriate, the six delta questions,
composition/stop rules, and the deterministic contract path. Do not duplicate
the registry bodies in `SKILL.md`.

- [x] **Step 4: Verify GREEN and adjacent controls**

Re-run the same cases plus trivial direct work, risk-triggered replan, and
generic detailed-planner subordination. Record static/manual versus provider
execution truthfully.

- [x] **Step 5: Commit**

```bash
python3 scripts/validate_behavior_evals.py
python3 scripts/manage_skill.py audit --check
python3 scripts/validate_pack.py
git add .agents/skills/development-process-tailoring evals/behavior/cases/resumable-lifecycle-orchestration.json SKILL_MANIFEST.json
git commit -m "feat: route composable lifecycle templates"
```

### Task 5: Documentation, regression, and exact-tip review

**Files:**
- Create: `docs/LIFECYCLE_TEMPLATE_CATALOG.md`
- Create: `docs/evolution/2026-08-11-lifecycle-template-pilot-evidence.md`
- Modify: `docs/RESUMABLE_LIFECYCLE_ORCHESTRATION.md`
- Modify: `CLOUDSKILL_AGENT_HANDOFF.md`
- Modify: `docs/CLOUDSKILL_CHANGE_HISTORY.md`
- Modify: `docs/superpowers/plans/2026-08-11-composable-lifecycle-templates.md`

**Interfaces:**
- Catalog is a human view; `config/lifecycle-templates.json` remains authoritative.
- Evidence identifies exact tips, methods, reviewers, deterministic checks, and NOT RUN items.

- [x] **Step 1: Document catalog and deferred boundary**

Document the three available templates, seven deferred IDs, composition rules,
delta fields, statuses, examples, and stop conditions without copying mutable
template definitions as a second authority.

- [x] **Step 2: Record RED/GREEN and cost evidence**

Record which full-risk calculations are avoided by exact matches, selector
input/output bytes, selector/composer model calls (expected zero), provider-
backed Runtime Eval status separately, semantic-adjudicator provenance, and all
regression findings. Token values remain estimates unless measured by a provider.

- [x] **Step 3: Run complete regression**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_all_checks.py
git diff --check
```

- [ ] **Step 4: Obtain independent exact-tip review**

Review authority, lifecycle continuity, evidence validity, composition conflict,
deferred-template behavior, anti-drift tests, token claims, privacy, and docs.
Correct every High/Medium finding before PASS.

- [x] **Step 5: Commit and present candidate**

Commit evidence/handoff/history truthfully. Present the candidate before
version synchronization, push, PR, merge, tag, or Release.
