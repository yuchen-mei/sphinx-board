# Reset and Control

## ON, OFF, and STOP

An `ON` command performs the configuration and discharge checks, sets U503 through a controller pulse, and enables the supplies. If the board is already running, `ON` checks its state and returns without interrupting power or repeating the pulse. `OFF` disables both supplies and clears U503. STOP and the hardware protective clear path act independently of software. None of these actions changes the explicit Pico DUT reset request.

After STOP or a latched protective trip, the supplies remain inhibited until a new `ON` command from the user or experiment script completes the startup checks. A released STOP button or cleared OVP condition cannot set U503 again. A fault latched inside the TPS259470L eFuse can require cycling the 12 V input; the controller cannot clear that internal latch through U503.

Intrinsic eFuse UVLO/OVLO is distinct from a latched protective trip: the eFuse can inhibit and recover its output while its fault pin remains inactive. Input recovery can restore the supplies if the control supply and run latch remain valid. Loss of the control supply clears U503 and requires a new `ON`. U509 reports post-eFuse input undervoltage on `VIN12_VALID` for diagnostics and does not clear U503.

An explicit `SET` that changes feedback scale performs a controlled shutdown, reconfiguration, and restart without inserting a reset pulse. An existing protective trip blocks this operation and requires a new `ON`. Ordinary measurement warnings do not become protective trips. A same-scale `SET` does not cycle power. `STATUS`, `PING`, reconnecting the host, and recovery from a latched protective fault cannot set a cleared run latch.

Controller status reports `run_latch` and `hw_fault_n`; neither is a measurement of output voltage. While off, GP15 holds `HW_FAULT_N` low to keep the latch cleared. This low status is expected and does not by itself identify an external fault.

## Controller interface

The [Pico firmware](../../controller/README.md) is maintained alongside this schematic package. The default commissioning profile is unconfirmed; confirm the selected voltage range, assembly, calibration, and protective settings before enabling the DUT. A complete host application for kernel upload, JTAG result checking, and steady-power data acquisition is not included. The controller accepts one JSON request per USB serial line and uses the following interface.

| Pico GPIO | Signal | Function |
|---|---|---|
| GP2 | `CORE_REQ` | Core enable request; default low |
| GP3 | `IO_REQ` | I/O enable request; default low |
| GP4 | `RESET_ASSERT` | High explicitly asserts DUT reset; low or high impedance leaves the request inactive |
| GP5 | `RUN_LATCH` | U503 state readback |
| GP6 | `CORE_PG` | Core PG observation; diagnostic only |
| GP7 | `IO_VALID` | Measured I/O-voltage qualifier; diagnostic only |
| GP8 | `HW_FAULT_N` | Read shared fault bus; low inhibits operation |
| GP10, physical pin 14 | `RUN_SET` | Pulse once during startup or a controlled SET scale change; otherwise low |
| GP12 | `VIN12_VALID` | Post-eFuse input-voltage observation; diagnostic only |
| GP15 | `HW_FAULT_N` | Open-drain clear: drive low or release to high impedance |

Never drive GP15 push-pull high. `HW_FAULT_N` is shared with STOP and the hardware fault detectors. U507 conditions it into `HW_CLEAR_N` for U503's asynchronous clear. Its other channel conditions `RUN_SET` into `RUN_SET_CLEAN` for U503's clock. R507 holds `RUN_SET` low when the controller pin is high impedance.

Startup from the off state, including restart during an explicit `SET` across feedback scales, must:

1. Hold `CORE_REQ`, `IO_REQ`, and `RUN_SET` low. Leave the explicit reset request unchanged. Pull GP15 low to clear U503 and confirm `RUN_LATCH` is low.
2. Confirm both outputs have discharged below 50 mV. Configure the selected operating point and protection settings with the outputs disabled, then verify register readback.
3. Release GP15 to high impedance and verify `HW_FAULT_N` remains high for 10 ms. If a hardware fault remains, report it and keep the outputs disabled.
4. Generate one 1 ms-high `RUN_SET` pulse, then return it low. Verify both `RUN_LATCH` and `HW_FAULT_N` are high before issuing the Core/I/O enable sequence.
5. Monitor the supplies and protective faults during startup and operation. A failed commissioning, discharge, configuration-readback, or latch check inhibits startup. A protective trip disables the outputs and clears the latch. Do not repeat the set pulse or automatically retry; require a new `ON` after the cause is resolved. Ordinary PG, undervoltage, measurement-deviation, and communication warnings are recorded without shutdown or a reset request.

Initialize the supply requests, `RUN_SET`, and `RESET_ASSERT` low on controller boot and clear the latch before accepting a start request. Normal `OFF` follows the configured reverse power sequence, confirms discharge, and then clears the latch; protective trips disable both supplies immediately. GP15 holds the latch clear while off and is released only after the next startup completes configuration readback. No host heartbeat is required to keep the supplies on. USB inactivity is recorded as a warning.

