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
