# PCB Layout Requirements

Use the current schematic sheets, local libraries, [netlist](../schematic/exports/sphinx_power_v2.net.xml), and BOM under `schematic/` as the electrical input. Sheet 09 adds autonomous control and sheet 10 adds independent protection. Obtain sheet/component/net counts from [generated design evidence](VALIDATION.md), not a duplicated fixed total. The current repository contains no V2 PCB.

## Power and return paths

Select stackup, copper thickness, and via construction from DC resistance, thermal, signal-integrity, and manufacturing requirements. The core continuous-current target is 10 A. Extract the hot PCB supply-and-return resistance from the load side of R201 to the socket; the layout objective is ≤1 mΩ, excluding the shunt, socket, and package.

Connect all 29 VDD and 25 VSS contacts with adequate copper and vias. Include I/O return current in the ground analysis. Inspect voltage and current density at each pin group rather than relying on one sense location.

Place NT601 and NT602 at adjacent socket-side power and ground groups. Route CORE_SENSE_P/N together without load current and away from switching nodes. Apply the TPS546B24A differential-sense routing and filtering guidance during layout review. The current schematic has no dedicated loop-injection resistor; define the measurement provision before routing is finalized.

Take shunt measurement traces independently from R201/R301 pads. Place INA226 input filters at the monitors. Reference the core monitor ground near the socket return. Take independent Core and I/O OVP sense from their socket planes; avoid a single narrow branch whose failure disconnects both regulation feedback and protection.

Keep U201 input switching loops, bootstrap connections, and local ceramic bypass compact. Connect DRTN only to C203 negative. Implement AGND, PGND, and exposed-pad connections according to the TI layout guidance. Keep ILM connected only to local R105, with parasitic capacitance below the device limit.

Route the positive and negative input paths for the same current. J101 has both pins on VIN_RAW; J102 has both pins on ground. Mark polarity clearly. Verify the AMASS 15.7 mm pin pitch, drill, pad, and body dimensions against the physical connector.

## Capacitors and measurement access

Place four groups of large core capacitors around the socket, each with three fitted polymer and three fitted large MLCC parts plus one optional position of each type. Keep all eight DNP capacitor positions electrically effective and accessible for assembly. Place 0402 decoupling near the relevant supply/return contacts. Check effective capacitance, mounting inductance, and PDN resonances.

Provide adjacent power/ground probe pads at the socket pin groups and regulator output. Provide space for a local pulsed load and loop measurement. J601 is for a high-impedance differential probe and is not a load connector. A dedicated high-current pulsed-load connector and synchronized trigger interface are not present in this schematic; resolve their physical implementation during layout review.

Place TP7 and TP607 near J1.54, on the same accessible face, with pad centers no more than 2 mm apart. Keep the reset stub and ground path short. Mark RESET and GND and preserve access with the socket closed. Both pads are 1 mm diameter.

Connect R603 to local VIO so Q601 releases reset whenever VIO is valid and no explicit request is asserted. Keep the three `RESET_BASE` pull-down paths from SW601, U601, and Q602 intact. Q602 gate is U903 P02 `RESET_ASSERT`, with R411 holding it low when U903 is uninitialized or unpowered; its initialized state persists through Pico loss. Route `CORE_PG`, `IO_VALID`, and `VIN12_VALID` to U903 diagnostic inputs without reset or run-latch clear connections. U509 retains its own R516 pull-up on `VIN12_VALID`. U501, U1001, and U1002 remain independent protective clear sources.

Implement the U301 enable interface placement requirements in [IO_ENABLE.md](IO_ENABLE.md). Keep comparator sense lines, NTC wiring, and clock routing clear of switching-node coupling.

## Independent control and protection

Power `3V3_CTRL` from U901 on AUX5V, not Pico pin 36. Place U901 input/output capacitors locally and verify effective capacitance and LDO dissipation. The Pico-side and board-side U902 supplies and bus pullups must remain distinct even though system grounds can be common. GP0/GP1 SDA/SCL are the only board-connected Pico GPIO. Do not reintroduce a direct control, status, or ADC wire that bypasses this separation.

