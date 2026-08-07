# Domain to Software Contracts

Translate every important physical statement into an observable software contract.

| Physical concept | Software contract questions |
|---|---|
| Wafer location | Who is authoritative? How is occupancy reconstructed after restart? |
| Atmosphere/vacuum boundary | Which pressure and valve conditions permit opening? |
| Pump-down/vent | What measured endpoint completes the transition? What is timeout versus failure? |
| MFC flow | What gas line, units, range, desired value, actual flow, and stabilization rule apply? |
| Pressure measurement | Which gauge/range is valid? What quality/status makes the value usable? |
| Heater/chiller | Which controller owns the loop? What are setpoint, PV, ready, and fault semantics? |
| Robot motion | What reserves the path? What proves in-position? How is late completion reconciled? |
| Power/plasma | What proves power accepted, plasma present, and process-ready? |
| Slit/gate valve | What pressure/path/interlock preconditions and actual-position feedback apply? |
| Recipe step | Which physical outcome, not just elapsed time, completes the step? |

## Readiness predicate pattern

A readiness predicate should identify:

- Required observations and their age/quality.
- Stable interval or tolerance where necessary.
- Blocking alarms/interlocks.
- Resource ownership.
- Required mode/config/recipe version.
- Whether simulation can provide equivalent evidence.

## Completion pattern

Separate:

- Command accepted.
- Device/controller action started.
- Physical readback reached.
- Process condition stabilized.
- Sequence-level step completed.

Do not collapse these states merely because the current implementation is synchronous.
