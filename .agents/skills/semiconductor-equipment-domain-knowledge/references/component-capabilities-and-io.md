# Component Capabilities and IO

Use component purpose and physical semantics before choosing class hierarchy or protocol abstraction.

| Family | Examples | Typical command | Typical readback/evidence | Important software concerns |
|---|---|---|---|---|
| Binary actuator | pneumatic/electric valve, slit valve | open/close or on/off | position switch/status | fail position, command versus actual, interlock |
| Discrete sensor | cover, position, ATM switch | usually none | boolean state/quality | debounce, polarity, stale/invalid state |
| Analog regulator | MFC, throttle valve, temperature controller | setpoint/mode/enable | accepted setpoint, process value, status | units, range, stabilization, loop ownership |
| Measurement | pressure gauge, thermocouple, MFM | read/configure | value, range, validity, alarm | sensor range, quality, calibration, stale data |
| Motion | robot, motor, lift, rotation | move/home/stop/speed | position, in-position, motion/fault | path safety, homing, timeout, late completion |
| Vacuum utility | dry, turbo, cryogenic pump | start/stop/regenerate | ready/speed/temperature/fault | staged readiness, isolation, cooldown/warmup |
| Thermal utility | heater, SCR/SSR, chiller | setpoint/power/mode | temperature, power, flow, fault | feedback mode versus open-loop power mode |
| Process energy | DC/RF/bias power | enable/set power/mode | forward/reflected/actual power, arc/fault | cooling, match, plasma evidence, ramp behavior |

## Capability cautions

- A component can combine several capabilities; do not force all devices into one inheritance chain.
- Input/output classification is insufficient for control semantics.
- Communication technology such as IO, fieldbus, RS-485, RS-232, or Ethernet is a transport choice, not the component’s domain identity.
- A command acknowledgement, controller setpoint, measured process value, and physical outcome are distinct facts.
- Exact ranges and status bits are vendor/model-specific and require current manuals and interface contracts.
