# Equipment software Skill-family closure assessment — 2026-08-19

## Scope and evidence level

This assesses the reusable Skill system, not a released equipment product.
ISO/IEC 25010:2023 is used as a classification framework. Model behavior,
deterministic validation and public-source review exist; hardware, approved
recipes, production traces, calibrated WPH and field recovery remain `NOT RUN`.
No existing or previously refactored simulator implementation was rewritten.

Evidence levels are `E0` not defined/not run, `E1` reasoned documentation,
`E2` deterministic contract/test, `E3` model/simulator/integration execution,
and `E4` target hardware or field evidence. A score never overrides a hard
gate.

## Development loop and owners

| Loop stage | Primary owner Skills | Current support |
|---|---|---|
| Existing-system discovery | codebase-architecture-discovery, architecture-review | Supported at analysis level; real repository evidence required |
| Physical/domain interpretation | semiconductor-equipment-domain-knowledge | Supported, public and vendor-neutral |
| State, command and readback model | equipment-domain-modeling | Supported; product mappings remain implementation work |
| Sequence, resources, interlocks and restart | equipment-control-architecture | Supported as architecture/contract; hardware safety is not certified |
| Tray-descum family semantics | tray-descum-simulator-development | 5-case Luna/Sol GREEN |
| Configurable cluster-tool semantics | cluster-tool-simulator-development | 4-case Luna/Sol GREEN |
| Bonder/debonder pair semantics | wafer-bonder-debonder-development | 5-case Luna/Sol GREEN |
| Cross-family throughput/capacity | wph-equipment-simulator-development | 5-case Luna/Sol GREEN; numeric/calibration evidence absent |
| Safe implementation change | safe-incremental-refactoring, code-review, framework-design | Supported process; whole rewrite requires explicit authority |
| Quality/release decision | software-quality-iso25010, development-process-tailoring | Available but proactive composition routing needs improvement |
| Skill evolution/release | developing-eval, developing-skills, runtime evaluation | Deterministic lifecycle and semantic disposition exist; new family Skills remain privately held |

## New Skill responsibilities and advantages

| Skill | Owns | Explicitly does not own | Advantage over the former generic model |
|---|---|---|---|
| tray-descum-simulator-development | Material/Tray/pocket identity, completeness, descum admission, unload, return, projection and recovery | Map/bin die sorting, vacuum cluster topology, capacity result | Prevents visually similar Tray equipment from receiving the wrong sorting or cluster semantics |
| cluster-tool-simulator-development | Versioned capability graph, pressure domains, configurable routes, arm/path custody, cardinality and topology recovery | Generic production safety authority or final WPH result | Replaces fixed-layout assumptions with configurable module/capability semantics |
| wafer-bonder-debonder-development | Wafer/carrier/pair lifecycle, temporary versus permanent method families, cleaning, metrology provenance and uncertain separation | Die-attach packaging, universal process limits, final WPH result | Preserves pair identity and method-specific recovery instead of one opaque equipment flag |
| wph-equipment-simulator-development | Discrete-event capacity, scenario fingerprint, good-output measurement, replications, confidence and bottleneck evidence | Physical interlock authority or invented family topology | One reusable capacity owner can compose several equipment families without flattening their physics |

## Provisional architecture fitness

The score describes the Skill-family architecture at `E2–E3`, not product
quality.

| Dimension | Weight | Rating (0–4) | Weighted result | Basis |
|---|---:|---:|---:|---|
| Responsibility/owner clarity | 15 | 4 | 15.0 | Family/WPH/control/domain boundaries are explicit |
| State/source-of-truth | 15 | 4 | 15.0 | Custody, readback, command and projection are separated |
| Failure/recovery | 15 | 3 | 11.25 | Restart/unknown/quarantine cases pass; no field execution |
| Compatibility/extensibility | 10 | 4 | 10.0 | Topology/cardinality/product family are configuration/composition seams |
| Testability/observability | 15 | 3 | 11.25 | 19 behavior cases and deterministic gates; no real simulator fault injection |
| Change/migration safety | 10 | 3 | 7.5 | Brownfield guard and smallest slices exist; product migration not run |
| Performance/capacity | 10 | 3 | 7.5 | WPH contract is strong; calibrated numeric evidence absent |
| Security/safety | 10 | 2 | 5.0 | Interlock ownership exists; hazard/security/field certification absent |
| **Total** | **100** |  | **82.5** | **Provisional architecture fitness, not release quality** |

Hard gates still open: real custody/restart fault injection, approved interlock
and process criteria, hardware/field evidence, calibrated traces, product
security/hazard review, and an explicit later public-distribution decision.

## ISO/IEC 25010 support view

| Characteristic | Skill-system support | Evidence | Gap |
|---|---|---|---|
| Functional suitability | Strong | E3 | Product requirements and implementation tests absent |
| Performance efficiency | Partial | E2–E3 | No calibrated WPH, latency or resource measurements |
| Compatibility | Partial | E2 | No host/protocol/device/version matrix execution |
| Interaction capability | Low | E1 | HMI/operator usability is outside this increment |
| Reliability | Moderate | E3 | Recovery reasoning passes; field restart/fault injection absent |
| Security | Low | E1 | Identity/access/threat model not in equipment family Skills |
| Maintainability | Strong | E2–E3 | Owner boundaries, routing and brownfield guard are tested |
| Flexibility | Strong | E3 | Product-family and topology variation are explicit |
| Safety | Partial | E2 | Architecture owns interlocks; approved limits and hardware evidence absent |

## Closure decision

The knowledge/architecture/evaluation loop is substantially closed: public
evidence can become de-identified family semantics, compose with control/domain
owners, execute behavior cases, and reach a governed release gate. The product
engineering loop is not closed until those contracts are mapped incrementally
onto the existing refactored implementation and verified with simulator,
integration, target hardware and field evidence. The correct status is therefore
"architecture and Skill loop supported; product/field loop partial," not
"equipment software complete."
