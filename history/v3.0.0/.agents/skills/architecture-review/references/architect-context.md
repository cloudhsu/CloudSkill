# Architect Context

## Experience Pattern

The architect's recurring capability is not tied to one industry. It is the construction of reusable frameworks and engines across:

- Cross-platform IC mass-production tools.
- Hardware and communication abstraction.
- Cross-platform GUI and application frameworks.
- Cross-platform 2D game engines.
- Semiconductor equipment control systems.
- Deployment, remote-update, field-service, and diagnostic tooling.

## Typical Architectural Lens

The architect tends to ask:

- What is the stable abstraction?
- What is domain-specific?
- Which part is an engine or framework capability?
- Where does state live?
- How can a new product or platform be added without copying the entire project?
- Can a failure be observed, reproduced, recovered, and audited?
- Is the abstraction solving a real variation boundary or only satisfying a pattern?

## Important Distinction

Do not assume equipment concepts are universal framework concepts.

Examples:

- Device communication, scheduling, logging, state persistence, plug-in loading, and command dispatch may be reusable capabilities.
- PVD, ALD, wafer process semantics, chamber sequence, and recipe meaning are domain concepts.
- Rendering, input, scene, resource, and game-loop concepts may provide useful analogies but should not be copied into equipment control without validating lifecycle and safety semantics.

## Communication Level

Use senior software-architecture discourse. Explain unfamiliar domain assumptions, but do not dilute architecture analysis into generic textbook instruction.
