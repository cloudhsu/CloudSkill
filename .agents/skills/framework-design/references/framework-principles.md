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
- Reusable source still living in a host/test project's tree with only a
  compiled reference pointing at the library -- ownership stays ambiguous
  and invites a second copy; the library must physically own its source.
- Promoting an unconfirmed future consumer's guessed requirements into
  confirmed kernel semantics before its physical requirements are known --
  model it as an extension point with explicitly missing capabilities instead.
- A subclass override of a reusable periodic/worker mixin's callback
  running its own indefinite internal loop instead of returning promptly
  each tick -- this silently defeats the mixin's own pause/stop/
  cancellation flags, since those are only rechecked between ticks that
  the override never lets happen. Verify every override of such a callback
  returns after one unit of work.
- Two composed base classes/mixins declaring identically-named lifecycle
  methods for unrelated concepts (a domain play/stop/pause/resume
  interface and a generic thread-control start/stop/pause/resume mixin).
  Flag the collision explicitly and require the derived class to
  disambiguate with distinct, purpose-specific names rather than relying
  on qualified calls to sort it out silently -- and when a stop/teardown
  sequence releases a shared resource on the calling thread, require that
  the background thread using that resource has actually observed
  cancellation and returned/joined first, not merely that a cooperative
  flag was set.

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

Apply the same positive/negative pair to a shared visualization or projection
contract: a positive case with an alternate configuration (alternate
role/equipment IDs, not only the default/baseline names) proving generic
resolution, and a negative case for an unsupported topology or a host that
still runs its own parallel projection despite referencing the library.
Assert the temporal event-to-output sequence -- ordering, state transitions,
and a negative check that no two outputs claim the same authoritative slot at
once -- rather than only a final frame or default-named snapshot; a passing
default-only test is not evidence of family-general or host-adopted behavior.

## Success Criteria

A framework is successful when:

- Adding a consumer requires mainly domain code.
- Existing consumers are not destabilized by unrelated extensions.
- Runtime behavior remains traceable.
- Failure recovery is consistent.
- The public contract changes less frequently than implementations.
- Teams can explain which behavior belongs inside and outside the framework.
