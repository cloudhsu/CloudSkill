# CloudBox runtime model evaluations

This directory contains executable model evaluations. It complements, but does not replace, `evals/skill-routing-cases.csv` and `evals/behavior/cases/`.

## Why context mode matters

A local Ollama model is not a Codex, ChatGPT, or Claude Code plugin host. It does not automatically discover or load `.agents/skills/`.

The original 5.6.0 routing runner assembled a synthetic routing instruction, the `SKILL_MANIFEST.json` ID/description catalog, the current case, and the structured-output schema. It did **not** load:

- `.agents/skills/using-cloudbox-skills/SKILL.md`
- `.agents/skills/using-cloudbox-skills/references/conversation-routing-map.md`
- downstream `SKILL.md` files or their declared references

Therefore a failed 4B-model result could represent a Runner/context defect rather than a CloudBox Skill defect.

## Eval kinds

### Routing Eval

A Routing Eval chooses the smallest sufficient downstream skill set. In `router` mode the actual request includes:

1. the complete `using-cloudbox-skills/SKILL.md`,
2. `conversation-routing-map.md`,
3. all 17 Skill IDs and descriptions from `SKILL_MANIFEST.json`,
4. the routing-decision JSON Schema,
5. one current case,
6. explicit router/downstream separation,
7. language-neutral, decision-boundary routing rules.

The router is context used to make the decision. `using-cloudbox-skills` must never appear in `supporting_skills`; it may be `primary_skill` only for a task specifically about router design or routing policy.

### Behavior Eval

A Behavior Eval is a two-stage execution:

1. run the Router with verified `router` context;
2. validate the returned routing decision;
3. load the actual selected downstream `.agents/skills/<id>/SKILL.md` files;
4. optionally load references explicitly declared by those Skill files;
5. call the model again to answer the engineering task.

Selecting a Skill ID is not treated as executing that Skill. The deterministic grader continues to grade routing; it records Behavior execution status but does not claim to grade engineering-answer quality.

## Context modes

| Mode | Intended use | Context |
|---|---|---|
| `none` | Diagnostic baseline only | Skill IDs, routing rules, schema, and case; no Skill descriptions or Skill files |
| `manifest` | Previous-runner comparison | Skill IDs/descriptions, routing rules, schema, and case; no Router Skill file |
| `router` | Default Routing Eval | Full Router Skill, routing map, manifest catalog, schema, and case |
| `selected-skills` | Two-stage Behavior Eval | Router stage first, then actual selected Skill files and declared references |

Executable Ollama runs in `none` or `manifest` mode are refused unless `--allow-context-baseline` is supplied. This prevents invalid scores from being mistaken for Skill evaluation.

## Context evidence

Every result includes context evidence. Routing records use:

```json
{
  "context": {
    "mode": "router",
    "loaded_files": [],
    "prompt_characters": 0,
    "prompt_utf8_bytes": 0,
    "estimated_tokens": 0,
    "estimated_tokens_method": "ceil(utf8_bytes/4)",
    "num_ctx": 4096,
    "reserved_output_tokens": 320,
    "input_budget_tokens": 3776,
    "overflow_tokens": 0,
    "truncated": false,
    "truncated_files": [],
    "prompt_sha256": "..."
  }
}
```

Behavior records contain separate `context.routing` and `context.behavior` evidence.

Routing context is never silently truncated. If the complete Router Skill, routing map, catalog, schema, and case cannot fit, the Runner stops with `ContextBudgetError`. In Behavior mode, selected `SKILL.md` files are also never truncated. Optional declared references may be dropped as whole files, and every dropped path is recorded.

## Static validation

```bash
python3 scripts/validate_runtime_evals.py
python3 -m py_compile \
  scripts/runtime_eval_common.py \
  scripts/run_runtime_evals.py \
  scripts/grade_runtime_evals.py \
  scripts/validate_runtime_evals.py
```

`validate_runtime_evals.py` rebuilds the actual prompts for R01, R03, R06, and R07 in `none`, `manifest`, and `router` modes at `num_ctx=4096`. It also proves that Router mode loads the required files without truncation and that selected-skills mode loads a real downstream `SKILL.md`.

Static validation does not call Ollama and is not a model-quality pass.

## Inspect the exact Ollama request

