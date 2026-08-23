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

## Module and topology capability declaration

Represent a variable-count or variable-role physical module -- a connection
port, an aligner station, a pressure-boundary module, or a motion system --
as a component with explicit configuration/capability properties, not as
fixed per-instance geometry or a generic shape carrying only a label.

For each such module define, as applicable to its family:

- Stable identity, orientation/attachment point, and endpoint geometry (a
  port or facet).
- Payload/scope, centering or motion capability, and configured duration (an
  aligner or similar motion station).
- Boundary/pressure-domain role, shelf or slot layout, and entry/exit
  assignment (a pressure-boundary module).
- Observation/mapping state, home/teach calibration validity, and a
  per-action motion profile (a robot or transport mechanism).

Keep the count, layout, and attachment map of these modules as configuration
data read at composition time, not a hardcoded per-instance drawing. A
vendor page or reference example showing one arrangement (a specific port
count, shelf count, or capability set) is a corroborating example of a valid
variant, never a confirmed default for the current equipment -- keep exact
instance values in the equipment configuration, sourced and
confidence-scoped separately from the schema that allows them to vary. A
logical grouping used for presentation or scheduling (e.g. a zone spanning
several ports) is not the physical port/carrier identity it groups and must
not substitute for it.

Do not let a shared visual base component collapse two modules with
different capability profiles (two motion-station types, or two
pressure-boundary types) into one rule merely because they render
similarly. Do not let animation completion, drawing order, or a rendered
link imply capability, readiness, or physical permission that the
underlying component/config model has not asserted.
