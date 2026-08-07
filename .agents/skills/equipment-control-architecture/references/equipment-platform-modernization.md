# Equipment Platform Modernization

## Two coordinated roadmaps

Maintain separate but linked views:

- **Capability roadmap:** automatic UI, configurable components, recipe, history, manual flow, automatic flow, real-equipment coverage.
- **Migration/deployment roadmap:** shared contracts, logical separation, single-PC client/server, multi-PC simulation, real-hardware pilot.

Do not merge them into one date list. A capability can exist before distribution; a process split can exist before full product capability.

## Checkpoint contract

Each checkpoint records:

- Architecture hypothesis being tested.
- Smallest end-to-end vertical slice.
- Supported and excluded devices/functions.
- Exact deployment topology.
- Artifact and configuration versions.
- Demonstrable user/engineering outcome.
- Failure and recovery cases.
- Evidence collected.
- Rollback and stop conditions.
- Decision and next-stage entry criteria.

## Recommended ladder

1. Baseline and contract inventory.
2. Simulated IO and component vertical slice.
3. Config-derived state and command UI.
4. Same-machine responsibility/process split.
5. Real protocol across simulated nodes.
6. Manual material handling and recipe path.
7. Automatic sequence with resource arbitration.
8. One real-equipment pilot.
9. Product/chamber expansion.

Keep structural refactoring, behavior changes, topology changes, and field-hardware activation separately attributable.