U902 ISO1640BDR side 1 is the board, side 2 the Pico. Keep the board-side bus within its 80 pF load limit, including all device pins, traces, connectors, and probes. Check low-level compatibility with every device, aggregate pullup resistance, rise time, and the selected bus frequency. Place a bypass capacitor at each side's supply pins. Retention testing must include the Pico side unpowered and reconnecting.

Keep U903 away from power hot spots and establish its junction temperature ≤100°C at the qualified worst load and airflow. Above this temperature, the TCA9535 Rev. F SDA current allowance falls to 1 mA, insufficient for the present 2.2 kΩ pullups. Measure local temperature and bus levels; the temperature at U1001 is not a substitute.

Place U903 and its request pull-downs near control logic. Route P04 `CLEAR_REQUEST` to Q901's gate; Q901 alone pulls down the common fault bus. Keep the asynchronous clear path short and independent of the I2C bus. R1004–R1009 individually pull unused U903 P12–P17 inputs to ground through 10 kΩ. R1001 = 100 kΩ connects U502 CT to `3V3_CTRL`; keep its supervisor sense and supply connections on that independent rail.

Place U1001 TMP302BDRLR where local board temperature is intended to be protected, with C1001 close to supply/ground. Document the thermal relationship to the regulator, socket, and NTC; a 75°C sensor threshold is not a die-temperature limit. Review the TI DRL SOT-563 land pattern against the local footprint and assembly process.

Place U1002 and C1002 with short supply/ground and sense paths. R1002 = 12.6 kΩ and R1003 = 20 kΩ form the independent I/O OVP divider. Do not route its sense branch through the NTC/ADC circuitry or add positive feedback from the shared fault bus. Keep U904's AIN0 NTC and AIN1 excitation-supply routes quiet; their conversion accuracy affects telemetry, not temperature protection. See [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md) for pin-level requirements and tolerance limits.

## Socket and package

The schematic uses J1 = 3M 280-5205-01 for a 12 × 12 mm, 0.5 mm-pitch QFN80 package. The 80 functional positions comprise 29 VDD, 25 VSS, 10 VDDPST, seven signals, and nine NC positions. The center thermal probe has no electrical connection in this design.

Use the manufacturer drawing to check the approximately 30 × 30 mm body, 17 mm height, 3.2 mm actuation stroke, pin orientation, support regions, and mounting holes. Maintain clearance for socket actuation, device insertion, probing, airflow, and rework. Resolve footprint and keepout dimensions before fabrication.

Package and socket replacement remain design options. A replacement requires a corresponding pinout, footprint, mechanical envelope, power-path, and thermal review. Do not assign package resistance, bond-wire inductance, or encapsulant thermal conductivity without applicable data.

## Clock and JTAG

Route J5 to J1.48 as a single-ended 50 Ω clock trace with a ±10% manufacturing impedance target, continuous ground reference, and short branches. J1.47 clock_tap is a separate signal. R601 = 49.9 Ω is DNP by default.

The experimental clock source is an HP8133A with a square-wave setting of 1.8 Vpp and 0.9 V offset. Record the actual output configuration and measure receiver-side amplitude, duty cycle, and ringing. The instrument load setting is not established in the setup record; do not infer a doubled receiver voltage from the front-panel amplitude alone.

J2/J6 JTAG VTref is 1.8 V. VTref is a reference input to the adapter, not a source of board power. External clock and JTAG drivers must be inactive or high impedance before VIO falls.

## Layout deliverables

Supply the stackup, impedance specification, DC resistance extraction, capacitor placement review, thermal plan, socket fit check, probe/load access plan, and PCB-to-schematic connectivity check. Report actual extracted quantities and measurement conditions. Board and package contributions must remain distinguishable.
