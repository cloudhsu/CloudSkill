# Equipment Skill RED baseline — 2026-08-19

## Execution identity

| Field | Luna baseline | Sol baseline |
|---|---|---|
| Requested model | `gpt-5.6-luna` | `gpt-5.6-sol` |
| Managed agent id | `01a019ea-7418-7b32-85e7-709c80e9864e` | `01a019ea-743d-72d2-8293-9dfabc4e5cfc` |
| Role | read-only pre-change executor | read-only pre-change executor |
| Authoritative baseline commit | `6e4e06cdedc1b90f91556a0a4b5a10ddc0936ba0` | `6e4e06cdedc1b90f91556a0a4b5a10ddc0936ba0` |
| Isolation | `git show HEAD:<path>` only; current uncommitted candidate prohibited | same |
| Result | RED observed on all four pressures | RED observed on all four pressures |

The Sol response reported the baseline hash correctly. The Luna response's
self-reported hash ended in `6ba6`; local `git rev-parse HEAD` proves `6ba0`, so
the inconsistent self-report is retained here as an identity/evidence warning
and is not treated as repository authority. Exact requested model identity
comes from the managed sub-agent selector rather than the model's generic
self-label.

## Actual baseline dispositions

| Pressure | Existing HEAD route | Luna observed omission | Sol observed omission | RED |
|---|---|---|---|---|
| Fixed atmospheric Tray loading followed by descum | WPH plus generic equipment control/domain | no descum stage semantics, persistent pocket mapping or explicit partial-Tray process policy | no descum readiness/completion, end-to-end slot identity or partial-Tray process policy | FAIL |
| Configurable cluster tool with mixed cardinalities and metrology | generic equipment control/domain; old WPH topology not applicable | no single/mini-batch/twin cardinality, metrology contract or cross-module capacity rule | no reusable configurable cluster simulator, coupled reservation/recovery or metrology route | FAIL |
| Temporary bond/debond plus die-to-wafer hybrid bonding | generic equipment control/domain | no distinct method lifecycles, queue-time budget or die/site mapping | no reversible pair lifecycle, hybrid distinction, die/site genealogy or queue-time constraints | FAIL |
| Cross-equipment WPH and good-output denominator | old product-shaped WPH plus generic equipment control | no module-count/cardinality distinction, good-output metric or cross-family aggregation | no cardinality normalization, yield-aware denominator or regression against gross-move WPH | FAIL |

## Present baseline strengths

Both models found useful generic foundations rather than declaring the old
repository empty: material custody, shared-resource reservation, pressure and
readiness concepts, event authority, generic correlation, utilization and
bottleneck reporting. The candidate therefore extends these owners and defines
composition boundaries; it does not replace generic equipment-control or
domain-modeling Skills.

## Expected GREEN

- Tray-descum owns carrier/pocket identity, readiness, process and recovery
  semantics but delegates capacity deliverables to WPH.
- Cluster-tool owns versioned topology, pressure/custody routes, capability and
  resource cardinality but delegates production control and WPH appropriately.
- Bonder/debonder distinguishes temporary, permanent and die-to-wafer lifecycle
  identities without reserving an entire future route atomically.
- WPH owns cross-family event simulation, reproducibility, statistics,
  cardinality, good-output metrics and capacity evidence.

Hardware, recipe and field validation are outside this model RED and remain
`NOT RUN` unless separately executed.
