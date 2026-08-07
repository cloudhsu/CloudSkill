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

## Capability Ports

Prefer ports that expose only required operations.

```text
Query repository: all/get
Command repository: run
Application service: transaction
```

The exact shape depends on the language and system. The principle is least authority and explicit ownership.
