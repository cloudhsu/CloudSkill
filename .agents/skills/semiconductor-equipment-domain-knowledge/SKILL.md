---
name: semiconductor-equipment-domain-knowledge
description: Use when a semiconductor-equipment task depends on the physical meaning of EFEM, load ports, loadlocks, transfer chambers, process chambers, vacuum pumps, pressure gauges, gas flow, heaters, power supplies, plasma, sputtering, or process readiness.
---

# Semiconductor Equipment Domain Knowledge

## Core principle

Interpret the physical equipment and process before translating it into software. Preserve the distinction between general process principles, product-specific implementation, recipe-specific values, and software contracts.

Read:

- `references/equipment-topology-and-material-flow.md`
- `references/component-capabilities-and-io.md`
- `references/vacuum-and-pvd-process-principles.md`
- `references/domain-to-software-contracts.md`

Use:

- `assets/SEMICONDUCTOR_EQUIPMENT_KNOWLEDGE_MAP.template.md`
- `assets/PHYSICAL_PROCESS_TO_SOFTWARE_CONTRACT.template.md`

## Workflow

### 1. Classify the domain question

Determine whether the primary need is:

- Equipment topology and wafer/material flow.
- Component purpose and capability.
- Vacuum, gas, thermal, motion, power, or plasma behavior.
- PVD process principles and readiness.
- Translation of physical behavior into software state, command, interlock, alarm, or sequence semantics.
- Training or terminology clarification.

Separate source-supported facts from inference. A historical training document may demonstrate domain knowledge but does not define the current machine, exact recipe, safe limit, or vendor behavior.

### 2. Map the material path and environmental boundaries

A common cluster-tool path may include:

`Carrier/FOUP -> Load Port -> ATM Robot -> Aligner -> Load Lock -> VCE Robot/Transfer Chamber -> Process Chamber -> return path`

Identify:

- Where the wafer is physically located.
- Which robot or mechanism may move it.
- Whether the current region is atmospheric, transitioning, vacuum, or high vacuum.
- Which door, slit valve, gate valve, or chamber boundary isolates environments and contamination zones.
- Which module owns transfer readiness and location truth.

Do not treat EFEM, Main Frame, Load Lock, Transfer Chamber, and Process Chamber as interchangeable boxes. Their physical responsibilities and failure consequences differ.

### 3. Interpret equipment modules by physical responsibility

Use the following high-level distinctions:

- **EFEM:** carrier handling, load/unload, mapping, atmospheric wafer transfer, alignment or orientation.
- **Main Frame / transfer system:** atmosphere-to-vacuum handoff, loadlock operation, vacuum-side transfer, chamber isolation, and shared transport.
- **Process Chamber:** controlled process environment, recipe execution, process utilities, measurement, and chamber-specific equipment.

A module name does not by itself define process ownership, executable ownership, network ownership, or team ownership. Use `equipment-control-architecture` when those software boundaries are the decision.

### 4. Classify components by capability rather than by one inheritance tree

Common families include:

- **Binary actuators:** electric/pneumatic valves, slit valves, simple on/off outputs.
- **Discrete sensors:** cover, position, atmosphere, limit, and interlock switches.
- **Analog regulators:** MFCs, throttle/pendulum valves, temperature controllers, controlled power outputs.
- **Measurements:** pressure gauges, thermocouples, flow meters, position or speed feedback.
- **Motion systems:** robots, motors, lift mechanisms, magnet rotation.
- **Vacuum utilities:** dry/roughing pumps, turbo pumps, cryogenic pumps, isolation valves.
- **Thermal utilities:** heaters, SCR/SSR power stages, chillers, cooling-water circuits.
- **Process-energy sources:** DC power, RF power, bias power, matching networks.

For each component identify command, readback, readiness, operating range, engineering units, fault, interlock, communication path, and physical side effects. Similar fields do not prove identical semantics.

### 5. Interpret vacuum as a staged physical state

Vacuum control is not one Boolean state. Distinguish:

- Atmospheric confirmation.
- Roughing or low-vacuum transition.
- High-vacuum establishment.
- Process-pressure regulation.
- Isolation and pressure equalization before opening a boundary.
- Gauge validity and measurement range.

Different gauge technologies are suited to different pressure regions. A displayed value is not trustworthy without range/status/quality information. A nominal “full-range” instrument may still have range-dependent accuracy or transition behavior; equipment may require an independent atmosphere switch or other confirmation.

