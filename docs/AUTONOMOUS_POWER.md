# Autonomous Power Contract

This specification defines the V2 change that makes an established power state independent of the Pico. It is a design and acceptance contract; the validation matrix below is not a record of completed hardware tests. The electrical and thermal qualification requirements in [REQUIREMENTS.md](REQUIREMENTS.md) still apply.

## Required behavior

After an explicit `ON` or `SET` command completes successfully, the board must retain its requested rail enables, programmed Core operating point, and explicit reset request while the 12 V input remains continuously valid and no hardware protection or STOP is asserted. Pico inactivity, USB disconnection, firmware termination, Pico reboot, or complete loss of Pico power must not change that state. Supply regulation and protection must not depend on a heartbeat, polling loop, periodic register write, or watchdog service performed by the Pico.

The supported input target is 11.5–13 V at the board terminals. Retention means preserving the established electrical control state; it does not promise constant ASIC power consumption or eliminate load-step voltage transients. The regulators must continue regulating when the kernel starts, finishes, or runs a back-to-back loop.

The Pico is a command and measurement interface. Between explicit commands it may sleep, stop executing, or be absent. Hardware protection continues without it. A `STATUS` or measurement command can collect a fresh snapshot, but issuing those commands is optional for continued operation. Measurements collected on demand cannot reconstruct an unobserved transient or an unlogged thermal history.

A complete loss of 12 V is different from loss of Pico power: after the board supply has discharged sufficiently to reset the control domain, the next power application must start **OFF**. No retained file, default firmware setting, USB attachment, or return of 12 V may issue a start pulse automatically. Starting again requires a new explicit `ON` and successful configuration checks. This is volatile state retention while powered, not restoration from nonvolatile memory.

STOP and a fault on the shared hardware clear path override every retained enable request. Clearing their cause must not set the run latch again. A cleared latch requires an explicit `ON`; an internal latched eFuse fault may additionally require cycling the input supply. `OFF` remains an explicit command. Manual and remote DUT reset remain available independently of the Pico.

## Power and communication domains

| Device | Selected part | Board function |
|---|---|---|
| U901 | TLV75533PDBVR | Generate independent `3V3_CTRL` from `AUX5V`; EN is tied to AUX5V |
| U902 | ISO1640BDR | Carry the bidirectional I2C bus between separately powered board and Pico domains |
| U903 | TCA9535PWR | Hold rail, reset, start, and clear requests; read board status |
| U904 | ADS1115IDGSR | Measure the board NTC and its excitation supply on demand |
| U1001 | TMP302BDRLR | Independent nominal 75°C board-temperature trip |
| U1002 | TLV3011AIDBVR | Independent nominal 2.02446 V I/O overvoltage trip |

