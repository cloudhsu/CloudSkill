# Semiconductor Equipment Training Evidence

## Evidence status

- **Document-verified:** private newcomer-training presentations supplied by the user.
- **Public-sanitization rule:** this record omits company/product names, images, exact internal topology, dates, schedules, proprietary identifiers, and machine-specific operating values.
- **Scope:** the evidence supports generalized semiconductor-equipment domain capability and training/document capability. It does not define current production recipes, safety limits, vendor contracts, or operating procedures.

## Verified domain areas

The material demonstrates practical familiarity with:

- Cluster-tool decomposition into atmospheric frontend handling, central/vacuum transfer, and process-chamber functions.
- Carrier loading, wafer mapping, atmospheric transfer, alignment, loadlock pump/vent, vacuum transfer, chamber isolation, and process-chamber roles.
- Equipment components including valves, sensors, MFC/MFM, motors, throttle/pendulum valves, robots, pumps, heaters, chillers, power sources, and pressure gauges.
- Control-loop relationships such as controller, power stage, heater, and temperature feedback.
- Vacuum regions, range-dependent pressure measurement, roughing versus high-vacuum pumping, and atmosphere confirmation.
- PVD/magnetron sputtering principles including vacuum cleanliness, process gas, plasma, target/cathode, substrate/pedestal, magnetic field, bias, reactive sputtering, and qualitative process-quality relationships.
- Training style that moves from physical purpose and terminology to components, process behavior, and software-relevant consequences.

## Generalized pressures extracted into skills

- Software architecture must begin from material flow, environmental boundaries, process readiness, and authoritative physical evidence.
- Component identity should be based on physical purpose and capability, not only IO direction or communication protocol.
- Command acknowledgement, controller setpoint, process measurement, physical condition, and sequence completion are different states.
- Pressure and other measurements require units, range/source, timestamp, quality, and stale semantics.
- Generic PVD principles may identify required readiness and observability but cannot supply a production recipe or safe limit.
- Historical training values and vendor-specific behavior require current controlled-document verification.

## CloudSkill ownership

- `semiconductor-equipment-domain-knowledge` owns terminology, physical modules, component purpose, vacuum/PVD principles, and physical-to-software interpretation.
- `equipment-control-architecture` owns Sequence, material flow, readiness/interlocks, shared resources, distributed control, recovery, and deployment.
- `equipment-domain-modeling` owns component state, command, units, quality, reconciliation, snapshot, and capability models.
