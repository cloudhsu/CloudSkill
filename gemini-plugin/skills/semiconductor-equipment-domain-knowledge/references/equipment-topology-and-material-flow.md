# Equipment Topology and Material Flow

## Common module responsibilities

### EFEM

Typical responsibilities include carrier load/unload, wafer mapping, atmospheric transfer, and alignment/orientation. Common elements include load ports, an atmospheric robot, and an aligner.

### Main Frame / vacuum transfer system

Typical responsibilities include atmosphere-to-vacuum transition, loadlock pump/vent, vacuum-side transfer, shared robot/path coordination, and isolation of process chambers. Common elements include loadlocks, a transfer chamber, a vacuum robot, and slit/gate isolation valves.

### Process Chamber

A process chamber provides a controlled environment for a specific process or function. It may own recipe execution, chamber utilities, sensors, actuators, process-energy sources, and process-specific readiness.

### Chamber function and where its duration comes from

A chamber is one unit of equipment, and what it does is its function: PVD, ALD,
pre-clean, degas, Flip, and so on. The function is uniformly named the recipe.
A Flip chamber's recipe only flips, taking a fixed time such as 5 or 10 seconds
that depends on the hardware configuration. A PVD chamber's recipe does physical
vapor deposition and may take around 1500 seconds. An ALD chamber's recipe does
atomic layer deposition and may take around 2000 seconds. A degas recipe heats,
and different degas recipes may heat to different temperatures, so the recipe
also changes the heating time. All times here are illustrative, not verified
values. "Cluster tool" names only how chambers are integrated; it does not
decide a chamber's function or duration source.

A loadlock's base operations are pump down and vent, each with its own
configured time; that time is the planning and simulation time source, while
completion in the control layer still follows the measured endpoint (see
`domain-to-software-contracts.md`). Customization may add a function such as
heating or cooling that takes a recipe. Example: a wafer enters the loadlock, cools by recipe,
the loadlock vents only after the temperature is reached, and then the ATM
robot takes the wafer out. Read the function set from how the equipment is
configured, never assume every loadlock or chamber of a type has the same one.

A recipe belongs to one chamber and does not span chambers. A process
chamber always has a process recipe; a Flip chamber has a fixed flip-only recipe; a
loadlock's pump down and vent use their own configured time, and it may have a
recipe function attached. A wafer's path through several chambers is the
sequence (its name in this project), a separate thing from any recipe. The
editable parameters of a recipe depend on that chamber's configuration: two PVD
chambers may differ by vendor or build, for example one more or one fewer MFC,
so the basic recipe parameter set differs. Read a chamber's recipe parameter
set from its own configuration, not from its function name alone.

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
