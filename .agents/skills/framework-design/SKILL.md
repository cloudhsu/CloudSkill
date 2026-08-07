---
name: framework-design
description: Use when reusable capability must be separated from product or domain behavior through framework, SDK, plug-in, platform, extension-point, state/command, or product-line contracts.
---

# Framework Design

Design a framework only when there is a demonstrated reuse, variation, replacement, lifecycle, or platform boundary.

Read `references/framework-principles.md` before making recommendations.

## Workflow

### 1. Identify consumers

List the actual or expected products, platforms, devices, applications, or modules that will consume the framework.

Separate confirmed consumers from hypothetical ones.

### 2. Identify invariants and variation axes

For each candidate abstraction, state:

- What remains invariant.
- What varies.
- When variation is selected: compile time, startup, configuration, runtime, or per request.
- Who owns the implementation.
- Whether consumers need substitution, composition, extension, or only configuration.

### 3. Define the minimum stable kernel

The kernel should contain only concepts that:

- Are shared across multiple consumers.
- Have stable semantics.
- Need a common lifecycle or contract.
- Benefit from central observability, safety, or compatibility control.

Keep product policy outside the kernel.

### 4. Design extension points

For each extension point define:

- Contract.
- Lifecycle.
- Threading model.
- Error propagation.
- Cancellation.
- Version compatibility.
- Resource ownership.
- Discovery and registration.
- Testing strategy.

Do not add an interface without explaining the variation or isolation boundary.

### 5. Model state and commands

Specify:

- State owner and source of truth.
- Command identity and lifecycle.
- Synchronous versus asynchronous semantics.
- Idempotency.
- Timeout and late completion.
- Persistence and reconstruction.
- Event ordering and replay assumptions.

### 6. Evaluate cross-platform boundaries

Distinguish:

- Portable policy.
- Platform service contract.
- Platform-specific implementation.
- Capabilities that cannot be normalized without semantic loss.

Avoid designing only for the lowest common denominator.

### 7. Produce an adoption path

Include:

- Pilot consumer.
- Compatibility adapter.
- Migration order.
- Deprecation policy.
- Measurement criteria.
- Exit criteria if the framework does not provide value.

## Output Format

1. Framework purpose and non-goals
2. Confirmed consumers
3. Invariants and variation axes
4. Kernel responsibilities
5. Extension-point contracts
6. State and command model
7. Cross-platform strategy
8. Failure and observability model
9. Adoption and migration plan
10. Risks and rejected abstractions
