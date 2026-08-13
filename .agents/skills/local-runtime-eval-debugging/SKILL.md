---
name: local-runtime-eval-debugging
description: Use when executing, diagnosing, grading, or packaging local CloudSkill or CloudBox Runtime Evals, especially with Ollama, Python discovery, context-budget overflow, missing reports, routing versus behavior failures, or a request for one reproducible upload bundle.
---

# Local Runtime Eval Debugging

## Core principle

A local Eval workflow should require one user command and produce one review bundle. Do not make the user manually chain Runner, Grader, report, Finder, and archive commands.

The pipeline must distinguish:

- **Infrastructure failure:** Python, Ollama, model availability, file availability, permissions, or process execution failed.
- **Context failure:** required Router or selected-skill context does not fit the configured budget.
- **Routing quality failure:** the model ran, but selected the wrong owner, supporting set, or execution order.
- **Behavior quality failure:** routing completed, but the engineering deliverable omitted required evidence or exposed internal planning.
- **Evaluation gate failure:** the pipeline completed and produced valid evidence, but the score did not meet the target. This is not a Runner failure.

Read:

- `references/local-eval-troubleshooting.md`
- `references/codex-runtime-eval.md`
- `assets/LOCAL_EVAL_BUNDLE_CONTRACT.md`

## Trigger examples

Use this skill when the request includes one or more of these pressures:

- Run the local Runtime Eval and package the result for review.
- Diagnose `Python not found`, Ollama connection/model errors, context overflow, missing JSONL, missing Markdown report, or invalid output shape.
- Determine whether a result is still running, failed before model execution, failed during routing, or failed only at the quality gate.
- Produce a single ZIP containing enough evidence for another engineer or AI assistant to diagnose the run.
- Simplify a multi-command local Eval procedure into one stable repository command.

Do not use this skill for:

- Designing the equipment architecture being evaluated.
- Ordinary application debugging unrelated to the Eval harness.
- Creating or changing skill behavior itself unless `developing-skills` is also selected.
- Generic repository governance unless repository rules, release, or CI are explicitly requested.

## Required workflow

### 1. Create evidence storage before validation

Create the run directory, latest-run pointer, status file, and log destination before checking Python, Ollama, files, or context. A failed preflight must still leave a diagnosable bundle.

### 2. Discover the runtime deterministically

Check, in order:

1. Explicit configured Python path.
2. Common Python 3.10+ command names.
3. python.org Framework paths.
4. Intel and Apple Silicon Homebrew paths.
5. pyenv paths when present.

Record the exact executable and version. Do not silently use Python 3.7 when the scripts require newer syntax or runtime behavior.

Check Ollama through its local API, record the installed model list, and verify the requested exact model name before starting a long run.

### 3. Use adaptive context preflight

Build the actual routing prompts and select the smallest configured context that fits all required cases without truncating required files. Do not keep a stale hard-coded 4096 assumption after skill or routing-map growth.

Record:

- candidate context sizes tested,
- selected routing context,
- selected behavior context,
- estimated tokens and overflow evidence,
- whether any optional reference was dropped.

### 4. Run and grade as separate stages

Run Routing, then grade Routing. Run Behavior only after a valid route is available. Preserve raw JSONL, summaries, Markdown reports, usage, latency, model identity, and errors.

Do not treat a non-perfect routing score as an infrastructure failure. Continue to package the evidence unless the user explicitly requested a fail-fast release gate.

### 5. Preserve raw behavior before refinement

If a behavior answer exposes planning, mentions Router/Eval/Skill machinery, or scores below the configured threshold, a refinement pass may rewrite it into a final engineering deliverable.

The refinement pass must:

- preserve the original output in a separate field/file,
- record that refinement occurred,
- avoid inventing host execution, tests, or current plant facts,
- separate assumptions and unresolved inputs,
- be graded separately from the raw answer.

Never overwrite the only copy of the model's first behavior output.

Reject a refinement candidate when it is empty, collapses to a fragment, still exposes internal planning, or lacks minimum task evidence. Preserve the rejected candidate for diagnosis, keep the raw answer as the scored fallback, and report `refinement attempted` separately from `refinement accepted`.

### 5a. Separate raw model text from the final deliverable

Use a structured final-deliverable contract for Behavior execution:

```json
{"final": "complete engineering deliverable"}
```

Preserve the complete provider response separately, grade only the validated `final` value, and record the output contract. A strict terminal `<final>...</final>` block may remain as a legacy refinement fallback, but an unstructured planning response must never be accepted merely because it contains enough rubric keywords.

Do not expose Router decisions, selected Skill IDs, case IDs, routing-only wording, or source paths to the downstream model unless the engineering task requires them.

### 6. Package one review bundle

Create one ZIP containing the bundle contract in `LOCAL_EVAL_BUNDLE_CONTRACT.md`. Include only the current run and selected source snapshots needed for diagnosis. Exclude credentials, complete transcripts, unrelated `.local` data, `.git`, caches, and machine metadata such as `.DS_Store`.