Dry-run the four acceptance cases and write the complete request payloads:

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --context-mode router \
  --case-id R01-networkstream-stale-response \
  --case-id R03-versioned-multi-audience-report \
  --case-id R06-chinese-translation-no-skill \
  --case-id R07-english-equipment-architecture \
  --repeat 1 \
  --num-ctx 4096 \
  --temperature 0 \
  --seed 42 \
  --dry-run \
  --show-prompt \
  --prompt-output .local/runtime-evals/prompts
```

Each `.prompt.json` contains the exact `messages`, `format`, and Ollama options that would be sent to `/api/chat`.

## Run the four acceptance cases

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --context-mode router \
  --case-id R01-networkstream-stale-response \
  --case-id R03-versioned-multi-audience-report \
  --case-id R06-chinese-translation-no-skill \
  --case-id R07-english-equipment-architecture \
  --repeat 1 \
  --num-ctx 4096 \
  --temperature 0 \
  --seed 42 \
  --timeout 600 \
  --output .local/runtime-evals/qwen3-4b-router-acceptance.jsonl
```

## Compare no-context, manifest, and router modes

The first two modes are diagnostic baselines and require explicit opt-in:

```bash
for MODE in none manifest router; do
  EXTRA=()
  if [[ "$MODE" != "router" ]]; then
    EXTRA+=(--allow-context-baseline)
  fi

  python3 scripts/run_runtime_evals.py \
    --provider ollama \
    --model qwen3:4b \
    --context-mode "$MODE" \
    "${EXTRA[@]}" \
    --case-id R01-networkstream-stale-response \
    --case-id R03-versioned-multi-audience-report \
    --case-id R06-chinese-translation-no-skill \
    --case-id R07-english-equipment-architecture \
    --repeat 1 \
    --num-ctx 4096 \
    --temperature 0 \
    --seed 42 \
    --timeout 600 \
    --output ".local/runtime-evals/qwen3-4b-${MODE}-acceptance.jsonl"
done
```

Combine and grade the comparison:

```bash
cat \
  .local/runtime-evals/qwen3-4b-none-acceptance.jsonl \
  .local/runtime-evals/qwen3-4b-manifest-acceptance.jsonl \
  .local/runtime-evals/qwen3-4b-router-acceptance.jsonl \
  > .local/runtime-evals/qwen3-4b-context-comparison.jsonl

python3 scripts/grade_runtime_evals.py \
  --input .local/runtime-evals/qwen3-4b-context-comparison.jsonl \
  --output .local/runtime-evals/qwen3-4b-context-comparison-summary.json \
  --allow-failures
```

The summary includes `metrics_by_context_mode`.

## Full Routing Eval

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --context-mode router \
  --repeat 1 \
  --num-ctx 4096 \
  --temperature 0 \
  --seed 42 \
  --timeout 600 \
  --output .local/runtime-evals/qwen3-4b-router-canary.jsonl

python3 scripts/grade_runtime_evals.py \
  --input .local/runtime-evals/qwen3-4b-router-canary.jsonl \
  --output .local/runtime-evals/qwen3-4b-router-canary-summary.json \
  --allow-failures
```

## Two-stage Behavior Eval

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --eval-kind behavior \
  --context-mode selected-skills \
  --selected-reference-mode declared \
  --case-id R07-english-equipment-architecture \
  --repeat 1 \
  --num-ctx 8192 \
  --context-reserve-tokens 1200 \
  --behavior-max-output-tokens 1200 \
  --temperature 0 \
  --seed 42 \
  --timeout 600 \
  --output .local/runtime-evals/qwen3-4b-r07-behavior.jsonl
```

A no-skill routing result, such as R06, skips the second call and records `behavior_status: "no-skill"`.

## Interpreting failures

Keep these categories separate:

1. **Runner problem** — missing file, malformed request, missing context evidence, incorrect mode, context overflow, request failure.
2. **Prompt/context problem** — valid Runner execution but insufficient or conflicting supplied context, schema pressure, poor discrimination between adjacent Skills.
3. **Model-capacity problem** — valid Router context and schema, but a small model repeatedly fails language-neutral counterexamples, ordering, or adjacent-skill discrimination.
4. **CloudBox Skill-rule problem** — only infer after the actual Router context is verified and the failure repeats across runs or a stronger model/human review demonstrates a rule defect.

Do not modify all 17 Skills because one `qwen3:4b` run fails. Repair Runner/context defects first, compare modes, then create a focused Skill regression only when evidence remains.

