# Validation status

CloudBox 5.6.0 adds executable Runtime Model Evals while preserving the 5.5.4 skill and plugin surface.

## Package-side checks completed

- `VERSION`, README, Codex manifest, Claude manifest, and `SKILL_MANIFEST.json` are set to `5.6.0`.
- The Runtime Eval routing schema is a closed, strict-output contract.
- The Canary Suite contains exactly 8 unique cases and references only the 17 canonical skill IDs.
- The deterministic grader passed an in-memory positive fixture and rejected an intentional negative fixture.
- The Runtime Eval runner completed Ollama and OpenAI dry-run request assembly without reading an API key or calling a model.
- Python syntax compilation completed for all new or modified Runtime Eval scripts.
- Package SHA-256 values were generated after validation.

## Full repository checks after copying

```bash
python3 scripts/run_all_checks.py
git diff --exit-code -- SKILL_MANIFEST.json
git diff --check
```

Expected additional output:

```text
Validated executable Runtime Eval suite: 8 Canary cases, 17 skill IDs
NOTE: static validation and synthetic grader checks do not call a model API.
```

## Actual model execution

This delivery environment did not execute the user's local Ollama model. After copying the package, run:

```bash
python3 scripts/run_runtime_evals.py \
  --provider ollama \
  --model qwen3:4b \
  --repeat 1 \
  --num-ctx 4096
```

Then grade the emitted JSONL file with `scripts/grade_runtime_evals.py`. A Runtime Eval is not considered executed merely because the suite, schema, workflow, mock server, or dry-run request plan passed.
