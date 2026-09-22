# V2 Final Source Review — 2026-09-22

The reviewed source has no remaining identified schematic, pin-mapping, or companion-controller defect that prevents the specified autonomous operation. This is a source-review result, not fabrication release or proof of 10 A continuous operation. The repository contains no V2 PCB or assembled-board measurements.

The operating contract is unchanged: run one kernel for functional correctness; use a large back-to-back loop and settled voltage/current readings for power. After a completed power command, continuously valid input and healthy hardware retain the programmed supplies and explicit reset request without Pico execution. STOP and hardware protection remain independent. Interrupted commands require readback; complete board-power loss defaults OFF.

## Completed checks

| Scope | Result |
|---|---|
| Fresh KiCad 10.0.5 ERC | 0 violations across 11 sheets, with the configured ignored checks recorded in the report |
| Fresh schematic export versus committed export | All 247 component records, 146 nets, pin attributes and library-part definitions match; only export metadata differs |
| Control connectivity | 270 contract pins pass; 236 procurement references and 75 order lines checked |
| Independent device pin review | 158 existing active-device pin expectations and 86 new control/protection pin expectations pass |
| Actual loaded footprints | All 247 symbol-pin/pad sets match; all component-list values, ordering codes and footprints match the netlist |
| ASIC and Pico | All 80 ASIC positions match the supplied bonding reference; all 40 Pico positions match the separated power/interface domains |
| Power polarity and return | All 16 polymer capacitor polarities correct; U201 DRTN connects only to C203 negative |
| Socket keepout | Four corrected local-coordinate regions load, move and rotate with the footprint; copper-layer and footprint exclusions checked |
| Schematic visual review | All 11 exported pages rendered and inspected |
| Companion firmware | 51 host tests pass on CPython 3.13.5; syntax checks pass |
| Interrupted commands | 122 accepted-write interruption points tested across ON, OFF, SET and RESET; fresh controller attachment and STATUS do not rewrite retained control state |
| USB transport | Binary input and bounded single-byte output tested, including stalled/slow hosts, malformed input and raw Unicode serialization |

The [full pin/footprint evidence](evidence/full_pinout_review.json), [new hardware pin evidence](evidence/autonomous_pinout.json), [control checks](evidence/hardware_review.json), [ERC](evidence/erc.json), [intentional net changes](evidence/autonomy_netlist_diff.json), and [keepout checks](evidence/socket_keepout.json) record the checked source. [Documentation evidence](evidence/documentation_validation.json) records exact companion firmware hashes. [PROVENANCE.json](../PROVENANCE.json) binds these reports to the current design files.

## High-current and interface screening

These calculations use the present BOM and programmed 650 kHz switching frequency. They are design screens, not measurements.

| Check | Recomputed result |
|---|---|
| Input at 1.2 V × 10 A Core, 1.8 V × 1 A I/O, assumed 80% conversion efficiency, 0.6 W AUX and 11.5 V input | Approximately 1.552 A; excludes extra external loads and inrush |
| U101 current-limit screen, R105 = 1.24 kΩ ±1% | Approximately 2.689 A nominal; 2.396 A using −10% current-limit accuracy and +1% resistor tolerance |
| Minimum output pulse at 0.30 V, 13 V input | Approximately 35.50 ns, above U201's 20 ns maximum minimum-on-time parameter |
| L201 at 1.2 V/13 V and −20% inductance | Approximately 3.740 A peak-to-peak ripple, 11.870 A peak and 10.058 A RMS at 10 A average; below the listed inductor reference ratings |
| Core 1 mΩ / I/O 10 mΩ shunts at 10 A / 1 A | 10 mV drop each; 0.10 W / 0.01 W dissipation |
| Fitted Core capacitance | 5177.6 µF nominal; 6897.6 µF with all optional bulk positions fitted; effective capacitance and stability require qualification |
| ISO1640 low-level margins | Approximately 90 mV toward TPS546B24A and 80 mV in the reverse direction, before noise and ground offsets; require measurement |

Component limits were checked against [TI TPS25947](https://www.ti.com/lit/ds/symlink/tps25947.pdf), [TI TPS546B24A](https://www.ti.com/lit/ds/symlink/tps546b24a.pdf), [Coilcraft XAL1030](https://www.coilcraft.com/getmedia/7b108457-7731-456d-9256-ca72f2e1a551/xal1030.pdf), and [TI ISO1640](https://www.ti.com/lit/ds/symlink/iso1640.pdf). No electrical rating has been inferred for the socket from mechanical dimensions. Kelvin feedback compensates PCB delivery loss up to the sense endpoint; socket contacts, bond wires and the die power grid remain downstream.

## Corrections from the final review

The CL21B475KOFNNNE lifecycle field incorrectly said Active. The parts catalog and purchase-list notes now identify the manufacturer's NRND status for C202/C901/C902 and distinguish dated stock observations from procurement availability. The electrical selection remains 4.7 µF, ±10%, 16 V X7R, 0805; qualify any replacement and its effective capacitance before substitution. [Samsung product page](https://product.samsungsem.com/mlcc/CL21B475KOFNNN.do)

The TMP302 startup description now accounts for both the typical 35 ms application response and §9's statement of readiness within 35 ms after VS reaches 1.4 V. U502's 180 ms minimum holdoff provides margin during normal monotonic startup; assembled-circuit hot-start and disturbed-supply tests remain required. [TI TMP302](https://www.ti.com/lit/gpn/TMP302)

The control-bus temperature constraint is now explicit. TCA9535 Rev. F reduces its SDA sink-current allowance to 1 mA above 100°C junction temperature, which does not support the selected 2.2 kΩ pullups. The qualified operating envelope must keep U903 at or below 100°C junction temperature and verify receiver levels; U1001's local 75°C measurement does not prove U903 temperature. [TI TCA9535, §5.3](https://www.ti.com/lit/ds/symlink/tca9535.pdf)

## Required before hardware qualification

The 10 A requirement remains a board design target. Regulator rating and correct pin connections alone do not establish copper/via capacity, loop stability, socket current distribution, contact heating, or DUT transient voltage. Complete the layout extraction, mechanical/assembly checks and load measurements in [LAYOUT_HANDOFF.md](LAYOUT_HANDOFF.md) and [VALIDATION.md](VALIDATION.md).

Qualify both feedback scales, effective output capacitance, low-voltage minimum on-time, protection thresholds and latency, input-power margins, socket-side power distribution, sustained heating and kernel start/stop transients. The ASIC absolute-maximum limits and numerical allowable droop are not supplied. No socket current rating is inferred from its mechanical drawing.

The isolated board bus still requires the ≤80 pF load check and noise-margin measurements. Pico removal/reconnection, actual MicroPython/USB execution, partial input brownouts, hot startup and the independent protection paths require physical tests. Firmware profile confirmation remains a commissioning step; it must not be bypassed merely because host tests pass.

The companion firmware remains outside this schematic repository at `../controller`, as specified by [repository maintenance](../CONTRIBUTING.md). Its files and tests were reviewed together with this design, but they are not included in this repository's commit or push. The recorded hashes identify exactly which companion revision was tested. New-part inventory has not been rechecked comprehensively.
