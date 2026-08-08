# CloudBox runtime model evaluations

This directory contains executable model-routing evaluations. It complements, but does not replace, `evals/skill-routing-cases.csv` and `evals/behavior/cases/`.

## Evidence levels

1. `validate_runtime_evals.py` proves the suite, schema, workflow, and deterministic grader are internally consistent.
2. `run_runtime_evals.py --dry-run` proves request assembly without calling a model.
3. A normal runner invocation proves that a named local or remote model returned a structured routing decision for each attempt.
4. `grade_runtime_evals.py` deterministically compares those decisions with the Canary expectations.
5. These routing checks do not prove the semantic quality of a complete engineering answer; that requires separate behavior or answer-quality evaluation.

## Local Ollama execution — no API key

Install and start Ollama, then make sure the local model exists:

```bash
ollama pull qwen3:4b
ollama list
```

Run one fast smoke case first:

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --case-id R06-chinese-translation-no-skill \
  --repeat 1
```

Run all eight Canary cases:

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --repeat 1 \
  --num-ctx 4096
```

The default provider is `ollama`, the default model is `qwen3:4b`, and model thinking is disabled for deterministic JSON routing. The runner calls only `http://127.0.0.1:11434` unless `--ollama-url` is supplied.

Grade the latest result:

```bash
RESULT="$(ls -t .local/runtime-evals/*.jsonl | head -1)"
python3 scripts/grade_runtime_evals.py \
  --input "$RESULT" \
  --output "${RESULT%.jsonl}-summary.json" \
  --allow-failures
cat "${RESULT%.jsonl}-summary.json"
```

`--allow-failures` is useful for small local models because the report is still generated when the strict 100% Canary gate fails.

## Optional OpenAI execution

```bash
export OPENAI_API_KEY="..."
python3 scripts/run_runtime_evals.py \
  --provider openai \
  --model <model> \
  --repeat 3
```

Results default to `.local/runtime-evals/`, which is excluded from Git. The local result records contain the routing decision, timing, usage metadata, and raw model JSON text for diagnosis. They do not contain API credentials.

## GitHub Actions

The `CloudBox Runtime Model Eval` workflow remains an OpenAI-provider workflow because a GitHub-hosted runner does not have access to the user's local Ollama service. Ordinary push and pull-request validation remains deterministic and does not call a model.

## Canary release gate

For the eight-case suite:

- overall pass rate: 100%
- primary-skill accuracy: 100%
- execution-order accuracy: 100%
- no-skill accuracy: 100%
- forbidden-selected-skill violation rate: 0%
- router self-inclusion rate: 0%
- invalid-output rate: 0%

A failed local 4B-model run is diagnostic evidence. It does not automatically prove that the Skill is wrong: failures may come from model capacity, schema adherence, prompt pressure, or Skill metadata. Review repeated failures before modifying a Skill.
