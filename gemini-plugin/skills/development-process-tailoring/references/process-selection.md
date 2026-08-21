# Process Selection

## Waterfall or Stage-Gated Governance

Good fit when:

- Contractual deliverables and approvals are fixed.
- Hardware or procurement milestones dominate.
- Interfaces must be frozen before downstream work.
- Formal verification evidence is required.
- The cost of uncontrolled change is high.

Risks:

- False certainty.
- Late integration.
- Large feedback delay.
- Documentation accepted without executable evidence.

Controls:

- Early prototypes.
- Interface simulators.
- Risk-driven spikes.
- Incremental integration inside formal gates.

## Iterative Development

Good fit when:

- Requirements or architecture need progressive discovery.
- Early operational feedback is valuable.
- The system can be delivered in usable slices.
- Risk can be retired through prototypes and increments.

Risks:

- Repeated local changes without architectural convergence.
- Uncontrolled scope.
- Weak baseline/version discipline.

Controls:

- Iteration goals.
- Architecture runway only where justified.
- Definition of done.
- Periodic baseline and debt review.

## Agile Delivery

Good fit when:

- Stakeholders can provide frequent feedback.
- Priorities change.
- Work can be sliced vertically.
- Teams own delivery outcomes.

Risks:

- Ceremony without engineering discipline.
- Product backlog replacing system design.
- Short-term velocity optimizing against system quality.

Controls:

- Quality requirements in backlog and release gates.
- Architecture decisions.
- Integrated system increments.
- Outcome and defect metrics.

## Extreme Programming Practices

Good fit when:

- Requirements change frequently.
- Automated testing and continuous integration are feasible.
- Fast feedback and safe refactoring are important.
- Close collaboration is available.

Useful practices:

- Test-first or test-driven development where it improves design feedback.
- Continuous integration.
- Pairing or collaborative review.
- Small releases.
- Refactoring.
- Simple design.
- Collective code ownership with clear architectural stewardship.

Risks:

- Applying unit-test-centric practices to hardware behavior without sufficient integration simulation.
- Treating simple design as no architecture.
- High discipline requirements hidden behind informal process.

## Hybrid

Commonly appropriate for equipment and hardware/software products:

```text
Product/hardware stage gates
    + software iterative increments
    + agile prioritization
    + XP engineering practices
    + formal system integration and release evidence
```
