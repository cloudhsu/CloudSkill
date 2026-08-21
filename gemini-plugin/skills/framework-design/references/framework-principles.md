# Framework Design Principles

## Capability Versus Purpose

Frameworks describe reusable capability.

Products describe business or domain purpose.

Examples of capabilities:

- Communication.
- Scheduling.
- Command dispatch.
- State persistence.
- Plug-in lifecycle.
- Logging and tracing.
- Resource loading.
- UI infrastructure.
- Deployment and update orchestration.

Examples of purpose:

- A specific wafer process.
- A particular IC test flow.
- A game rule.
- A product-specific recipe.
- A customer's operational procedure.

## Evidence Required for Abstraction

An abstraction should normally correspond to at least one of:

- Multiple current implementations.
- A confirmed upcoming implementation.
- Platform or hardware isolation.
- Independent testing requirement.
- Independent lifecycle.
- Failure containment boundary.
- Deployment or version boundary.
- Security or trust boundary.
- Stable public contract.

“May be useful someday” is insufficient by itself.

## Framework Failure Modes

Watch for:

- Leaking product terminology into the kernel.
- Callback or event systems with undefined ordering.
- Service locators hiding dependencies.
- Plug-ins without lifecycle and compatibility rules.
- Configuration becoming an untyped programming language.
- Extension points that bypass safety or observability.
- Shared mutable state.
- Cross-platform APIs that erase important native semantics.
- Frameworks that require copying internal code to support a new product.
- A generic core that is harder to understand than each duplicated product implementation.

## Capability and Registry Contracts

When implementations use different transports, define the reusable contract in
terms of product capabilities, then attach transport-specific limits, lifecycle,
error and cancellation semantics. Do not erase a difference that affects what a
caller may safely request or conclude.

If discovery or registration is an authoritative contract, name one source,
one shared executable adapter, and every required consumer. Match the closest
existing authoritative-contract pattern: test positive propagation so a new
entry reaches every consumer without copied edits, and inject negative drift so
a copied registry, switch or stale consumer is rejected. A centralized file
without both mutation directions is only a proposed authority.

## Success Criteria

A framework is successful when:

- Adding a consumer requires mainly domain code.
- Existing consumers are not destabilized by unrelated extensions.
- Runtime behavior remains traceable.
- Failure recovery is consistent.
- The public contract changes less frequently than implementations.
- Teams can explain which behavior belongs inside and outside the framework.