## Warnings and protective trips

| Observation | Controller response |
|---|---|
| `CORE_PG`, `IO_VALID`, or `VIN12_VALID` low; ordinary undervoltage or voltage deviation | Record a warning; leave power and reset requests unchanged |
| PMBus warning/status information, USB inactivity, malformed command, or operating-time I2C/INA read failure | Record a diagnostic warning; leave power and reset requests unchanged |
| Core current above the routine 8 A experiment budget or the 10 A continuous board target | Warn; these values are not automatic trip thresholds |
| I/O current above the 1 A provisioned budget | Warn; no arbitrary 1.5 A shutdown threshold is imposed |
| Core current above 14 A continuously for 100 ms, regulator 15 A overcurrent fault, damaging overvoltage, or overtemperature | Protective shutdown; retain the trip until an explicit recovery request |
| STOP, asserted hardware fault bus, or lost run latch during operation | Disable supplies and require a new `ON` |

The controller's default board-temperature guard is 75°C. Regulator relative OVP is configured at 112.5% of the target; software fixture overvoltage checks and the independent approximately 1.319 V hardware OVP remain protective. These are commissioning settings and board-protection thresholds, not measured ASIC absolute-maximum ratings. A read failure prevents that sample from evaluating a software limit; independent hardware protection remains active. Warnings remain available in status along with raw PMBus status so experiment results can be interpreted afterward.

## DUT reset

J1.54 is a 1.8 V, active-high reset input. R602 is its 10 kΩ pull-up to VIO. Q601, an MMBT3904 with B/E/C on pins 1/2/3, releases reset by pulling the node low. R603 = 21.5 kΩ biases its base from VIO, and R604 = 100 kΩ connects the base to ground. With valid VIO and no reset request, Q601 conducts and reset is released without firmware execution.

SW601, U601, and Q602 each pull `RESET_BASE` low to assert reset. Q602 is a DMN62D2UQ-7: gate pin 1 connects to GP4 `RESET_ASSERT`, source pin 2 to ground, and drain pin 3 to `RESET_BASE`. R411 = 100 kΩ holds its gate low when the Pico output is high impedance. GP4 high asserts the Pico request; low or high impedance leaves it inactive. `RUN_LATCH`, PG, voltage qualifiers, and automatic power sequencing have no reset-control function. The high reset level depends on VIO being present; no valid logic level is promised during VIO collapse. There is no event latch, minimum pulse-width circuit, or clock synchronizer.

Manual, remote, or Pico reset can be repeated while the rails remain enabled. The explicit Pico commands are `{"cmd":"RESET","assert":true}` and `{"cmd":"RESET","assert":false}`. Only these commands change the Pico request after boot; `ON`, `OFF`, `SET`, warnings, and protective shutdown do not change it. `reset_asserted` in controller status describes the Pico request, not a measurement of the pin or the manual/remote inputs. Releasing one request cannot override another asserted request. Reset does not clear the run latch. STOP clears the latch and disables the rails.

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
2. Complete controller commissioning, enable control power, select the core operating point, and issue `ON`. The controller checks the configuration, sets the run latch, and enables Core and I/O. It does not reset the DUT.
3. Once supplies are valid, run the external clock and establish JTAG communication.
4. Explicitly assert reset with SW601, J602, or the Pico `RESET` command. Keep the clock running throughout the reset interval. Use a comfortably long pulse; minimum-cycle operation is not required.
5. Release reset asynchronously and begin testing. Repeat reset as required during the experiment.
6. For functionality, load and run one kernel, then read and compare its output. For power, run a large back-to-back loop, allow electrical and thermal readings to settle, and record averaged voltage, current, and power together with warning status and clock settings.
7. For shutdown, stop or tri-state external signal drivers before I/O power falls, issue `OFF`, and confirm discharge. An intentional reset before shutdown is optional and must be requested explicitly with power and clock valid; `OFF` never inserts it.

Remote reset does not replace the controller's power and fault handling.

## Measurement

Probe TP7 against TP607 to observe reset at J1.54. Use a high-impedance, low-capacitance probe with a short ground connection. Do not use a 50 Ω termination. Include probe capacitance when measuring the 10 kΩ pull-up edge.

Capture Core, I/O, `CORE_PG` or `IO_VALID`, and reset together during kernel transitions. Verify that ordinary power-qualification changes do not generate a reset pulse. Software polling is not a record of every short pin event. Record the regulator status registers separately from observed waveforms; steady-loop INA226 telemetry serves the averaged-power experiment, while the oscilloscope checks transient supply behavior.
