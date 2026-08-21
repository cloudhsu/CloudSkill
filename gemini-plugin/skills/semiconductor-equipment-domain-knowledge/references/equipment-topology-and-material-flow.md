# Equipment Topology and Material Flow

## Common module responsibilities

### EFEM

Typical responsibilities include carrier load/unload, wafer mapping, atmospheric transfer, and alignment/orientation. Common elements include load ports, an atmospheric robot, and an aligner.

### Main Frame / vacuum transfer system

Typical responsibilities include atmosphere-to-vacuum transition, loadlock pump/vent, vacuum-side transfer, shared robot/path coordination, and isolation of process chambers. Common elements include loadlocks, a transfer chamber, a vacuum robot, and slit/gate isolation valves.

### Process Chamber

A process chamber provides a controlled environment for a specific process or function. It may own recipe execution, chamber utilities, sensors, actuators, process-energy sources, and process-specific readiness.

## Material and environment state

Track at least:

- Carrier and wafer identity.
- Physical location and occupancy.
- Robot/blade ownership.
- Atmosphere/vacuum/high-vacuum region.
- Door/slit/gate state.
- Pressure compatibility between adjacent regions.
- Contamination/isolation boundary.
- Transfer and process readiness.

A hardware topology does not define executable or network topology. A wafer-location state is safety- and recovery-relevant and should not be inferred only from the last command sent.

## Typical transfer implications

- Opening a boundary requires pressure/environment compatibility and motion clearance.
- Loadlock pump/vent is a state transition, not a delay timer.
- Shared robots and paths require reservation and arbitration.
- Reconnect or restart requires reconstructing location, occupancy, pressure, and valve state from authoritative evidence.

The exact path, module count, and responsibilities vary by product and must be confirmed from current controlled documents.
