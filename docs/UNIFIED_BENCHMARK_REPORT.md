# Unified Benchmark report

`scripts/render_benchmark_report.py` turns existing routing, behavior, panel,
and lifecycle JSON into one Markdown report plus optional JSON. It is a reader,
not a grader: it never runs a model, changes a source verdict, or authorizes a
merge, tag, or release.

```bash
python3 scripts/render_benchmark_report.py \
  --subject developing-skills \
  --routing-baseline path/to/red-routing-summary.json \
  --routing-candidate path/to/green-routing-summary.json \
  --behavior-baseline path/to/red-behavior-summary.json \
  --behavior-candidate path/to/green-behavior-summary.json \
  --panel path/to/panel.json \
  --lifecycle .agents/skills/developing-skills/lifecycle.json \
  --output .local/reports/developing-skills-benchmark.md \
  --json-output .local/reports/developing-skills-benchmark.json
```

Missing inputs remain `NOT_PROVIDED`; malformed inputs make the report
`INVALID_INPUT`. A source `FAIL`, `DEGRADED`, or `UNKNOWN` remains unchanged.
