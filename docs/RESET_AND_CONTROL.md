# Reset and Control

## ON, OFF, and STOP

An `ON` command performs configuration and discharge checks, sets U503 through U903's `RUN_SET` pulse, and enables the supplies. If the board is already running at the requested configuration, `ON` checks its state and returns without interrupting power or repeating the pulse. `OFF` disables both supplies and clears U503. STOP and the hardware protective clear path act independently of software. None of these actions changes the explicit DUT reset request retained by U903.

After verified command completion, the power state must survive Pico inactivity, USB disconnection, reboot, or complete Pico power loss while 12 V remains continuously valid and no hardware fault or STOP occurs. The Pico performs no periodic task to sustain power. A complete board input loss and discharge instead defaults OFF on return and requires a new checked `ON`. See [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md) for the full contract.

After STOP or a latched protective trip, the supplies remain inhibited until a new `ON` command from the user or experiment script completes the startup checks. A released STOP button or cleared OVP condition cannot set U503 again. A fault latched inside the TPS259470L eFuse can require cycling the 12 V input; the controller cannot clear that internal latch through U503.

Intrinsic eFuse UVLO/OVLO is distinct from a latched protective trip: the eFuse can inhibit and recover its output while its fault pin remains inactive. Restoring the previous operating point requires both surviving control state and surviving regulator configuration. A partial brownout that resets PMBus registers while the latch remains set is not guaranteed to recover transparently. Loss of independent control power clears U503 and requires a new `ON`. U509 reports post-eFuse input undervoltage on `VIN12_VALID` for diagnostics and does not clear U503.

An explicit `SET` that changes feedback scale turns off the rail requests, verifies discharge, programs the new configuration, and restores the prior running requests only if the existing run latch survives throughout. It does not clear or repulse U503. STOP or a hardware fault during that interval clears the retained latch and blocks restart even if the fault later disappears; recovery requires a new `ON`. A SET while already OFF programs and reads back the new target while remaining OFF. Neither path inserts a reset pulse. Ordinary warnings do not become protective trips. A same-scale SET while ON does not cycle power. `STATUS`, `PING`, reconnecting the host, and fault recovery cannot set a cleared run latch.

Controller status reports `run_latch` and `hw_fault_n`; neither measures output voltage. A completed OFF returns U903 P04 `CLEAR_REQUEST` low after pulsing it high through Q901. A high clear request retained by an interrupted command continues to hold the fault bus low; that reading does not by itself identify an external fault.

## Controller interface

The [Pico firmware](../../controller/README.md) is maintained alongside this schematic package. Confirm the selected voltage range, assembly, calibration, and protective settings before enabling the DUT. A complete host application for kernel upload, JTAG result checking, and steady-power data acquisition is not included. The controller accepts one JSON request per USB serial line. Its only board-connected GPIO are GP0 SDA and GP1 SCL, through U902 ISO1640BDR; side 1 is board-powered and side 2 Pico-powered.

U903 TCA9535 at 7-bit address 0x20 supplies the retained control interface:

| U903 port | Signal | Function |
|---|---|---|
| P00 | `CORE_REQ` | Retained Core enable request |
| P01 | `IO_REQ` | Retained I/O enable request |
| P02 | `RESET_ASSERT` | Retained explicit reset request; high asserts, low releases |
| P03 | `RUN_SET` | One pulse during a checked startup; low after completion |
| P04 | `CLEAR_REQUEST` | High turns on Q901 to pull the fault bus low |
| P05 | `RUN_LATCH` | U503 state readback |
| P06 | `HW_FAULT_N` | Shared fault bus readback; low inhibits operation |
| P07 | `CORE_PG` | Core PG observation; diagnostic only |
| P10 | `IO_VALID` | Measured I/O-voltage qualifier; diagnostic only |
| P11 | `VIN12_VALID` | Post-eFuse input-voltage observation; diagnostic only |
| P12–P17 | `UNUSED_P12`–`UNUSED_P17` | Inputs, each pulled to ground through R1004–R1009 = 10 kΩ |

Q901 provides the clear pull-down; never drive `HW_FAULT_N` push-pull high. The bus is shared with STOP and the hardware fault detectors. U507 conditions it into `HW_CLEAR_N` for U503's asynchronous clear. Its other channel conditions `RUN_SET` into `RUN_SET_CLEAN` for U503's clock. R507 holds `RUN_SET` low before U903 is configured.

