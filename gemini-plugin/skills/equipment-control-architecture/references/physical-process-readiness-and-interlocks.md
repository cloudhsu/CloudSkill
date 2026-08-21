# Physical Process Readiness and Interlocks

## Readiness is a predicate, not a flag copied from the UI

For each operation define the observations and policies that make it safe and meaningful.

### Material transfer

Check:

- Authoritative wafer/source/destination occupancy.
- Robot/blade/path reservation and position.
- Door/slit/gate actual position.
- Pressure/environment compatibility.
- Chamber/loadlock mode and availability.
- Blocking alarms and interlocks.

### Pump-down and vent

Check:

- Chamber isolation and valve path.
- Pump/utility readiness.
- Applicable gauge range and valid measurement.
- Endpoint criteria and stable interval.
- Timeout versus uncertain physical state.
- Safe recovery if a pump, valve, or gauge faults.

### Gas and pressure stabilization

Check:

- Correct gas-line identity and allowed recipe.
- MFC command/actual flow and units.
- Throttle/pressure-control mode.
- Pressure-gauge validity and stabilization tolerance.
- Exhaust/pump state and safety conditions.

### Power/plasma/process

Check:

- Cooling/temperature readiness.
- Target, pedestal, magnet/rotation, matching, and power-source readiness as applicable.
- Gas/pressure stability.
- Arc/fault/interlock state.
- Distinct evidence for power accepted, plasma detected, and process step completed.

## Interlock layers

- Hardware/electrical safety where required.
- Device/chamber local interlock close to the physical side effect.
- Equipment/service validation for commands and current state.
- Sequence policy for process ordering and recovery.
- UI guidance, which is never the only protection.

Do not place a physical safety rule only in a remote GUI or configuration generator.
