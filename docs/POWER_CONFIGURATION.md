# Power Configuration

## Controller interface

The TPS546B24A uses the 7-bit PMBus address **0x10**. R209 is 4.64 kΩ from ADRSEL to ground with no upper resistor; SYNC uses automatic detection. The address is a 7-bit value, not a shifted address byte.

Program and read back the regulator configuration while the output is disabled. Match compensation to the fitted capacitor population and feedback scale. Set the switching frequency to 650 kHz and soft-start time to 5 ms. The hardware MSEL straps provide startup settings and do not replace runtime configuration.

The controller uses feedback scales 1 and 0.5 to cover the 0.30–1.20 V fixture range. Confirm the permitted scale-1 endpoint against the exact TI device documentation: the available register and operating-range descriptions differ at 0.70–0.75 V. Verify operation at the selected scale and voltage before loading the ASIC. Change scale with reset asserted and both outputs disabled; confirm discharge below 50 mV before reconfiguration.

Firmware is maintained outside this repository. The controller provides configuration readback, hardware-fault handling, output discharge checks, and reset control through the [ON/OFF and fault-latch interface](RESET_AND_CONTROL.md). Startup verifies the configuration and sets the latch through GP10 before enabling outputs. An explicit `SET` that changes feedback scale during healthy operation performs a controlled shutdown, reconfiguration, and restart using the same checks.

## Capacitor population

| Population | 330 µF polymer | 100 µF MLCC | 1 µF | 100 nF | Nominal total |
|---|---:|---:|---:|---:|---:|
| Default | 12 | 12 | 16 | 16 | 5177.6 µF |
| Full | 16 | 16 | 16 | 16 | 6897.6 µF |

Default DNP positions are C704, C708, C764, C768, C714, C718, C774, and C778. R601, the clock termination resistor, is also DNP. Preserve all capacitor footprints and their short power/ground connections in layout.

Distribute the large capacitors in four socket-local groups. Each group fits three polymer and three large MLCC parts by default, with one additional position of each type. Place the 0402 parts at the corresponding power and return pins. Polymer capacitor polarity is positive stripe to Core.

Nominal capacitance is an assembly quantity. Use effective capacitance, ESR, and mounting parasitics for layout analysis and board verification.

## Compensation configuration

The configuration values below are controller programming inputs. Loop stability and transient response require measurements on the assembled board.

Common current-loop settings: GMI = 100 µS, RVI = 20 kΩ, CZI = 799.2 pF, CPI = 12.8 pF.

| Population | SCALE_LOOP | GMV | RVV | CZV | CPV | B1 value |
|---|---:|---:|---:|---:|---:|---|
| 12 + 12 | 1 | 25 µS | 120 kΩ | 750 pF | 6.25 pF | `0xC913826102` |
| 12 + 12 | 0.5 | 50 µS | 120 kΩ | 750 pF | 6.25 pF | `0xC913C26012` |
| 16 + 16 | 1 | 50 µS | 80 kΩ | 1000 pF | 6.25 pF | `0xC913024112` |
| 16 + 16 | 0.5 | 100 µS | 80 kΩ | 1000 pF | 6.25 pF | `0xC913824022` |

B1 is a five-byte SMBus block, least-significant byte first. For the default population at scale 0.5, the block count and payload are `05 12 60 C2 13 C9`. A readback mismatch must inhibit output enable.

Configure current limits, voltage protection, and `POWER_GOOD_CONFIG` explicitly and record the readback. PG timing must be evaluated from the actual register settings and measurements. A voltage-warning threshold alone does not specify the delay or pulse width of a reset event.
