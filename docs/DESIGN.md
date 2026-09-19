# Circuit Description

## Power paths

The core path is J101/J102, F101, U101, U201/L201, R201, and the socket supply plane. U201 is a TPS546B24ARVFR synchronous buck regulator. L201 is 0.56 µH and the configured switching frequency is 650 kHz. Differential feedback returns from the socket-side net ties NT601 and NT602, after the 1 mΩ core current shunt R201.

At 10 A, R201 has a nominal 10 mV drop and dissipates 0.10 W. Feedback includes this shunt and the PCB path to the sense endpoint. It excludes socket and package impedance. The WSL shunts are two-terminal devices; route independent sense traces from their pads.

U301 is the fixed-output TPS62131RGTR, supplying 1.8 V through L301 and the 10 mΩ I/O shunt R301. TPS62133 is a different output-voltage variant and is not a substitute. The enable circuit is specified in [IO_ENABLE.md](IO_ENABLE.md).

U102 supplies AUX5V through the 73.2 kΩ / 10 kΩ feedback network. D401 supplies Pico VSYS from AUX5V. Follow the schematic power connections when combining USB and board input power.

## Input protection and run latch

F101 is a 3.15 A backup fuse. U101 is a TPS259470L eFuse. Its 1.24 kΩ ILM resistor sets a nominal 2.69 A current limit. Input UVLO and OVLO are approximately 10.64 V and 14.4 V. These are nominal circuit thresholds; evaluate tolerances and fault transients during verification.

U509 senses VIN12 after the eFuse and clears the run latch through `HW_FAULT_N`. U503 is the hardware fault latch: pin 5 is Q (`RUN_LATCH`), and its unused Q-bar output is left unconnected. STOP, input loss, eFuse fault, control-supply brownout, and independent core overvoltage participate in the hardware clear path. U507 conditions the fault bus into `HW_CLEAR_N`, which asynchronously clears U503.

The controller sets U503 by pulsing GP10 (`RUN_SET`) through U507 during startup. R507 holds this input low while GP10 is high impedance. Hardware faults clear the latch even if the controller stalls or its enable requests remain high; fault recovery alone cannot set it again. An `ON` command from the off state verifies discharge and configuration, checks the fault bus, and generates a single set pulse. During healthy operation, an explicit `SET` across feedback scales uses the same checked startup after a controlled shutdown. Repeated `ON` while running only checks the operating state. `OFF` clears the latch through GP15 and holds it clear until the next startup. See [RESET_AND_CONTROL.md](RESET_AND_CONTROL.md) for the controller contract. The eFuse has its own fault behavior; an internally latched eFuse fault may still require cycling the 12 V input.

U504, a Diodes Incorporated 74LVC08AT14-13 in TSSOP-14, combines the three enable/reset AND functions in one quad gate package:

```text
CORE_EN      = RUN_LATCH AND CORE_REQ
IO_EN_CTRL   = RUN_LATCH AND IO_REQ
RESET_PERMIT = RUN_LATCH AND RESET_RELEASE
```

The unused fourth gate has both inputs grounded and its output unconnected. U506 combines `RESET_PERMIT`, `CORE_PG`, and `IO_VALID`.

| Detector | Sense network | Nominal threshold | Function |
|---|---|---:|---|
| U501 | 1.24 kΩ / 20 kΩ | 1.319 V | Independent core overvoltage, clears run latch |
| U509 | 73.2 kΩ / 10 kΩ | 10.333 V | Post-eFuse input undervoltage, clears run latch |
| U508 | 6.19 kΩ / 20 kΩ | 1.626 V | I/O voltage qualifier for reset |

The fixed core OVP is a board fault threshold. Configure the regulator's relative voltage and current protection for each experiment. An ASIC absolute-maximum rating is not defined by either protection mechanism.

Take the U501 sense connection independently from the socket core plane. A break in the narrow feedback branch must not also disconnect the OVP sense path. U508 directly measures I/O voltage; U301 PG alone does not establish that an operating I/O supply is present.

## Reset

R602 pulls J1.54 to I/O voltage through 10 kΩ. Q601 pulls the node low to release reset. The release condition is:

```text
RESET_RELEASE_OK = RUN_LATCH AND RESET_RELEASE AND CORE_PG AND IO_VALID
```

SW601 or U601 pulls Q601's base low and asserts DUT reset. A reset command leaves the run latch and power rails enabled. Loss of `CORE_PG` or `IO_VALID` inhibits reset release independently of software. These two qualifiers are combinational: recovery can release reset when the other conditions remain true. The circuit has no separate event latch or pulse stretcher for these qualifiers. The direct `RUN_LATCH` condition asserts reset when STOP or a latched fault disables the supplies, before output capacitors necessarily discharge.

TP7 measures the actual J1.54 reset node; TP607 supplies the adjacent probe ground. See [RESET_AND_CONTROL.md](RESET_AND_CONTROL.md).

## Decoupling and telemetry

The default core population is 12 × 330 µF polymer, 12 × 100 µF MLCC, 16 × 1 µF, and 16 × 100 nF. Total nominal capacitance is 5177.6 µF. The board reserves four additional polymer and four additional large-MLCC positions. Assembly options and controller settings are specified in [POWER_CONFIGURATION.md](POWER_CONFIGURATION.md).

R212 (47 Ω) and R304 (100 Ω) discharge Core and I/O. Confirm output voltage before a range change or hardware reconfiguration; disabling a regulator does not immediately discharge its output.

Two INA226 devices measure core and I/O voltage and current. With configuration `0x4297`, four averages of 332 µs bus and 332 µs shunt conversions give a nominal 2.656 ms update period. Use these readings for averaged telemetry. Use an oscilloscope for kernel transients and reset pulses.

The core shunt measures regulator current before local decoupling. Capacitor-supplied load current is not measured directly at that shunt. INA226 VBUS is referenced to its local ground; it is not a die-side differential voltage measurement. Input current requires an external instrument.
