# Reset and Control

## ON, OFF, and STOP

An `ON` command performs the configuration and discharge checks, sets U503 through a controller pulse, and enables the supplies. If the board is already running, `ON` checks its state and returns without interrupting power or repeating the pulse. `OFF` asserts reset, disables both supplies, and clears U503. STOP and hardware faults clear U503 independently of software.

After a fault, the supplies remain inhibited until a new `ON` command from the user or experiment script completes the startup checks. Restored input power, a released STOP button, or a cleared OVP condition does not restart them automatically. A fault latched inside the TPS259470L eFuse may require cycling the 12 V input; the controller cannot clear that internal latch through U503.

An explicit `SET` that changes feedback scale during healthy operation performs a controlled shutdown, reconfiguration, and restart. It first checks the current operating state; an existing fault stops the operation and requires a new `ON`. Fault recovery, `STATUS`, `PING`, and reconnecting the host never restart the supplies.

Controller status reports `run_latch` and `hw_fault_n`; neither is a measurement of output voltage. While off, GP15 holds `HW_FAULT_N` low to keep the latch cleared. This low status is expected and does not by itself identify an external fault.

## Controller interface

Firmware is maintained outside this schematic repository. The V2 controller uses the following interface.

| Pico GPIO | Signal | Function |
|---|---|---|
| GP2 | `CORE_REQ` | Core enable request; default low |
| GP3 | `IO_REQ` | I/O enable request; default low |
| GP4 | `RESET_RELEASE` | DUT reset-release request; default low |
| GP5 | `RUN_LATCH` | U503 state readback |
| GP8 | `HW_FAULT_N` | Read shared fault bus; low inhibits operation |
| GP10, physical pin 14 | `RUN_SET` | Pulse once during startup or a controlled SET scale change; otherwise low |
| GP15 | `HW_FAULT_N` | Open-drain clear: drive low or release to high impedance |

Never drive GP15 push-pull high. `HW_FAULT_N` is shared with STOP and the hardware fault detectors. U507 conditions it into `HW_CLEAR_N` for U503's asynchronous clear. Its other channel conditions `RUN_SET` into `RUN_SET_CLEAN` for U503's clock. R507 holds `RUN_SET` low when the controller pin is high impedance.

Startup from the off state, including restart during an explicit `SET` across feedback scales, must:

1. Hold `CORE_REQ`, `IO_REQ`, `RESET_RELEASE`, and `RUN_SET` low. Pull GP15 low to clear U503 and confirm `RUN_LATCH` is low.
2. Confirm both outputs have discharged below 50 mV. Configure the selected operating point and protection settings with the outputs disabled, then verify register readback.
3. Release GP15 to high impedance and verify `HW_FAULT_N` remains high for 10 ms. If a hardware fault remains, report it and keep the outputs disabled.
4. Generate one 1 ms-high `RUN_SET` pulse, then return it low. Verify both `RUN_LATCH` and `HW_FAULT_N` are high before issuing the Core/I/O enable sequence.
5. Monitor the supplies and faults during startup and operation. Any failed check must disable the outputs, assert reset, and clear the latch. Do not repeat the set pulse or automatically retry; require a new `ON` command after the cause is resolved.

Initialize these outputs to their inactive states on controller boot and clear the latch before accepting a start request. Normal `OFF` follows the configured reverse power sequence, confirms discharge, and then clears the latch; faults disable both supplies immediately. GP15 holds the latch clear while off and is released only after the next startup completes configuration readback. Host-timeout shutdown also clears the latch; keep the host heartbeat interval below five seconds. A DUT reset command leaves the supply requests and latch unchanged.

## DUT reset

J1.54 is a 1.8 V, active-high reset input. R602 is its 10 kΩ pull-up to VIO. Q601, an MMBT3904 with B/E/C on pins 1/2/3, releases reset by pulling the node low. R603 is 21.5 kΩ and R604 is 100 kΩ. The high level depends on VIO being present.

The hardware permits release only when `RUN_LATCH`, `RESET_RELEASE`, `CORE_PG`, and `IO_VALID` are all high and neither local nor remote reset is asserted. A low power qualifier asserts reset through this hardware path. There is no event latch, minimum pulse-width circuit, or clock synchronizer on this path.

Manual or remote reset can be repeated while the rails remain enabled. It does not clear the run latch. STOP clears the latch and disables the rails.

## Remote connector

J602 connects to the input LED of U601, `TLP293(GB-TPL,E`, through R605 = 750 Ω.

| Pin | Net | Connection |
|---|---|---|
| 1 | ZED_3V3 | ZedBoard Pmod 3.3 V, for example JA pin 6 |
| 2 | ZED_RESET_OD | ZedBoard GPIO configured for low or high impedance, for example JA pin 1 |

Pin 2 is a GPIO return for the optocoupler LED, not ground. Use two male-to-female leads and verify connector orientation against the ZedBoard revision. Do not supply this input from the Sphinx 3.3 V rail. Account for the 200 Ω series resistor on the applicable ZedBoard Pmod signal.

A low GPIO asserts reset. High impedance releases the remote request. Disable internal pull-down and keeper functions. The input circuit has no conductive connection to Sphinx power or ground; other interfaces, including JTAG, can connect the board grounds.

U601 output emitter pin 3 connects to Sphinx ground and collector pin 4 to `RESET_BASE`, in parallel with SW601. Verify reset levels and optocoupler delay over the intended supply and temperature range.

## Procedure

1. Connect the supply, clock source, and 1.8 V JTAG interface with outputs inactive.
2. Enable control power, select the core operating point, and issue `ON`. The controller checks the configuration, sets the run latch, and enables Core and I/O.
3. Once supplies are valid, run the external clock and establish JTAG communication.
4. Assert reset with SW601 or J602. Keep the clock running throughout the reset interval. Use a comfortably long pulse; minimum-cycle operation is not required.
5. Release reset asynchronously and begin testing. Repeat reset as required during the experiment.
6. For shutdown, assert reset while power and clock are valid, then stop or tri-state external signal drivers before I/O power falls. Issue `OFF` and confirm discharge.

Remote reset does not replace the controller's power and fault handling.

## Measurement

Probe TP7 against TP607 to observe reset at J1.54. Use a high-impedance, low-capacitance probe with a short ground connection. Do not use a 50 Ω termination. Include probe capacitance when measuring the 10 kΩ pull-up edge.

Capture Core, I/O, `CORE_PG` or `IO_VALID`, and reset together during kernel transitions. Software polling is not a record of every short reset event. Record the regulator status registers separately from the observed pin waveforms.
