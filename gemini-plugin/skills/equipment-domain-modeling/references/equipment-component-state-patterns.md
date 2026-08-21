# Equipment Component State Patterns

## Binary actuator

Typical fields/contracts:

- Desired command.
- Actual position/state.
- Transitioning/unknown.
- Position switches or controller status.
- Interlock and fail-safe state.
- Last command/attempt and error.

Do not assume a slit valve, gate valve, throttle valve, and pneumatic process valve share identical state machines.

## Discrete sensor

Typical fields/contracts:

- Actual state (e.g. present/absent, open/closed, in/out).
- Polarity (normally-open vs. normally-closed wiring, since raw signal level alone does not reveal logical state).
- Debounce/quality (a bare edge is not yet a confirmed transition).
- Timestamp of last confirmed transition.
- Alarm/fault when the signal is stuck, missing, or contradicts an interlocked expectation.

Examples include cover/door switches, position/proximity switches, and ATM/interlock switches. Do not treat a discrete sensor's raw level as the reported state without debounce and polarity resolution.

## Analog regulator

Typical fields/contracts:

- Desired setpoint and units.
- Controller-accepted/readback setpoint.
- Process value.
- Mode/enable.
- Allowed command range and measurement range.
- Stabilization tolerance/time.
- Alarm/fault/quality.

Examples include MFC flow control, pressure control, and temperature control. The control-loop owner must be explicit.

## Measurement

Typical fields/contracts:

- Value and engineering units.
- Sensor/gauge identity and active range.
- Timestamp and stale threshold.
- Validity/quality/status.
- Calibration or alarm metadata where required.

A measurement does not need Desired/Pending unless the device also exposes a configurable setpoint or mode.

## Motion

Typical fields/contracts:

- Command/target and attempt identity.
- Actual position or station.
- Homed, in-position, moving, stopped, faulted.
- Resource/path reservation.
- Timeout, stop, recovery, and late-completion behavior.

## Pump and utility lifecycle

Model lifecycle states such as unavailable, starting, ready, stopping, cooling/warming, regenerating, faulted, and unknown according to the actual device. Avoid reducing startup-dependent equipment to a Boolean.

## Process energy

Separate command/accepted power, actual/readback power, mode, ramp state, cooling/match readiness, fault/arc, and any independent process evidence such as plasma detection. A power supply status alone may not prove the intended chamber process condition.
