# Compatibility Façade and Seams

## Compatibility Façade

A façade can remain while internal responsibilities migrate.

Benefits:

- Existing callers remain stable.
- Migration can be incremental.
- Tests can compare old and new paths.
- Release risk is reduced.

Costs:

- Temporary duplication or delegation.
- Constructor wiring can grow.
- The façade may remain too long.
- Ownership may be ambiguous unless documented.

Define an exit or stabilization condition. A compatibility façade is not automatically the final architecture.

## Dynamic Seams

Existing systems may depend on:

- Monkeypatchable methods.
- Callback injection.
- Runtime substitution.
- Fake clocks.
- Fault-injection hooks.
- Stable method names.

Preserve these deliberately when they provide verification value. Do not accidentally freeze every accidental implementation detail.

## Dual Implementation Behind a Single Compile-Time Switch

When a shared implementation is replaced, and the new implementation's
correctness in the actual target environment is not yet independently
confirmed (not merely "compiles" or "the API reports success" -- an
outcome someone outside the change can observe and confirm), do not delete
the old implementation in the same change that introduces the new one.

Do instead:

1. **Rename the old implementation to say what it actually is**, rather
   than deleting it. A generic name like the original component's name
   stops being accurate once a second implementation exists beside it --
   picking it back up later requires knowing it was ever there.
2. **Add the new implementation alongside it**, both satisfying the same
   existing interface/base type. No interface change is needed if the
   old implementation already conformed to one.
3. **Select between them with exactly one compile-time flag**, defined in
   a single, obviously-named location (a dedicated small header/config
   file, not scattered `#ifdef`s repeated at every call site). Document
   in that one place which value is currently the intended direction and
   why, and that flipping it requires a rebuild -- this is deliberately
   not a runtime toggle, so there is no path for it to change silently
   in a running system.
4. **Only remove the old implementation and the flag in a later, separate
   change**, once the new implementation's correctness has actually been
   confirmed by the outside observation that matters for this component
   (a user, an integration test against a real dependency, a field
   report) -- not from source inspection or a success return code alone.

Never edit both implementations' logic in the same change that also flips
the flag's default -- that reintroduces exactly the untangled-cause
problem this pattern exists to avoid: if something regresses afterward,
there are now two independent variables (which implementation is active,
and what changed inside it) instead of one.

This differs from the general Compatibility Façade above in shape, not
intent: a façade lets responsibilities migrate underneath a stable calling
surface while both old and new logic may be partially entangled during the
transition. This pattern is for two complete, independent, side-by-side
implementations of an already-existing interface, where the goal is a
clean A/B switch with no shared internal state -- appropriate specifically
when the new implementation's behavior in production-like conditions is
still an open question, not yet a confirmed replacement.

## Capability Ports

Prefer ports that expose only required operations.

```text
Query repository: all/get
Command repository: run
Application service: transaction
```

The exact shape depends on the language and system. The principle is least authority and explicit ownership.