Pico boot and host reconnection first read existing state without rewriting outputs, direction registers, regulator settings, or reset requests. Cold U903 initialization is permitted only after confirming the board is OFF: write safe output values before output directions, because U903's power-on output register is 0xFF while its ports start as inputs. The exact register sequence is in [AUTONOMOUS_POWER.md](AUTONOMOUS_POWER.md).

An explicit `ON` startup from the OFF state must:

1. Hold U903 `CORE_REQ`, `IO_REQ`, and `RUN_SET` low. Preserve the explicit reset request. Pulse `CLEAR_REQUEST`, confirm `RUN_LATCH` is low, then release the clear request.
2. Confirm both outputs have discharged below 50 mV. Configure the selected operating point and protection settings with the outputs disabled, then verify register readback.
3. With `CLEAR_REQUEST` released, verify `HW_FAULT_N` remains high for 10 ms after hardware startup holdoff. If a hardware fault remains, report it and keep the outputs disabled.
4. Generate one 1 ms-high `RUN_SET` pulse, then return it low. Verify both `RUN_LATCH` and `HW_FAULT_N` are high before issuing the Core/I/O enable sequence.
5. Check final requests, latch state, and regulator readback before reporting success. A failed commissioning, discharge, configuration-readback, or latch check inhibits startup. Do not repeat the set pulse or automatically retry. Once established, independent hardware protects the rails without software monitoring; faults on the shared clear path disable both rails and require a new `ON` after the cause is resolved.

Normal `OFF` follows the configured reverse power sequence, attempts to confirm discharge, and clears the latch while preserving the explicit reset request. A successful OFF verifies that rail requests and the run latch are low; it does not prove zero measured voltage. Failed discharge or regulator/measurement access is reported in `off_verification` warnings. Check the measured rails for external back-power before handling the DUT. STOP and hardware clear act without waiting for this software sequence. A completed OFF stays OFF without Pico execution. If a command is interrupted before its writes and readbacks complete, its outcome is unknown: retained state may be intermediate. Reconnect with read-only observation, report the actual state, and require an explicit recovery command. Never replay a command or clear/reinitialize active outputs merely because the Pico rebooted.

## Warnings and protective trips

| Observation | Controller response |
|---|---|
| `CORE_PG`, `IO_VALID`, or `VIN12_VALID` low; ordinary undervoltage or voltage deviation | Report a warning when observed; leave power and reset requests unchanged |
| PMBus warning/status information, USB inactivity, malformed command, or measurement I2C/INA read failure | Report diagnostics when available; leave power and reset requests unchanged |
| Core current above the routine 8 A experiment budget or the 10 A continuous board target | Warn; these values are not automatic trip thresholds |
| I/O current above the 1 A provisioned budget | Warn; no arbitrary 1.5 A shutdown threshold is imposed |
| Programmed regulator OC/OV/OT condition | Regulator hardware performs its verified protective response without Pico service |
| STOP, board hardware OV/temperature trip, control brownout, or asserted eFuse fault | Hardware clears U503 and inhibits both rails; recovery requires a new `ON` |

U1001 independently trips at nominal 75°C with ±2°C sensor accuracy and nominal 5°C hysteresis. U1002 independently protects I/O at nominal 2.02446 V; its tolerance means this is not an exact 2.025 V ceiling. R1001 = 100 kΩ gives U502 a 180–420 ms startup holdoff, providing margin over the TMP302 datasheet §9 statement of functional readiness within 35 ms after VS reaches 1.4 V. Hot-start and supply-ramp qualification of the assembled circuit is still required. Regulator relative OVP is configured at 112.5% of target, with commissioned 15 A OC and internal OT protection; approximately 1.319 V Core hardware OVP remains separate. The former software 14 A/100 ms guard is not an autonomous hardware timing guarantee. These are fixture settings, not measured ASIC absolute-maximum ratings. On-demand warnings and raw PMBus status aid interpretation but are not a continuous event log.

## DUT reset

J1.54 is a 1.8 V, active-high reset input. R602 is its 10 kΩ pull-up to VIO. Q601, an MMBT3904 with B/E/C on pins 1/2/3, releases reset by pulling the node low. R603 = 21.5 kΩ biases its base from VIO, and R604 = 100 kΩ connects the base to ground. With valid VIO and no reset request, Q601 conducts and reset is released without firmware execution.