## Contract repair and transparent scoring

The Runner defaults to:

```text
--contract-repair deterministic
```

This repair is intentionally narrow. It may:

- remove duplicate selected IDs,
- remove selected/rejected overlap,
- remove `using-cloudbox-skills` from downstream supporting skills,
- reconcile `execution_order` with the model-selected primary/supporting set.

It does **not** change `primary_skill` and does not add a missing supporting skill. Every record preserves:

- `initial_actual`: parsed model output before repair,
- `actual`: effective result after optional repair,
- `contract_repair.initial_errors`,
- `contract_repair.changes`,
- `contract_repair.final_errors`.

Disable repair when measuring raw schema/contract adherence:

```bash
--contract-repair none
```

The deterministic grader reports both `initial_metrics` and final `metrics`. A contract error no longer forces unrelated metrics to zero: a correct primary Skill and absence of router self-inclusion remain visible even when `execution_order` is invalid.

The grader also writes a human-readable Markdown report beside the JSON summary by default:

```bash
python3 scripts/grade_runtime_evals.py \
  --input .local/runtime-evals/qwen3-4b-router-canary.jsonl \
  --output .local/runtime-evals/qwen3-4b-router-canary-summary.json \
  --markdown-output .local/runtime-evals/qwen3-4b-router-canary-report.md \
  --allow-failures
```

Use `--no-markdown` only when a machine-only JSON artifact is required.

## Cleaning or archiving previous local results

Runtime results are local diagnostic evidence and are excluded from Git. For a clean rerun, archive them instead of immediately deleting them:

```bash
cd /Users/cloudhsu/projects/cloudskill/CloudSkill
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p ".local/runtime-evals-archive/$STAMP"
find .local/runtime-evals -mindepth 1 -maxdepth 1 \
  -exec mv {} ".local/runtime-evals-archive/$STAMP/" \;
mkdir -p .local/runtime-evals
```

To discard them completely:

```bash
rm -rf .local/runtime-evals
mkdir -p .local/runtime-evals
```

Archiving is preferable for this change because the earlier results provide the before/after baseline for Router retrieval, contract validity, and grading behavior.

## Deterministic Behavior evidence grading

Routing correctness and engineering-answer quality are graded separately.

After running a Behavior Eval, grade explicit engineering evidence with:

```bash
python3 scripts/grade_behavior_evals.py \
  --input .local/runtime-evals/qwen3-4b-r07-behavior.jsonl \
  --output .local/runtime-evals/qwen3-4b-r07-behavior-summary.json \
  --markdown-output .local/runtime-evals/qwen3-4b-r07-behavior-report.md \
  --allow-failures
```

The Behavior score checks configured evidence groups and unsafe claims. It is deterministic and human-readable, but it is a coverage-oriented diagnostic rather than proof of complete semantic correctness.

## One-command local review bundle

From the repository root, run:

```bash
./cloudbox-skills-eval
```

The command discovers Python 3.10+, verifies Ollama and the requested model, selects an adaptive routing context, runs the focused routing regression and R07 Behavior Eval, grades raw and refined behavior separately, and creates one ignored review ZIP. Upload the ZIP path printed as `UPLOAD THIS ZIP`; do not manually collect individual result files.

A score gate failure still produces a successful diagnostic bundle. Infrastructure and packaging failures also leave a partial ZIP when possible.

## Confidence and priority tooling (advisory, no live model call)

Three analysis-layer scripts, none wired into `run_all_checks.py`, none costing a
model call by themselves:

- `scripts/eval_confidence_report.py` -- Hoeffding margin an authored case
  *count* would support if fully executed. Blind to actual outcomes.
- `scripts/eval_confidence_report_bayesian.py` -- Beta-Binomial credible
  interval from real outcomes in `execution-ledger.json`. Tighter than
  Hoeffding at the same n, but only exists for Skills with real executions.
- `scripts/eval_priority_ranker.py` -- ranks every Skill (tested or not) by a
  pessimistic lower-confidence-bound score, to answer "whose next real
  execution is most worth spending on" without relying on someone noticing
  the worst-margin Skill by hand.

## Learning-curve tracking (Wright's Law)

