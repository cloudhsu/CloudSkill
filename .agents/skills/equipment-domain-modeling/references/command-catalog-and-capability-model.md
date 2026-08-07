# Command Catalog and Capability Model

## Four semantic tools

| Tool | Question | Equipment use |
|---|---|---|
| Inheritance | Is it a kind of? | ValveState is a ComponentState |
| Composition | What state/capability does it own? | Generator has PowerControlState |
| Interface capability | What can it do? | ISwitchable, IPositionable |
| Generic | What pattern repeats by type? | Signal<bool>, Signal<float> |

## Catalog fields

A command definition can contain command ID/name, required capability, payload schema, value type, unit, range, enum values, permission, interlock category, idempotency, timeout, and UI hints.

## Responsibility boundary

- Catalog defines a command contract.
- UI renders and collects an intent.
- Executor validates and dispatches.
- Driver/adapter performs device-specific transport.
- Polling/callback updates Actual.

Do not select a handler solely from UI control type or concrete component class when capability and command identity are the real contract.
