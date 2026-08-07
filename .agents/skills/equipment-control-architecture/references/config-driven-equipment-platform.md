# Config-driven Equipment Platform

Configuration can reduce duplicated chamber and UI code only when it is governed as a versioned contract.

## Configuration domains

- Component identity and type.
- Capabilities and supported commands.
- DIO/AIO/fieldbus binding.
- Engineering units, ranges, scaling, and conversion.
- Interlocks and enable conditions.
- Recipe and tolerance binding.
- UI label, grouping, editor type, permissions, and presentation hints.
- Product/chamber variant and deployment identity.

## Required controls

- JSON/XML/schema or equivalent machine validation.
- Semantic validation across fields and references.
- Version and migration policy.
- Provenance, reviewer, release baseline, and artifact hash.
- Safe behavior for unknown types or fields.
- Separation of product policy from reusable capability.
- Clear runtime reload versus restart semantics.
- Configuration backup and rollback.

## Automatic UI

The UI may project component capabilities and command metadata into controls. The command receiver still validates identity, capability, value type, range, permission, interlock, and current operating state.

## Common-library governance

Choose one authority for source, package, and built artifacts. Avoid committing ad hoc DLL copies as the only compatibility mechanism. Define package version, dependency constraints, binary compatibility, build reproducibility, and rollback before multiple products consume the shared kernel.
