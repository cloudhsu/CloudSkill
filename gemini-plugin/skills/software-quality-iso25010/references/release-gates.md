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
