# Circuit Description

## Power paths

The core path is J101/J102, F101, U101, U201/L201, R201, and the socket supply plane. U201 is a TPS546B24ARVFR synchronous buck regulator. L201 is 0.56 µH and the configured switching frequency is 650 kHz. Differential feedback returns from the socket-side net ties NT601 and NT602, after the 1 mΩ core current shunt R201.

At 10 A, R201 has a nominal 10 mV drop and dissipates 0.10 W. Feedback includes this shunt and the PCB path to the sense endpoint. It excludes socket and package impedance. The WSL shunts are two-terminal devices; route independent sense traces from their pads.

U301 is the fixed-output TPS62131RGTR, supplying 1.8 V through L301 and the 10 mΩ I/O shunt R301. TPS62133 is a different output-voltage variant and is not a substitute. The enable circuit is specified in [IO_ENABLE.md](IO_ENABLE.md).

U102 supplies AUX5V through the 73.2 kΩ / 10 kΩ feedback network. U901, TLV75533PDBVR, independently generates `3V3_CTRL` from AUX5V with its enable tied to AUX5V. D401 supplies Pico VSYS from AUX5V, but Pico pin 36 does not supply `3V3_CTRL`. Removing or rebooting the Pico therefore does not remove board control power. Follow the schematic power connections when combining USB and board input power.

Sheet 09 contains the autonomous control interface: U902 ISO1640BDR separates board-side I2C on side 1 from Pico-side I2C on side 2. Pico GP0/GP1 are its only GPIO connections, carrying SDA/SCL. Each bus side has its own supply and pullups. U903 TCA9535PWR retains output requests and reads digital status; U904 ADS1115IDGSR reads the NTC and its excitation supply. Sheet 10 contains independent temperature and I/O overvoltage protection. See [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md) for the complete pin map and power-domain contract.

## Input protection and run latch

F101 is a 3.15 A backup fuse. U101 is a TPS259470L eFuse. Its 1.24 kΩ ILM resistor sets a nominal 2.69 A current limit. Input UVLO and OVLO are approximately 10.64 V and 14.4 V. These are nominal circuit thresholds; evaluate tolerances and fault transients during verification.

U509 senses VIN12 after the eFuse and reports `VIN12_VALID` to U903 P11, with R516 providing its 10 kΩ pull-up. This observation does not clear the run latch. U503 is the hardware fault latch: pin 5 is Q (`RUN_LATCH`), and its unused Q-bar output is left unconnected. STOP, an asserted eFuse fault output, control-supply brownout, independent Core/I/O overvoltage, and independent board overtemperature participate in the hardware clear path. U507 conditions the fault bus into `HW_CLEAR_N`, which asynchronously clears U503.

The controller commands U903 P03 to pulse `RUN_SET` through U507 during an explicit ON startup. R507 holds this input low before U903 is initialized. A hardware clear acts even if the Pico is absent or retained enable requests remain high; recovery alone cannot set the cleared latch again. `ON` verifies discharge and configuration, checks the fault bus, and generates one set pulse. A scale-changing SET while ON disables rail requests, checks discharge, and reconfigures while preserving the existing run latch; it restores requests only if that latch remains set and never generates another set pulse. Repeated ON at the matching established state checks it without cycling power. OFF pulses U903 P04 `CLEAR_REQUEST` high through Q901 to clear the latch, then returns P04 low. These actions preserve U903 P02's explicit DUT reset request.

The eFuse has its own operating and fault behavior. UVLO and OVLO inhibit its output without necessarily asserting its fault output. Recovery with the original operating point requires both retained control state and retained regulator configuration; a dip that resets PMBus settings while AUX/control power survives is a separate qualification case. USB does not sustain the independent control domain. Control brownout or an asserted eFuse fault clears the latch; a complete input loss and discharge defaults OFF on return. An internally latched eFuse fault can also require cycling 12 V. See [RESET_AND_CONTROL.md](RESET_AND_CONTROL.md).

U502 supervises `3V3_CTRL`. R1001 = 100 kΩ connects its CT pin to `3V3_CTRL`, selecting a nominal 300 ms startup holdoff, specified 180–420 ms. The TMP302 datasheet describes 35 ms as typical in §8.2.3 and states in §9 that U1001 becomes fully functional within 35 ms after its supply reaches 1.4 V. The 180 ms minimum holdoff provides startup margin for a normal monotonic supply ramp. Qualify the assembled clear path during hot startup and nonmonotonic supply ramps; see [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md).

U504, a Diodes Incorporated 74LVC08AT14-13 in TSSOP-14, implements the two supply-enable AND functions:

```text
CORE_EN      = RUN_LATCH AND CORE_REQ
IO_EN_CTRL   = RUN_LATCH AND IO_REQ
```

