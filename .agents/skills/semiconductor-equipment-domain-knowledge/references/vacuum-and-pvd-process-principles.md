# Vacuum and PVD Process Principles

## Vacuum principles relevant to software

PVD uses a controlled, clean, low-pressure environment to reduce contamination and establish repeatable gas/plasma behavior. Software should model pressure as a measured state with range, validity, timestamp, and readiness criteria rather than as a simple Boolean.

Gauge technologies cover different pressure regions. Rough/low-vacuum gauges, capacitance manometers used for process pressure, and high-vacuum ionization gauges do not have identical valid ranges or semantics. A “full-range” device may combine sensing technologies and still require explicit range/status handling. Atmosphere confirmation may use an independent switch or sensor according to equipment design.

Vacuum creation is staged. Roughing pumps commonly reduce pressure from atmosphere; turbo or cryogenic pumps commonly support higher-vacuum operation. Isolation valves, pump readiness, crossover conditions, cooling, regeneration, and fault recovery are machine-specific.

## Generalized magnetron sputtering chain

1. Establish a clean vacuum and verify chamber/utilities.
2. Introduce process gas and stabilize flow/pressure.
3. Apply power so a plasma can be generated and sustained.
4. Positive gas ions bombard the negatively biased target/cathode.
5. Target atoms are sputtered and travel toward the substrate.
6. Magnetic fields confine electron motion and influence plasma/deposition behavior.
7. Recipe-specific controls may include substrate bias, temperature, rotation, gas chemistry, and time.
8. Energy and gas are ramped down and the chamber transitions through approved post-process states.

## Variants and quality relationships

- Substrate bias changes ion bombardment and may influence stress or step coverage.
- Reactive sputtering combines target material with reactive gas and may show hysteresis.
- Target and gas purity relate to contamination risk.
- Pressure relates to collision behavior and mean free path.
- Magnetic-field distribution and rotation can influence erosion and uniformity.
- Cooling and temperature control affect stability and equipment protection.

These are qualitative domain principles, not production recipes. Exact setpoints, order, tolerances, endpoint rules, and safe limits must be verified against the current chamber, target, process, and controlled recipe.
