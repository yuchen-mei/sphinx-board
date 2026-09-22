# Power Configuration

## Controller interface

The TPS546B24A uses the 7-bit PMBus address **0x10**. R209 is 4.64 kΩ from ADRSEL to ground with no upper resistor; SYNC uses automatic detection. All addresses below are 7-bit values, not shifted address bytes.

| Device | Address | Purpose |
|---|---|---|
| U201 TPS546B24A | 0x10 | Core configuration and regulator status |
| U903 TCA9535 | 0x20 | Retained control requests and digital status |
| U302 INA226 | 0x40 | Core rail measurements |
| U303 INA226 | 0x41 | I/O rail measurements |
| U904 ADS1115 | 0x48 | NTC and its excitation supply measurements |

Pico GP0/GP1 carry SDA/SCL through U902 ISO1640BDR. Side 1 and its pullups use independent `3V3_CTRL`; side 2 uses Pico power. The listed devices are on the board side and remain powered independently of the Pico while the board input is valid. U903, the run latch, and regulator registers hold the established configuration without periodic Pico work. A Pico reboot must first read these states, not reset them. Complete input loss and board discharge require fresh configuration before a new explicit `ON`.

Program and read back the regulator configuration while the output is disabled. Match compensation to the fitted capacitor population and feedback scale. Set the switching frequency to 650 kHz and soft-start time to 5 ms. The hardware MSEL straps provide startup settings and do not replace runtime configuration.

The controller uses feedback scales 1 and 0.5 to cover the 0.30–1.20 V fixture range. The TI register and operating-range descriptions differ at the 0.70–0.75 V scale-1 endpoint; use scale 0.5 for the nominal 0.75 V point and verify the selected scale and voltage before loading the ASIC. Change scale with both outputs disabled and confirm discharge below 50 mV before reconfiguration. A scale change does not assert reset automatically. The experiment operator decides whether to request reset before or after the power interruption; a meaningful reset pulse requires VIO and a running clock.

The [companion Pico firmware](../../controller/README.md) performs configuration readback, discharge checks, and explicit control through the [ON/OFF and fault-latch interface](RESET_AND_CONTROL.md). Confirm its commissioning profile before enabling the DUT. ON startup verifies configuration and pulses U903 P03 `RUN_SET` before enabling outputs. A scale-changing SET while ON disables rail requests, checks discharge, and reconfigures without clearing or pulsing the run latch; only a surviving latch permits restoration of the previous running requests. A SET while OFF programs and verifies the target without starting the rails. Power commands preserve U903 P02's reset request. Once a command completes, power and protection operate without continued firmware execution. Interrupted commands have unknown outcomes; read back state before recovery, as specified in [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md).

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

Configure current limits and voltage protection explicitly. Write and read back `PGOOD_CONFIG` (E3h) = `0x009F`, retaining the documented manufacturer default, and `MISC_OPTIONS` (EDh) = `0x0000`, retaining PGD as a power-good output. The TI PGOOD register figure and field table differ in their read/write annotations; this design does not depend on changing the disputed PG mask bits. PG remains diagnostic and never controls DUT reset. Read the detailed PMBus status registers separately from PG. Disable automatic undervoltage fault shutdown used solely as an experiment pass/fail criterion while retaining damaging overvoltage, excessive-current, and overtemperature protection. Record warning and fault status so failed characterization points remain distinguishable from protective trips.

Measurements requested by the host can warn above the routine 8 A Core budget, the 10 A continuous board target, and the 1 A I/O budget. No sampled software limit is required for protection or power retention. Configure and read back the regulator's commissioned 15 A overcurrent fault, relative OVP at 112.5% of target, and overtemperature response. Retain the independent approximately 1.319 V Core hardware OVP, U1001 nominal 75°C temperature switch, and U1002 nominal 2.02446 V I/O OVP. Their tolerance and response requirements are detailed in [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md); none is an exact ASIC damage limit. The former sampled 14 A/100 ms software guard is not a hardware timing guarantee. Review all settings for the actual DUT and qualify protection responses and loop stability on the assembled fixture. These settings do not certify 10 A continuous board operation.