The unused third and fourth gates have their inputs grounded and outputs unconnected. U506 and C507 are absent; no logic gate combines power-good or run-latch signals with DUT reset. U507 remains part of the power-latch circuit.

| Detector | Sense network | Nominal threshold | Function |
|---|---|---:|---|
| U501 | 1.24 kΩ / 20 kΩ | 1.319 V | Independent core overvoltage, clears run latch |
| U509 | 73.2 kΩ / 10 kΩ | 10.333 V | Post-eFuse input-voltage observation on `VIN12_VALID`; warning only |
| U508 | 6.19 kΩ / 20 kΩ | 1.626 V | I/O voltage observation on `IO_VALID`; warning only |
| U1001 | TMP302B straps: TRIPSET0 high, TRIPSET1 low, HYSTSET low | 75°C, nominal 5°C hysteresis | Independent local board-temperature protection; clears run latch |
| U1002 | R1002 = 12.6 kΩ / R1003 = 20 kΩ, both 0.1% | 2.02446 V | Independent socket-side I/O overvoltage; clears run latch |

The fixed Core OVP is a board fault threshold. The controller programs regulator overvoltage, overtemperature, and excessive-current protection once and verifies readback; protection then operates without Pico service. C1001/C1002 locally bypass U1001/U1002. TMP302B accuracy is ±2°C before placement error. The I/O comparator threshold has an approximate 1.943–2.106 V initial static screening range, not a guaranteed 2.025 V ceiling. Ordinary PG loss, undervoltage, voltage deviation, PMBus warnings, and communication loss are diagnostic observations; they do not request shutdown or reset. The 10 A continuous target and routine current budgets are qualification limits and warnings, not instantaneous current clamps. No protection threshold establishes an ASIC absolute-maximum rating.

Take the U501 sense connection independently from the socket core plane. A break in the narrow feedback branch must not also disconnect the OVP sense path. U508 directly measures I/O voltage; U301 PG alone does not establish that an operating I/O supply is present.

## Reset

R602 pulls J1.54 to I/O voltage through 10 kΩ. R603 biases Q601's base from VIO through 21.5 kΩ; R604 provides the 100 kΩ base pull-down. With valid VIO, Q601 normally conducts and pulls J1.54 low to release reset. SW601, optocoupler U601, and U903-controlled Q602 independently pull `RESET_BASE` low to turn Q601 off and assert active-high reset:

```text
RESET_ASSERTED = LOCAL_RESET OR REMOTE_RESET OR RETAINED_RESET_ASSERT
```

This expression applies while VIO provides valid logic levels. U903 P02 is `RESET_ASSERT`: high requests reset, and low releases that request. R411 keeps the request inactive when U903 is in its cold-start input state. Once programmed, this request survives Pico loss or reboot. An explicit reset command leaves the power requests and latch unchanged; power commands and protective shutdown leave the retained reset request unchanged. Reset is not automatically driven by invalid power. Its high level is unavailable when VIO is absent. There is no pulse stretcher or clock synchronizer; the operator supplies an adequate explicit pulse with the external clock running.

TP7 measures the actual J1.54 reset node; TP607 supplies the adjacent probe ground. See [RESET_AND_CONTROL.md](RESET_AND_CONTROL.md).

## Decoupling and telemetry

The default core population is 12 × 330 µF polymer, 12 × 100 µF MLCC, 16 × 1 µF, and 16 × 100 nF. Total nominal capacitance is 5177.6 µF. The board reserves four additional polymer and four additional large-MLCC positions. Assembly options and controller settings are specified in [POWER_CONFIGURATION.md](POWER_CONFIGURATION.md).

R212 (47 Ω) and R304 (100 Ω) discharge Core and I/O. Confirm output voltage before a range change or hardware reconfiguration; disabling a regulator does not immediately discharge its output.

Two INA226 devices at 7-bit addresses 0x40 (Core) and 0x41 (I/O) measure rail voltage and current. With configuration `0x4297`, four averages of 332 µs bus and 332 µs shunt conversions give a nominal 2.656 ms update period. U201 PMBus is at 0x10, U903 at 0x20, and U904 at 0x48. U904 AIN0/AIN1 measure `BOARD_NTC`/`3V3_CTRL` for a calibrated ratiometric temperature reading. Reading telemetry is optional for power retention. Use an oscilloscope for kernel transients and reset pulses.

The core shunt measures regulator current before local decoupling. Capacitor-supplied load current is not measured directly at that shunt. During a sustained back-to-back kernel loop, average capacitor charging current approaches zero, so averaged shunt current is useful for steady rail-power measurement. INA226 VBUS is referenced to its local ground; it is not a die-side differential voltage measurement. The reported rail power includes downstream board loads and socket/package losses. R212 consumes about 12 mW at 0.75 V and R304 consumes 32.4 mW at 1.8 V; account for these loads when estimating DUT supply power. Input current requires an external instrument.