SW601, U601, and Q602 each pull `RESET_BASE` low to assert reset. Q602 is a DMN62D2UQ-7: gate pin 1 connects to U903 P02 `RESET_ASSERT`, source pin 2 to ground, and drain pin 3 to `RESET_BASE`. R411 = 100 kΩ holds its gate low when U903 is uninitialized or unpowered. U903 high asserts the explicit request; low releases it. Once set, the request survives Pico reboot or absence. `RUN_LATCH`, PG, voltage qualifiers, and automatic power sequencing have no reset-control function. The high reset level depends on VIO; no valid logic level is promised during its collapse. The control request is retained, but there is no automatic event capture, minimum pulse-width circuit, or clock synchronizer.

Manual, remote, or commanded reset can be repeated while the rails remain enabled. The explicit Pico commands are `{"cmd":"RESET","assert":true}` and `{"cmd":"RESET","assert":false}`. Only explicit RESET commands change the initialized retained request; `ON`, `OFF`, `SET`, Pico reconnection, warnings, and protective shutdown preserve it. `reset_asserted` in status describes the U903 request, not a measurement of the pin or manual/remote inputs. Releasing one request cannot override another asserted request. Reset does not clear the run latch. STOP clears the latch and disables the rails.

## Remote connector

J602 connects to the input LED of U601, `TLP293(GB-TPL,E`, through R605 = 750 Ω.

| Pin | Net | Connection |
|---|---|---|
| 1 | ZED_3V3 | ZedBoard Pmod 3.3 V, for example JA pin 6 |
| 2 | ZED_RESET_OD | ZedBoard GPIO configured for low or high impedance, for example JA pin 1 |

Pin 2 is a GPIO return for the optocoupler LED, not ground. Use two male-to-female leads and verify connector orientation against the ZedBoard revision. Do not supply this input from the Sphinx 3.3 V rail. Account for the 200 Ω series resistor on the applicable ZedBoard Pmod signal.

A low GPIO asserts reset. High impedance releases the remote request. Disable internal pull-down and keeper functions. The input circuit has no conductive connection to Sphinx power or ground; other interfaces, including JTAG, can connect the board grounds.

U601 output emitter pin 3 connects to Sphinx ground and collector pin 4 to `RESET_BASE`, in parallel with SW601 and Q602. Verify reset levels and optocoupler delay over the intended supply and temperature range.

## Procedure

1. Connect the supply, clock source, and 1.8 V JTAG interface with outputs inactive.
2. Apply 12 V and complete controller commissioning. The board starts OFF; attaching USB does not start or reset it. Select the Core operating point and issue one `ON`, then wait for verified completion. The command checks configuration, sets the run latch, and enables Core and I/O without resetting the DUT. The established supply state then persists without continued Pico execution.
3. Once supplies are valid, run the external clock and establish JTAG communication.
4. Explicitly assert reset with SW601, J602, or the Pico `RESET` command. Keep the clock running throughout the reset interval. Use a comfortably long pulse; minimum-cycle operation is not required.
5. Release reset asynchronously and begin testing. Repeat reset as required during the experiment.
6. For functionality, load and run one kernel, then read and compare its output. For power, run a large back-to-back loop, allow electrical and thermal readings to settle, and request averaged voltage, current, and power together with warning/status and clock settings. PMBus is at 0x10; Core/I/O INA226 at 0x40/0x41; retained controls at 0x20; NTC telemetry at 0x48. These measurements do not keep the rails alive. Reconnect a lost Pico or USB link with read-only state discovery before further commands.
7. For shutdown, stop or tri-state external signal drivers before I/O power falls, issue `OFF`, and confirm discharge. An intentional reset before shutdown is optional and must be requested explicitly with power and clock valid; `OFF` never inserts it.

Remote reset does not replace explicit power commands or independent hardware protection. If a command is interrupted, read back the state before deciding whether to continue or issue recovery.

## Measurement

Probe TP7 against TP607 to observe reset at J1.54. Use a high-impedance, low-capacitance probe with a short ground connection. Do not use a 50 Ω termination. Include probe capacitance when measuring the 10 kΩ pull-up edge.

Capture Core, I/O, `CORE_PG` or `IO_VALID`, and reset together during kernel transitions. Verify that ordinary power-qualification changes do not generate a reset pulse. Software polling is not a record of every short pin event. Record the regulator status registers separately from observed waveforms; steady-loop INA226 telemetry serves the averaged-power experiment, while the oscilloscope checks transient supply behavior.
