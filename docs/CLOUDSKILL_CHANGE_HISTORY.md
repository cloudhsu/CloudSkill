# CloudSkill evolution change history

This document records the evolution rationale and evidence chain for work that may span multiple conversations. Git commits and tags remain the authoritative source history.

## 2026-08-09 — Behavior contract consumer registry closure

Observed:

- The shared Behavior output contract and dedicated anti-drift Validator were
  present in the working tree.
- `validate_local_eval_debugging.py` still searched the local review runner for
  the retired literal `json-final-v1`.
- Static validation therefore stopped before Ollama or Codex was called.

Root cause:

- The shared contract centralized Prompt, schema, extraction, and planning
  rules, but it did not yet enumerate every required consumer.
- One adjacent Validator was omitted from the anti-drift migration and could
  retain a copied implementation detail.

Change:

Consumer registry:

- Add `required_consumer_paths` to the authoritative Behavior output contract.
- Register Runtime, Refiner, local Eval validation, and anti-drift validation
  consumers.
- Make `validate_local_eval_debugging.py` execute the shared extraction and
  Refiner Prompt contracts instead of searching for a contract-name literal.
- Make `validate_behavior_contract.py` parse every registered consumer, require
  a shared-contract import, scan all other Validators for retired API names and
  Prompt literals, and compare contract IDs/fingerprints at runtime.
- Add positive contract-propagation and negative injected-drift tests to the
  release package validation.

Expected evidence:

- Editing the authoritative Prompt requirements propagates through Runtime and
  Refiner Prompt assembly without editing Validators.
- Injecting a retired contract literal into another Validator is detected.
- Full static validation reaches the model stage without another contract-copy
  failure.
- One new Ollama Review ZIP is generated and then committed with the complete
  working-tree increment.

Unresolved:

- Interpret the resulting R02/R05/R07 evidence.
- Run the Codex comparison after the available usage pool resets.

## 2026-08-09 — Single-source Behavior output contract and anti-drift validation

Observed:

- The structured Behavior/refinement overlay was applied locally.
- Static validation first failed because one Validator imported the retired
  `extract_final` API.
- After that API was aligned, another Validator still required four copied
  prompt markers from the retired tag-based `<final>` contract.
- No model call occurred in either failure; the earliest failing layer was
  deterministic contract validation.

Root cause:

- Prompt text, JSON schema, extraction rules, refinement rules, planning-leak
  patterns, and Validator expectations had multiple independent copies.
- A format migration could update Runtime code while leaving one or more
  Validators on the old contract.

Change:

- Add one authoritative data contract:
  `evals/runtime/contracts/behavior-output-contract.json`.
- Add one executable adapter:
  `scripts/behavior_output_contract.py`.
- Runtime Prompt, Refiner Prompt, schemas, extraction, minimum lengths,
  planning-leak patterns, contract ID, and contract fingerprint now come from
  that source.
- Add `scripts/validate_behavior_contract.py` to test actual generated prompts,
  schemas, wrappers, structured extraction, strict legacy fallback, and
  planning-leak detection.
- Remove copied Behavior prompt-marker assertions from
  `validate_behavior_runtime_evals.py`.
- Delegate Behavior-contract consistency out of the Codex-path Validator.
- Record contract ID and fingerprint in Runtime Eval evidence.

Expected evidence:

- Static validation passes without looking for retired prompt sentences.
- A contract edit automatically changes both prompts and schemas.
- A consumer that stops importing the contract fails
  `validate_behavior_contract.py`.
- One fresh Ollama Review ZIP is produced before commit/push.
- PR #1 remains Draft until the new Runtime evidence is interpreted.

Unresolved:

- Review the next R02/R05/R07 Routing and Behavior results.
- Run the quota-conscious Codex comparison after availability resets.

## 2026-08-09 — Validator API alignment hotfix

Observed:

- The structured-refiner increment was applied locally.
- Static validation stopped before Runtime Eval because
  `validate_codex_eval_path.py` imported the removed `extract_final` API.
- The production refiner now exposes
  `extract_refined_final(text) -> (value, extracted, contract)`.

Earliest failing layer:

- Deterministic validator compatibility, before any Ollama or Codex model call.

Change:

- Align synthetic refiner checks with `extract_refined_final`.
- Validate structured `{ "final": "..." }`, strict terminal legacy fallback,
  unstructured tag mentions, and non-terminal legacy blocks.