Dry pumps commonly establish rough vacuum; turbo or cryogenic pumps commonly support higher-vacuum operation. Exact pumping sequence, crossover pressure, valve timing, and safe limits are machine-specific and must come from current controlled specifications.

### 6. Interpret PVD as a chain of readiness and controlled physical effects

A generalized magnetron-sputtering model includes:

- Establishing a clean vacuum environment.
- Confirming chamber, cooling, target/cathode, substrate/pedestal, gas, and power readiness.
- Introducing process gas and stabilizing pressure/flow.
- Applying DC/RF energy to generate and sustain plasma.
- Accelerating ions toward the target so target atoms are sputtered and deposited on the substrate.
- Controlling magnet, rotation, bias, temperature, gas chemistry, and time according to the process.
- Ramping down energy and gas, preserving safe isolation, and transitioning to the next approved state.

Magnetron fields affect electron confinement and plasma behavior. Substrate bias changes ion bombardment and can affect film stress or step coverage. Reactive sputtering introduces reactive gas and may exhibit hysteresis. These principles do not supply production recipe values.

### 7. Connect process variables to quality outcomes without claiming a recipe

Potential relationships include:

- Vacuum cleanliness and contamination risk.
- Target/gas purity and film impurity risk.
- Pressure and mean free path.
- Gas flow and process pressure.
- Power/plasma stability and deposition behavior.
- Magnetic-field distribution/rotation and uniformity.
- Bias and film stress or step coverage.
- Temperature/cooling and process stability.

Treat thickness, uniformity, step coverage, stress, rate, and contamination as quality outcomes requiring process-specific evidence. Do not infer a setpoint, tolerance, or acceptance limit from generic training material.

### 8. Translate domain facts into explicit software contracts

For each physical operation define:

- Preconditions and readiness predicates.
- Command and command authority.
- Expected readbacks and completion evidence.
- Interlocks and where they are revalidated.
- Timeouts, uncertain completion, and recovery.
- Alarm/fault severity and operator action.
- Traceability to wafer, chamber, recipe step, device command, and readback.
- Engineering units, valid range, sensor quality, and stale threshold.

Examples:

- `OpenSlitValve` requires compatible pressure domains, robot/path clearance, chamber availability, and authoritative position readback.
- `StartPlasma` requires controlled pressure/flow, cooling, power readiness, and applicable interlocks; a power-command acknowledgement is not plasma confirmation.
- `SetMfcFlow` requires gas-line identity, units, allowed range, command acceptance, actual-flow readback, and stabilization criteria.

Use `equipment-domain-modeling` for data and command structures. Use `equipment-control-architecture` for workflow, shared resources, distributed control, interlocks, and recovery.

### 9. State uncertainty and safety limits

When source material is historical, incomplete, or product-specific:

- Mark exact values, ranges, protocol choices, and safety behavior as requiring current verification.
- Do not convert educational diagrams into operating procedures.
- Do not recommend bypassing hardware or safety interlocks.
- Do not claim a process result without current recipe, hardware, metrology, and acceptance evidence.
- Keep confidential company, customer, topology, schedule, and hardware-identification details out of reusable public skills.

## Common mistakes and red flags

- “All pressure gauges measure the full range equally well.”
- “A valve is a valve; gate, slit, throttle, and pneumatic valves have the same role.”
- “The power supply is on, so plasma and deposition are confirmed.”
- “Pump-down completed because the timeout elapsed.”
- “A training slide’s pressure or temperature is the production-safe limit.”
- “EFEM, Main Frame, and Chamber are merely UI pages.”
- “The process recipe can be reconstructed from general sputtering principles.”
- “A component’s communication protocol defines its domain identity.”

## Skill composition

- Use `equipment-control-architecture` when the decision concerns Sequence, material movement, resource arbitration, interlocks, distributed IPCs, simulation, recovery, or process execution ownership.
- Use `equipment-domain-modeling` when the decision concerns component state, commands, readback, capabilities, snapshots, engineering units, or metadata-driven UI.
- Use `software-quality-iso25010` when domain risks must become measurable quality scenarios or release gates.
- Use `document-governance` when producing controlled training, specification, terminology, or evidence documents.
- Use `code-review` for a concrete driver, polling, protocol, sequence, or interlock implementation defect.

## Required output

1. Domain question and evidence confidence
2. Equipment/material-flow context
3. Relevant component and physical-process semantics
4. Physical authority, readiness, and completion evidence
5. Software-contract implications
6. Product-specific unknowns and verification needs
7. Safety, confidentiality, and non-goal limits