U901, the run latch and its gating logic, the hardware fault detectors, U903, U904, board-side bus pullups, and the regulator/INA interfaces belong to the board domain. Pico pin 36 must not supply or be tied to `3V3_CTRL`. U901 uses IN/EN pins 1/3 at AUX5V, GND pin 2, OUT pin 5, and NC pin 4; C901/C902 must each retain at least 1 µF effective capacitance. The selected CL21B475KOFNNNE parts are 4.7 µF, ±10%, 16 V X7R, 0805; verify bias and temperature derating in procurement/layout review. [TI TLV755P datasheet](https://www.ti.com/lit/ds/symlink/tlv755p.pdf)

Samsung marks CL21B475KOFNNNE as NRND as of 2026-09-22; this also applies to C202 on U201 VDD5. Verify procurement before ordering or separately qualify a replacement with the required effective capacitance. Dated distributor stock is not a reservation. [Samsung product page](https://product.samsungsem.com/mlcc/CL21B475KOFNNN.do)

For U902, **side 1 is the board and side 2 is the Pico**: pins 1/2/3/4 are VCC1/SDA1/SCL1/GND1, and pins 8/7/6/5 are VCC2/SDA2/SCL2/GND2. Each side has local decoupling and pullups to its own supply. The isolation barrier prevents an unpowered Pico from clamping the board bus. Shared system ground through other connections does not invalidate this power-domain separation; the assembled board must not be advertised as a galvanically isolated system. Side 1 has an 80 pF load limit and an offset low-output level, so the complete board bus requires capacitance and logic-level verification. [TI ISO1640 datasheet](https://www.ti.com/lit/ds/symlink/iso1640.pdf)

The board bus uses 2.2 kΩ pullups. Keep U903 junction temperature ≤100°C throughout the qualified operating envelope: TCA9535 Rev. F permits 3.5 mA SDA sink current at that limit but only 1 mA above it, below the current demanded by these pullups. U1001's local 75°C trip does not establish U903 junction temperature. Place U903 away from power hot spots and verify its temperature and bus levels under worst qualified load and airflow. [TI TCA9535 datasheet, §5.3](https://www.ti.com/lit/ds/symlink/tca9535.pdf)

Remove direct Pico connections to retained requests, board status, and the board-powered thermistor node. A remaining direct connection could back-power the Pico or pull down a protection input when Pico power disappears. GPIO high-impedance behavior alone is not sufficient isolation.

## Retained command and status interface

U903 has all address straps grounded and uses 7-bit I2C address `0x20`. Port assignments are:

| Port | Direction after initialization | Signal / behavior |
|---|---|---|
| P00 | Output | `CORE_REQ` |
| P01 | Output | `IO_REQ` |
| P02 | Output | `RESET_ASSERT`; high asserts the explicit software reset request |
| P03 | Output | `RUN_SET`; pulse only during an explicitly authorized start |
| P04 | Output | `CLEAR_REQUEST`; high turns on Q901 to pull `HW_FAULT_N` low |
| P05 | Input | `RUN_LATCH` |
| P06 | Input | `HW_FAULT_N` |
| P07 | Input | `CORE_PG`, diagnostic |
| P10 | Input | `IO_VALID`, diagnostic |
| P11 | Input | `VIN12_VALID`, diagnostic |
| P12–P17 | Input | Unused inputs pulled to ground individually through R1004–R1009 = 10 kΩ; keep configured as inputs |

U903 outputs persist without I2C traffic while its supply remains valid. Hardware pull-downs establish inactive rail requests, inactive start/clear requests, and released software reset at a cold start, when its ports are inputs. On a confirmed cold initialization, write safe output values before changing port directions: output register `0x02 = 0x00`, then configuration registers `0x06 = 0xE0` and `0x07 = 0xFF`; retain zero polarity inversion. The power-on output-register value is `0xFF`, so reversing this order could briefly assert every request. [TI TCA9535 datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf)

A Pico boot or reconnection is **not** a cold initialization of U903. Attachment must first read the existing direction, output, input, and regulator state, without rewriting them. Do not create GPIO objects or drivers whose constructors reset board outputs. Unknown or inconsistent state must be reported as such; do not silently replace it with software defaults. Commands must modify only their owned output bits, preserving the explicit reset request and other retained bits.

`CLEAR_REQUEST` acts through Q901 as a pull-down; U903 must never drive the shared fault bus high. The common hardware fault line has asynchronous priority over U503. Both P03 and P04 must be low after a completed ON, OFF, or SET. OFF pulses P04 to clear the latch and then releases it. An interrupted command can leave P04 high, so a low fault-bus reading alone does not identify which external protection fired.

## Commands and completion

The transport accepts a request; a successful response is issued only after that request's required writes and readbacks complete. These are distinct events. Do not report success just because bytes were received or an I2C transaction was acknowledged.

For `ON` from OFF, the implementation must:

1. Preserve the explicit reset request. Hold rail requests and `RUN_SET` low, pulse `CLEAR_REQUEST`, verify the run latch is clear, and release the clear request.
2. Check commissioning, verify both outputs have discharged below 50 mV, program the selected Core voltage, feedback scale, compensation, and protection settings, and read them back.
3. With `CLEAR_REQUEST` released, verify the hardware fault line remains released for the startup qualification interval and generate a single `RUN_SET` pulse. Verify the latch and hardware fault line before enabling the requested rails in the configured sequence.
4. Verify the final requested outputs and regulator configuration, return `RUN_SET` low, and return the completed state. There must be no outstanding background action required to sustain it.

The nominal 0.75 V point uses feedback scale 0.5 as specified in [POWER_CONFIGURATION.md](POWER_CONFIGURATION.md). An `ON` directed at an already established matching state reads and checks that state without cycling the supplies or generating another pulse. A changed operating point must be an explicit `SET`.

A same-scale SET while ON changes the operating point without a rail power cycle. A scale-changing SET while ON turns off the rail requests, checks discharge, and reconfigures while preserving the existing run latch. It restores the prior requests only if that latch survives, and does not pulse RUN_SET. A SET while already OFF programs and verifies the target while remaining OFF. None of these paths changes the explicit reset request. SET must not recover a cleared latch or protective trip; recovery requires ON.

If Pico execution or communication is lost **during** `ON`, `OFF`, `SET`, or `RESET`, completion is unknown. A register write may already have taken effect; a multistep command is not atomic. The board may retain an intermediate rail request, clear request, reset request, or start level. No promise is made that it rolls back or completes on its own. On reconnection, read back actual state and require a deliberate recovery command; do not replay the interrupted command automatically. A start level left high must not generate repeated edges or an automatic restart when a fault clears.

If the command completed but its final USB response was lost, the same uncertainty applies to the host's knowledge, even though the board can be in its correctly retained final state. A read-only status query resolves the present state without disturbing it.

## Independent protection

| Mechanism | Required autonomous behavior | Interpretation |
|---|---|---|
| Hardware STOP | Clear U503 and inhibit both rails | Recovery requires new `ON` |
| Input eFuse | Retain its current, voltage, and thermal protections and fault connection | Intrinsic UVLO/OVLO and latched FLT events are different behaviors |
| U502 control supervisor | Clear the latch on control-power brownout and hold it clear during startup | Protects the retained control state |
| Existing Core absolute OVP | Retain the independent approximately 1.319 V hardware guard | Fixture guard with tolerance, not an ASIC maximum rating |
| TPS546B24A internal protection | Retain programmed relative OVP, excessive-current, and overtemperature protection | Operates without continued PMBus traffic; use verified response settings |
| TPS62131 internal protection | Retain its intrinsic current and thermal protection | Does not replace external I/O OVP |
| U1001 temperature switch | Pull the hardware fault bus low at nominal 75°C | Measures local board temperature, not die junction temperature |
| U1002 I/O OVP comparator | Pull the hardware fault bus low at nominal 2.02446 V | Independent of ADC readings and Pico execution |

U1001 uses pin 1 `TRIPSET0` high, pin 6 `TRIPSET1` low, pin 4 `HYSTSET` low, pin 5 at `3V3_CTRL`, pin 2 at ground, and open-drain pin 3 on `HW_FAULT_N`; C1001 is its local bypass capacitor. This selects a nominal 75°C trip with ±2°C sensor accuracy and nominal 5°C hysteresis. Cooling to approximately 70°C releases the detector; it must not restart power. Physical placement and the temperature gradient to the socket, regulator, and DUT remain qualification items. [TI TMP302 datasheet](https://www.ti.com/lit/gpn/TMP302)

U1002 uses `3V3_CTRL` on pin 6, ground on pin 2, REF pin 5 tied to IN+ pin 3, and the divided socket-side I/O rail on IN− pin 4; C1002 is its local bypass capacitor. OUT pin 1 joins `HW_FAULT_N`. Upper R1002/lower R1003 are 12.6 kΩ/20.0 kΩ, both 0.1%, giving `1.242 × (1 + 12.6/20) = 2.02446 V` nominal. The TLV3011A reference and 25°C offset limits yield an approximate initial screening range of 1.943–2.106 V before further temperature and dynamic effects. This is not a guaranteed 2.025 V ceiling. There is no feedback resistor from the shared fault bus to the divider. Use the specified A-version; changing comparator variants requires reviewing threshold and hysteresis. [TI TLV3011 datasheet](https://www.ti.com/lit/ds/symlink/tlv3011.pdf)

The historical software temperature threshold of 75°C and software I/O threshold of 2.025 V are replaced as protection mechanisms by these independent detectors. Software can report measurements and warnings, but samples must not be required to sustain or protect the rails. Likewise, an old sampled Core guard above 14 A for 100 ms or an absolute software Core guard at 1.26 V does not become an autonomous hardware guarantee merely because its constant remains in a profile. The regulator's commissioned 15 A OC setting, relative OVP at 112.5% of target, and independent fixture guards are separate mechanisms with their own accuracy, delay, and response. If the experiment requires a specific 14 A/100 ms envelope, it needs separately qualified hardware support.

The routine 8 A Core budget, 10 A continuous design target, 1 A I/O budget, ordinary PG loss, undervoltage, measurement deviation, PMBus warnings, and communication errors remain diagnostic. They must not cause software power cycling, a clear pulse, a reset request, or periodic intervention. Hardware and software thresholds are fixture commissioning choices; none establishes an ASIC absolute-maximum rating or a demonstrated 10 A board rating.

## Startup temperature and input disturbances

TMP302 §8.2.3 describes a typical 35 ms output-valid delay; §9 states functional readiness within 35 ms after VS reaches 1.4 V. U502's former CT-open delay could release in 12 ms. **R1001 = 100 kΩ connects U502 CT pin 4 to `3V3_CTRL`** to select a nominal 300 ms delay, specified 180–420 ms. Both VDD and SENSE monitor the independent control supply. The minimum supervisor delay exceeds the stated detector readiness interval by 145 ms for normal monotonic startup. Qualify the complete clear path during hot startup, including nonmonotonic supply ramps and temperature corners. An above-threshold board must remain inhibited even with a pending ON attempt; cooling alone must not set the latch. [TI TPS3808 datasheet](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [TI TMP302 datasheet](https://www.ti.com/lit/gpn/TMP302)

Input undervoltage indication is not a DUT reset request. An input disturbance can nevertheless interrupt energy delivery through the regulators' or eFuse's intrinsic limits. The following cases must be distinguished:

| Disturbance | Required interpretation |
|---|---|
| Pico/USB loss with valid 12 V and `3V3_CTRL` | Retain board state and output configuration; no rail or reset disturbance caused by the controller loss |
| Input dip while the control domain and regulator configuration remain valid | Physical regulation may be lost; intrinsic UVLO/OVLO recovery can restore output if no latched protective clear occurred |
| `3V3_CTRL` falls through the supervisor threshold | Clear the run latch; recovery of control voltage alone cannot start the rails |
| Regulator loses configuration while control/latch state survives | Original operating-point retention is not guaranteed; this partial-power case must be characterized and must not be claimed as transparent recovery |
| Complete input loss and discharge | All volatile board control state is reset; restored input defaults OFF and requires fresh configuration plus explicit `ON` |

The valid-input retention contract does not cover arbitrary input brownouts. Qualification must determine the duration/depth boundaries of partial-power cases, including whether Core PMBus settings can reset while AUX/control power remains alive. Where such a case cannot retain a safe known configuration, the implementation needs an appropriate hardware inhibit or an explicitly constrained operating envelope. The `VIN12_VALID` diagnostic alone is not that inhibit.

## Temperature and power measurements

U904 uses 7-bit address `0x48`. AIN0 reads `BOARD_NTC`, formed by R408 = 100 kΩ to `3V3_CTRL` and R409 = 100 kΩ NTC, B = 4250 K, to ground. AIN1 reads `3V3_CTRL` directly; AIN2 and AIN3 are grounded. Use a conversion range that covers 3.3 V, such as ±4.096 V, and a consistent range for the ratio. Compute `r = V(AIN0)/V(AIN1)` and, before calibration corrections, `R_NTC = 100 kΩ × r/(1-r)`. Reject invalid ratios and stale or failed conversions.

The ADS1115 input is not an ideal infinite-impedance voltmeter: at ±4.096 V its typical differential/common-mode input impedances are 15 MΩ/6 MΩ. The 100 kΩ thermistor network therefore needs loading, settling, resistor/NTC tolerance, and temperature calibration review. This channel is telemetry only; its failure or inaccuracy cannot disable U1001 protection. The thermistor's B25/50 approximation is not a substitute for its full resistance/temperature characteristic. [TI ADS1115 datasheet](https://www.ti.com/lit/ds/symlink/ads1115.pdf)

For functionality, run one kernel and compare the output. For power, execute a large back-to-back kernel loop, wait for the electrical and thermal conditions to settle, then request averaged INA226 rail voltage, current, and power. Record the operating point, clock, warning/status snapshot, and measurement conditions. No polling is needed to keep the loop powered; periodic host measurements are an optional data-acquisition choice. INA telemetry does not capture every load transient, and rail power includes downstream board losses rather than isolating die power.

## Acceptance matrix

Use a dummy load before DUT commissioning. Observe both socket rails, `3V3_CTRL`, the run latch, fault bus, and DUT reset as appropriate. A scope verifies transients and absence of unwanted edges; readback verifies configuration. Repeat relevant tests with the requested reset released and asserted, with both feedback scales, and at representative idle and high-load operating points. These are required tests, not claims that they have passed.

| Test | Stimulus | Pass condition |
|---|---|---|
| Cold default | Apply 12 V with Pico absent, blank, or booting | Both outputs remain inhibited; no start edge; explicit software reset request is inactive |
| One-command start | Complete commissioned `ON` and all readbacks | Requested rails/configuration established; `RUN_SET` low; no further software action required |
| No traffic | Stop commands and polling through the experiment interval | No control-state changes or controller-induced rail/reset interruption |
| USB disconnect | Unplug/reconnect USB after successful command | Established board state unchanged; reconnect does not rewrite it |
| Pico reboot | Reset Pico, restart firmware, or enter its bootloader | Board state and reset request retained; startup code is read-only toward active controls |
| Pico power loss | Remove only Pico power, leaving 12 V and load present; restore later | No board-bus clamp/back-power path that changes state; rails and explicit reset request retained |
| Diagnostic access | Issue `PING`, `STATUS`, and measurement commands | No start/clear edges, rail cycle, or reset-request change |
| Bus fault | Interrupt or hold the Pico-side bus during idle/reads | No software power intervention; STOP and independent protection still work |
| STOP | Assert and release STOP with Pico absent | Both rails inhibited; no automatic restart after release |
| Temperature trip | Heat U1001 through its threshold with Pico absent, then cool | Hardware clear observed; threshold/hysteresis recorded; cooling does not restart |
| Hot startup | Apply input above the thermal threshold, including a pending ON attempt | Supervisor holdoff and detector inhibit startup; no transient rail enable |
| I/O OVP | Inject a controlled I/O sense overvoltage with Pico absent | Hardware trip with measured threshold and latency; no restart after removing fault |
| Core/other protection | Exercise commissioned Core OV/OC/OT and eFuse fault cases | Their documented hardware responses occur without Pico execution; fault-bus trips remain latched OFF |
| Warning only | Exercise ordinary PG/UV/measurement warnings and communication loss | No commanded shutdown or DUT reset; intrinsic regulator operating limits still apply |
| Full input loss | Remove 12 V long enough to discharge board control/storage, then restore | No automatic start; next ON reprograms and verifies configuration |
| Partial brownout | Sweep input dip depth/duration, slow ramps, and rapid interruptions | Capture rail and control behavior; identify every retained/reset configuration case and prohibit unsupported recovery claims |
| Command interruption | Stop Pico at each write/readback/start/sequence boundary | No fabricated success; state reported unknown until readback; no automatic replay or repeated start pulses |
| Lost response | Drop USB after final board update but before host receives completion | Read-only reattachment identifies actual state without changing it |
| Explicit OFF/RESET | Complete OFF; separately assert/release RESET while ON | OFF remains OFF without Pico; RESET changes only the explicit request and does not alter rail enables |
| Kernel transitions | Run the one-shot functional kernel and sustained back-to-back loop | Record droop, overshoot, recovery, steady power, and thermal behavior; controller independence does not substitute for power-integrity qualification |

Record firmware revision, assembly, supply/temperature conditions, measured thresholds, scope captures, and readback results for each accepted operating envelope. Until these tests and the separate PCB/layout qualification are complete, this document defines intended behavior rather than verified hardware performance.