- Continue through `cloudskill-resume --provider ollama` without reapplying
  the already completed evolution overlay.

Expected evidence:

- `scripts/validate_codex_eval_path.py` passes without a model call.
- `scripts/run_all_checks.py` passes.
- One fresh Ollama Review ZIP is produced.
- The complete overlay and this hotfix are committed and pushed together.

Unresolved:

- Interpret the new Routing and Behavior evidence before changing PR #1 from Draft.

## 2026-08-09 — Structured Behavior final contract and durable handoff

Planned increment based on `CloudSkill-local-eval-review-local-review-20260809-101744.zip`.

Observed:

- R05A/R05B/R05C and R07 routing all passed 3/3.
- R02 regressed 0/3 by selecting `equipment-control-architecture` instead of the required `equipment-domain-modeling` support.
- Raw R07 Behavior scored 70.
- Refinement was reported as accepted at 84, but the accepted text still contained planning and did not satisfy a real final-deliverable boundary.

Change:

- Reassert the code-review plus component-state-modeling composition rule for R02.
- Add a dedicated R07 `behavior_prompt` that removes routing-only wording.
- Require structured Behavior output: `{ "final": "..." }`.
- Preserve raw provider output separately from the graded final value.
- Require structured or strict terminal-final refinement output; reject unstructured keyword-rich planning.
- Expand planning-leak detection.
- Add design, flow, history, and agent-handoff documents plus deterministic validation.

Expected evidence:

- R02 returns `code-review` plus `equipment-domain-modeling`.
- R05A/B/C remain unchanged.
- Raw Behavior output contains only the structured final deliverable value after parsing.
- An unstructured refinement cannot be marked accepted.

## 2026-08-09 — Codex Runtime Eval path

Commit: `61f33c39ce9ba4628dd1225ead5df9542bb64d4c`

- Added `cloudskill-eval-codex`.
- Added Codex CLI adapter and provider-aware resume logic.
- Isolated Codex execution in a temporary read-only Git repository.
- Kept Codex authentication and quota failures separate from Skill-quality results.
- Tightened legacy terminal `<final>` extraction.
- Strengthened the R05C composition instruction.
- GitHub Actions passed.

## 2026-08-09 — R05 decomposition and R07 recovery evidence

Commit: `7a67da8a62a4449b09bcd477a2aba23bf2f5a42e`

- Split the ambiguous R05 case into R05A component state contract, R05B recovery ownership, and R05C combined composition.
- Added explicit component-versus-control ownership boundaries.
- Added minimum distributed ownership/recovery evidence.
- Preserved raw and extracted Behavior outputs separately.
- GitHub Actions passed.

## 2026-08-09 — Interruption-safe continuation command

Commit: `fa054afcce6e141f90eb0000dc33a76e2115330b`

- Added `cloudskill-resume`.
- Added provider/process detection, source-hash ZIP reuse, stage logging, commit/push/PR continuation, and stale-lock handling.
- Kept stashes and `.local` evidence outside commits.

## 2026-08-09 — Standardized Skill lifecycle and Runtime Eval engineering

PR: `#1`, initial lifecycle commit series.

- Established `draft -> experimental -> active -> stable -> deprecated`.
- Added per-Skill lifecycle metadata and lifecycle validation.
- Added `runtime-evaluation-engineering`.
- Kept `local-runtime-eval-debugging` focused on host execution, diagnosis, reports, and bundle handoff.
- Fixed canonical routing-evidence retrieval for version-scoped multi-audience reports.
- Separated pipeline success from evaluation-gate success.
- Updated GitHub Actions action versions.

## 2026-08-08 — Local Runtime Eval debugging foundation

Baseline commit: `a060ac9b4f18d137abb52eb3a02d48ba062bd9f1`

- Added one-command local Runtime Eval tooling.
- Added Ollama execution, adaptive context selection, grading, reporting, and uploadable review ZIP generation.
- Established the evidence used by the subsequent lifecycle and evaluation-engineering work.

## Maintenance rule

For each future increment, add a new entry at the top containing:

- date and commit/PR when available;
- observed evidence;
- diagnosed earliest failing layer;
- change made;
- expected or actual validation result;
- unresolved risks and next decision.