`learning-curve-log.json` -- append-only, cross-session log of real per-batch
throughput, tagged with `session_id`. `scripts/learning_curve_report.py` fits
a power-law curve (`cost(n) = a * n^(-b)`) via log-log least squares.
Honestly limited right now: only one session's data exists (cannot yet
distinguish a durable improvement from a session-bound prompt-cache effect),
and the seeded batches differ in content/skill/complexity rather than being a
literal same-task repeated trial -- treat any current fit as a rough
throughput trend, not a validated learning curve. Both limitations are
reported by the script itself, not just documented here.

## Execution ledger

`execution-ledger.json` is a small, committed, append-only *summary* of real
executions (skill, case id, kind, result) -- distinct from `results/`, which
holds full raw model output and is gitignored/machine-local. Add a row per
real execution; never edit or delete an existing row's outcome, only append.
This is what the two tools above read.

## Mutation-testing a case (does the case actually discriminate?)

A case that PASSes against a Skill's current content proves the instruction
was followed. It does not by itself prove the case would have caught the
instruction's *absence* -- a case can pass for reasons unrelated to the rule
it claims to test (general model judgment, an unrelated overlapping rule
already present). To check a specific case's discriminating power:

```bash
# 1. Find the commit that added the rule this case targets, and its parent.
git log --oneline -- .agents/skills/<skill>/references/<file>.md

# 2. Temporarily swap in the pre-rule content for that one file only.
git checkout <parent-commit> -- .agents/skills/<skill>/references/<file>.md

# 3. Run the case against the swapped-in old content.
python3 scripts/run_runtime_evals.py --provider claude --eval-kind behavior \
  --skip-model-check --num-ctx 16384 --case-id <CASE-ID> \
  --cases evals/behavior/cases/<skill>.json --output /tmp/mutation-<CASE-ID>-old.jsonl

# 4. Restore immediately, before doing anything else.
git checkout HEAD -- .agents/skills/<skill>/references/<file>.md
git status --short   # must show no diff on that file before continuing
```

If the case still PASSes against the old content, it is not discriminating
for that rule and should be tightened. If it FAILs (or the model visibly
does the thing the rule now forbids), that is real causal evidence the rule
changes behavior, not just that the new text exists and gets mentioned.

**Pilot result (2026-08-22, REF-BEH-025):** re-ran the case that models this
session's own distilled scope-invention incident (Vikunja cloudbox-skills
#9) against `safe-incremental-refactoring/references/refactoring-workflow.md`
as it stood *before* that rule was added. Under the old content the model
proposed extracting the three requested checks into a new shared-validator
abstraction instead of the literal requested duplication -- the exact
scope-elaboration pattern the new rule targets. Under the current content
(same case, same day, separate real execution) the model explicitly named
and rejected that same move ("not inventing a shared validator... a new
abstraction layer"), doing only the literal requested mirroring. This is
one case, not a systematic sweep -- but it is real, disclosed, causal
evidence that this specific rule changes behavior, not merely correlated
survivorship. Raw evidence for the old-content run:
`results/2026-08-22-mutation-pilot-REF-BEH-025-oldcontent.jsonl` (gitignored).

## Supporting-skill ablation study (does the supporting skill earn its place?)

`scripts/run_ablation_study.py` runs the same case twice with a FIXED skill
set (bypassing the router entirely) -- once with only the primary skill,
once with primary + the one supporting skill under test -- so the graded
difference is real, causal evidence for a `required_supporting_skills`
claim, not just a human assertion. Costs two real model calls per case; not
free like the tools above.

```bash
python3 scripts/run_ablation_study.py \
  --cases evals/runtime/cases/canary.json --case-id R02-code-and-command-state \
  --primary-skill code-review --supporting-skill equipment-domain-modeling \
  --output /tmp/ablation-R02.jsonl
```

**Pilot result (2026-08-22, R02, code-review + equipment-domain-modeling):**
first real ablation run. code-review alone produced an equally
comprehensive state-model redesign (late-response semantics, recovery/
restart handling, rejection rules, required test scenarios all present and
detailed); the declared supporting skill mainly added
equipment-domain-modeling-native terminology precision (AttemptId/Reconciler
vocabulary) and an explicit self-justification of the skill choice, not
substantive completeness the primary skill alone was missing. One case, one
model -- not grounds to drop the supporting-skill claim, but real, honest,
somewhat surprising evidence against assuming every declared supporting
skill earns a large quality gain. Raw evidence:
`results/2026-08-22-ablation-R02-code-review-equipment-domain-modeling-claude.jsonl`
(gitignored).
