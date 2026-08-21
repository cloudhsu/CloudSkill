# Full-stack Boundaries

## Client

Owns:

- Interaction state.
- Presentation.
- Input assistance.
- Local transient state.
- Accessibility behavior.

Does not own authoritative:

- Price.
- permission.
- account identity.
- workflow legality.
- account balance.
- business deadline.
- final persistence result.

## HTTP/API Layer

Owns:

- Identity extraction.
- Request validation.
- Authorization entry check.
- Status/error mapping.
- Response shape.
- Correlation metadata.

Should not absorb core transaction policy merely because it is convenient.

## Application Service

Owns:

- Use-case orchestration.
- Transaction boundary.
- Domain policy coordination.
- External side-effect sequencing.
- Result construction.

## Domain Policy

Owns:

- Invariants.
- State-transition legality.
- Business calculations.
- Domain-specific validation.

## Repository/Persistence Adapter

Owns:

- Queries and writes required by the use case.
- Mapping between persisted and application representations.

Does not automatically own transaction, save, connection lifecycle, or business orchestration.

## Operations

Deployment constraints are architecture.

Examples:

- A database that supports only one writer.
- A process that loads the entire database into memory.
- A reverse proxy that terminates TLS.
- A file-based backup requiring a flush/integrity check.
