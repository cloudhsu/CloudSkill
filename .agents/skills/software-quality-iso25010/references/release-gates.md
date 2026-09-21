# Quality Release Gates

## Gate Types

### Hard gate

Release is blocked.

Use for:

- Critical safety violation.
- Unauthorized consequential action.
- Data corruption.
- Unrecoverable state ambiguity.
- Mandatory contractual or regulatory failure.
- Unsupported upgrade/rollback path.

### Conditional gate

Release requires accepted mitigation and accountable approval.

Use for:

- Known reliability degradation with containment.
- Performance target missed outside the primary operating envelope.
- Deferred maintainability work with quantified operational cost.

### Monitored target

Release may proceed, but production evidence must be collected.

Use when:

- The target requires field scale.
- The risk is bounded and reversible.
- Monitoring and rollback are effective.

## Gate Record

For each gate record:

- Requirement ID.
- Metric and threshold.
- Result.
- Evidence.
- Exception.
- Risk owner.
- Approval.
- Expiration/revisit condition.

Do not use a single average score to override a failed critical gate.

## Real-time and Native Evidence

For a decision that combines asynchronous observations, define freshness at the
decision point: timestamp authority/domain, correlation identity, allowed age
and skew, and behavior for missing, stale, duplicate and out-of-order samples.
Preserve the denominator for each disposition. Average latency or throughput
alone cannot prove that the values used together described the same operation
or sufficiently aligned physical interval.

Keep emulator/simulator evidence separate from evidence for each release cell
whose platform, architecture, ABI, build mode, device, driver or timing behavior
can change the result. Use risk to select required cells, but record unsupported,
not-run and failed cells explicitly with owners and hard, conditional or
monitored disposition; do not improve a pass rate by removing them.

For a distributed or config-driven system moving toward hardware, classify
evidence by the topology it exercised: simulated, same-machine multi-process,
multi-PC (real network), and real hardware. Each gate names the minimum class
that can satisfy it; a lower class never closes a gate that needs a higher one
(process-local runs cannot show network partition, clock skew or node-version
skew; simulation cannot show sensor, timing or safe-state behavior). Report
results per class with owner and disposition.

For a port or rewrite that must reproduce a legacy view or behavior, a
done/not-done verdict needs parity evidence, not build success. Map the legacy
authority chain (what owns state, timing, geometry and assets) before judging.
Compare deterministic frame fixtures captured at exact playback times, one
component and one state transition at a time. Report architecture parity,
state/custody parity and pixel parity as three independent gates, each
PASS/FAIL/NOT RUN, never one aggregate impression. Keep an explicit open list
of missing legacy assets, geometry, typography and timing semantics until each
is closed. A compile, matching class names or a smoke test closes none of the
three, and an approximate renderer is not reported as a faithful clone.

When a new path is compared with a legacy path, keep machine-readable events and add a compact per-workpiece timeline; state the configuration and run conditions; compare equivalent modes and timing permutations; and report the first divergence and any invariant failures. Report throughput separately from correctness: aggregate throughput alone never shows behavioral equivalence.
