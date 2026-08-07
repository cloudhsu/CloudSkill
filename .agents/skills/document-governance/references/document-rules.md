# Document Rules

## Controlled Metadata

Include as appropriate:

- Document ID.
- Version.
- Status.
- Owner.
- Reviewer/approver.
- Effective date.
- Product/project/release.
- Source data.
- Classification.
- Superseded document.

## Normative Language

Use:

- Must: mandatory.
- Should: recommended unless a justified exception exists.
- May: permitted.
- Will: declared future behavior or commitment.

Avoid using “should” when a requirement must be verified.

## Precision

Bad:

- The system is fast.
- The update process is stable.
- The interface is user-friendly.

Better:

- The operator screen shall acknowledge an accepted command within 500 ms at P95 under the defined load.
- The update service shall recover from a network interruption without duplicate installation.
- A trained operator shall complete the standard update procedure without external assistance in the acceptance test.

## Tables and Metrics

Every table should identify:

- Definition.
- Unit.
- Population or denominator.
- Date range.
- Version scope.
- Exclusions.
- Source.
- Refresh date where applicable.

## Diagrams

Every diagram should identify:

- Viewpoint.
- Scope.
- Direction of flow.
- Runtime versus logical meaning.
- Legend.
- Source of truth.
- Version or date.

Do not mix deployment, component, sequence, and data-flow semantics in one diagram without explicit notation.
