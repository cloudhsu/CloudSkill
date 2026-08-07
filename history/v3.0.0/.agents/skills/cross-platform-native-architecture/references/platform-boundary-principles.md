# Platform Boundary Principles

## Portability Is Not Uniformity

A good cross-platform architecture provides stable concepts while preserving differences callers must understand.

Examples:

- Mobile background suspension is not equivalent to desktop minimization.
- Graphics-context loss may require resource reconstruction.
- File paths and permissions differ.
- UI-thread rules differ.
- Hardware access and permissions differ.
- Packaging and update channels differ.

## Boundary Tests

An abstraction is justified when it isolates:

- A platform API.
- A hardware transport.
- A lifecycle difference.
- A build/deployment difference.
- A replaceable implementation.
- A test seam.
- A stable product capability.

An abstraction is suspect when it only renames a native API without reducing risk or variation.

## Ownership

Cross-platform failures often come from ambiguous ownership:

- Who owns the native handle?
- Which thread creates and destroys it?
- What happens when the platform destroys the surface first?
- Can resources survive context recreation?
- Which layer translates native events?