Create a stable pointer such as `LATEST_REVIEW_ZIP.txt`, print the exact ZIP path, and reveal the file in Finder on macOS when possible.

### 6a. Maintain evolution handoff

When the task produces an increment intended for another conversation or coding agent, update:

- `/CLOUDBOX_SKILLS_AGENT_HANDOFF.md` with current branch/PR, latest verified evidence, open items, commands, and safety constraints;
- `/docs/CLOUDBOX_SKILLS_DESIGN_AND_FLOW.md` when the architecture or operating flow changes;
- `/docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md` with the evidence, diagnosed layer, change, result, and unresolved risk.

The handoff must be sufficient to continue from repository files and the newest review ZIP without requiring the previous chat transcript.

### 7. Report stage truthfully

Use these final statuses:

- `PIPELINE_SUCCESS / GATE_PASS`
- `PIPELINE_SUCCESS / GATE_FAIL`
- `PIPELINE_FAILED / PARTIAL_BUNDLE_CREATED`
- `MANUAL_REQUIRED`

A quality score below threshold is normally `PIPELINE_SUCCESS / GATE_FAIL` because the evidence was generated successfully.

## Diagnosis order

Always diagnose from the earliest failed stage:

1. bootstrap/runtime discovery,
2. repository file and manifest validation,
3. Ollama/model availability,
4. context preflight,
5. routing execution,
6. routing grading,
7. behavior execution,
8. behavior grading/refinement,
9. packaging.

Do not infer a later-stage defect when an earlier stage never ran.

## Common mistakes

- Giving the user five commands when one wrapper can own the sequence.
- Writing the latest-run pointer only after success.
- Calling every file under `.local` “tracked” without asking Git which files are actually tracked.
- Keeping static validation at 4096 after the prompt catalog grows.
- Treating a strict score failure as a crashed process.
- Grading a report path before the JSONL exists.
- Deleting old results before the new bundle is confirmed.
- Replacing the raw behavior output with a polished rewrite and losing evidence.
- Packaging the entire repository or private transcript history.

## Codex CLI evaluation path

Use the Codex path when a higher-capability authenticated Codex baseline is needed in addition to the local Ollama baseline.

- Run `codex login status` before a long test; use `codex login` when no valid session exists.
- Use `./cloudbox-skills-eval-codex` for the quota-conscious one-repeat smoke path.
- Use `./cloudbox-skills-eval-codex --repeat 3` only after the smoke path completes and the expected usage budget is available.
- Execute Codex non-interactively through `codex exec` with an ephemeral session, read-only sandbox, no approvals, JSONL event capture, and a final-message file.
- Run the model in an isolated empty Git repository so it cannot silently load extra CloudSkill source beyond the assembled Eval prompt.
- Keep Codex and Ollama results as separate review bundles. Do not average them into one provider-independent score.
- A Codex failure caused by authentication or usage limits is an infrastructure/availability result, not a Skill-quality failure.
- Never package `~/.codex/auth.json`, access tokens, account identifiers, or raw authentication output.

## Claude Code CLI evaluation path

Use the Claude path when a higher-capability authenticated Claude baseline is needed alongside the local Ollama baseline and/or the Codex comparison.

- Run `claude auth status` before a long test; use `claude auth login` when no valid session exists.
- Use `./cloudbox-skills-eval-claude` for the quota-conscious one-repeat smoke path.
- Use `./cloudbox-skills-eval-claude --repeat 3` only after the smoke path completes and the expected usage budget is available.
- Execute Claude Code non-interactively through `claude -p --output-format json` with `--safe-mode` (no CLAUDE.md/Skills/plugins/hooks/MCP auto-loading), `--tools ""` (no tool access), `--permission-mode acceptEdits` (so a non-interactive session cannot stall on an unanswerable permission prompt; the ephemeral directory has nothing real to protect), and `--no-session-persistence`. Also frame the piped prompt itself with an explicit "do not inspect the workspace, do not use any tool" instruction — confirmed against a real run that omitting this let the model occasionally attempt a tool call anyway and exhaust its structured-output retry budget against a call `--tools ""` had already disabled.
- Run the model from an isolated empty temporary directory so it cannot silently load extra CloudSkill source beyond the assembled Eval prompt.
- Keep Claude, Codex, and Ollama results as separate review bundles. Do not average them into one provider-independent score.
- A Claude failure caused by authentication or usage limits is an infrastructure/availability result, not a Skill-quality failure.
- Never package Claude Code credential files, access tokens, account identifiers, or raw authentication output.
- `scripts/claude_eval_adapter.py`'s `--output-format json` result-field parsing was written from CLI documentation and `--help` output but has not been confirmed against a live process; treat its first real run as the point that assumption is actually verified, not the point it was written.

## Required output

1. Exact one-command invocation
2. Run directory and stable review ZIP path
3. Pipeline status and evaluation-gate status
4. Python, Ollama, model, and selected context evidence
5. Routing metrics and per-case failures
6. Raw and refined Behavior scores when refinement was used
7. Earliest failed stage and concrete next action
8. Privacy/exclusion statement for the bundle
9. Explicit statement of checks not actually run
