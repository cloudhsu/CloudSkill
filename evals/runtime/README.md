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
