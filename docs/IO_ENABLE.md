# I/O Regulator Enable Interface

U301 EN is supplied from local VIN12 through a resistive divider. USB-powered logic controls MOSFET gates and does not directly drive EN. This separates the EN high-level source from the USB control supply.

## Connections

| Component | Value / type | Connection |
|---|---|---|
| R305 | 2.2 kΩ, 1%, 0.25 W, 1206 | VIN12 to IO_EN |
| R303 | 270 Ω, 1%, 0603 | IO_EN to ground |
| Q301 | DMN62D2UQ-7 | Gate IO_EN_CTRL; source ground; drain IO_EN_PULLDOWN |
| Q302 | DMN62D2UQ-7 | Gate IO_EN_INHIBIT; source ground; drain IO_EN |
| R306 | 10 kΩ | VIN12 to IO_EN_INHIBIT |
| R307 | 270 Ω | IO_EN_CTRL to ground |
| R308 | 100 Ω, 0.5 W, 0805 | IO_EN_INHIBIT to IO_EN_PULLDOWN |
| C306 | 1 nF, 50 V, C0G, ±5% | VIN12 to IO_EN_INHIBIT |
| C307 | 100 pF, 100 V, C0G, ±5% | IO_EN to ground |

Q301 and Q302 use gate/source/drain pins 1/2/3. U504 pin 6 drives `IO_EN_CTRL`, the AND of `RUN_LATCH` and `IO_REQ`.

With the command low or control power absent, R306 biases Q302 on and inhibits U301. A high command turns Q301 on, discharges the Q302 gate through R308, and permits the VIN12 divider to enable U301. The unloaded nominal divider voltage is 1.31 V at 12 V input.

C306 couples VIN12 startup edges into the inhibit gate. R308 controls gate discharge, R307 holds the logic-side gate low, and C307 controls EN-node transients. Fit all three resistors and both capacitors with the specified values. Changes require a new transient evaluation.

## Ratings and layout

The TPS6213x EN absolute-maximum range is −0.3 V to VIN + 0.3 V. Its specified enable and disable levels are 0.9 V and 0.3 V. The circuit must satisfy these limits at the U301 pins during startup, operation, and input loss. See the [TI datasheet](https://www.ti.com/lit/ds/symlink/tps62130.pdf).

At 14.4 V with EN low, R305 dissipates approximately 95 mW including its −1% resistance tolerance. Use the specified 0.25 W, 1206 part. R307 dissipates approximately 49 mW at 3.6 V and −1% resistance tolerance. Check local resistor temperatures and manufacturer derating.

Place the interface close to U301. Use local VIN12 and ground connections, short gate/drain traces, and low-inductance access to VIN, EN, and SS/TR. C307's exact part number is listed as NRND in the dated catalog; qualify any substitute for capacitance, dielectric, tolerance, and package.

## Verification

Measure VIN, EN, IO_EN_CTRL, and IO_EN_INHIBIT during cold startup, command transitions, and rapid input interruption with USB power maintained. Include the fastest measured supply edges and the intended temperature range. Verify `EN − VIN ≤ 0.3 V`, `EN ≥ −0.3 V`, and the enable/disable thresholds.

Also measure SS/TR during rapid VIN collapse; its pin rating depends on VIN. A static divider calculation does not establish transient pin compliance. Use measured parasitics and probe loading when interpreting the waveforms.
