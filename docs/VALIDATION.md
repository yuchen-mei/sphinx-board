# Verification Plan and Evidence

## Schematic evidence

The project contains nine schematic sheets. The [ERC report](evidence/erc.json) records the KiCad version, configured checks, and violations. The [control connectivity review](evidence/hardware_review.json) checks the current control, explicit-reset, and protective-shutdown connections. [PROVENANCE.json](../PROVENANCE.json) records design-file checksums and the scope of the repository checks. Use the regenerated netlist and evidence for component and net counts after design changes.

No V2 PCB measurements are included. Electrical-rule checking establishes schematic consistency within the configured rules; it does not establish loop stability, transient pin voltages, thermal performance, or ASIC operating limits.

## Board measurements

| Area | Measurement |
|---|---|
| Assembly and startup | Inspect polarity, socket orientation, solder joints, default output inhibition, AUX, and USB supply interaction with the ASIC absent. Verify the controller holds requests low and clears the run latch at boot. |
| ON/OFF and protective faults | Capture GP10 set pulse, RUN_LATCH, HW_FAULT_N, and rail enables. Exercise ON/OFF, STOP, control brownout, asserted eFuse fault, and independent core OVP. Confirm a cleared run latch is never set again without an explicit authorized startup and STOP cannot be overridden by a set pulse. Power commands and protective trips must leave the explicit Pico reset request unchanged. |
| Input interruption | With USB maintained, measure VIN12, VIN12_VALID, eFuse FLT, RUN_LATCH, and the output rails. Verify U509 only reports undervoltage. Distinguish intrinsic eFuse UVLO recovery with a retained latch from reverse-current/eFuse faults or control brownout that clear the latch. |
| Failed startup | Verify an unconfirmed commissioning profile, incomplete discharge, configuration mismatch, active protective fault, or failed latch readback leaves both supplies disabled. Confirm there is no automatic set-pulse retry and no inserted reset request. |
| Diagnostic warnings | Exercise PG loss, ordinary undervoltage/voltage deviation, PMBus warning status, USB inactivity, malformed commands, and operating-time telemetry read failures. Confirm warnings are retained without automatically changing power or reset requests. |
| Current and temperature policy | Confirm the routine Core/I/O budgets and 10 A continuous target produce warnings. Verify the commissioned severe-current, overvoltage, and overtemperature guards still stop the supplies and require explicit recovery. Use a suitable load with the ASIC absent for destructive-threshold testing. |
| I/O enable | Measure EN relative to local VIN during cold start, rapid input loss, and command transitions. Include SS/TR and the intended temperature range. |
| Regulation | Use a local load to measure 0.30, 0.50, 0.75, 1.00, and 1.20 V at light load and increasing current, including the 10 A continuous design target. Record operating temperature and protection settings. |
| Range changes | Verify explicit SET across feedback scales checks the running state, disables outputs, confirms discharge and configuration readback, and restarts with one set pulse. The explicit reset request stays unchanged throughout. An existing protective trip must block restart and require a new ON; ordinary warning status must not become an automatic trip. |
| Loop stability | Measure gain and phase for each fitted capacitor population and feedback scale. Use ≥45° phase margin and ≥10 dB gain margin as engineering review criteria. |
| Load transients | Apply measured current steps at the socket with 100 ns and 1 µs edge settings and 10, 20, 50, and 100 µs pulse widths. Record actual edge rate, droop, overshoot, recovery, and repetition rate. |
| Explicit reset | Test local, remote, and Pico reset; simultaneous requests; Pico absent/unprogrammed or GPIO high impedance; disconnected remote cable; and remote-source power loss. With valid VIO and no request, confirm J1.54 is low. Confirm each request independently asserts it and releasing one cannot override another. Keep the external clock running during intentional reset pulses. |
| Reset independence | With VIO held valid, vary CORE_PG, IO_VALID, VIN12_VALID, and RUN_LATCH and exercise ON/OFF/SET and warnings. Confirm none of these generates a reset request. Capture actual J1.54 during supply ramps as well; distinguish analog behavior during invalid VIO from deliberate logic-controlled reset. |
| Telemetry | Calibrate voltage, shunt readings, zero-current offset, and board-temperature readings. Record instrument settings and temperature. |
| Functionality | Establish power and clock, explicitly reset the DUT, load and execute one kernel, and compare its output. Capture supply behavior at kernel start and completion. Include nominal operation and selected low-voltage and boost points. |
| Steady power | Run the kernel in a large back-to-back loop, allow electrical and thermal readings to settle, and collect averaged Core/I/O voltage, current, and power. Record warning status and airflow; distinguish board/socket supply power from die power and account for downstream board loads. |
| Sustained operation | Run selected operating points for eight hours, logging resets, errors, supply extrema, current, temperature, and airflow. |

Choose pulsed-load amplitude and duty cycle within the configured input, current, and thermal limits. The 10 A continuous target is not an instantaneous current clamp or a required load at every voltage. Numerical droop acceptance limits are not assigned; use the measurements to assess board delivery and the observed ASIC operating region.

Measure rising and falling load edges. Trigger actual ASIC captures on the single functionality kernel's start and completion and on transitions into or out of the power loop. Supplemental qualification can vary idle intervals. Probe socket power and ground locally and document bandwidth and probe loading. INA226 telemetry is intended for steady averaged power; it does not establish the minimum transient voltage or capture every pin event.

## Test record

Each record should identify the board and DUT, hardware revision, fitted capacitor population, controller revision, register readback, clock settings, input wiring, load waveform, probe locations, instrument configuration, and temperature. Attach the waveforms supporting supply extrema and reset events. Keep board-side observations separate from inferred die behavior.
