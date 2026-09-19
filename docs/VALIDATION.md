# Verification Plan and Evidence

## Schematic evidence

The project contains nine sheets, 219 netlisted components, and 119 nets. The [ERC report](evidence/erc.json) records the KiCad version, configured checks, and violations. The [control connectivity review](evidence/hardware_review.json) checks the control and fault-shutdown connections. [PROVENANCE.json](../PROVENANCE.json) records design-file checksums and the scope of the repository checks.

No V2 PCB measurements are included. Electrical-rule checking establishes schematic consistency within the configured rules; it does not establish loop stability, transient pin voltages, thermal performance, or ASIC operating limits.

## Board measurements

| Area | Measurement |
|---|---|
| Assembly and startup | Inspect polarity, socket orientation, solder joints, default output inhibition, AUX, and USB supply interaction with the ASIC absent. Verify the controller holds requests low and clears the run latch at boot. |
| ON/OFF and faults | Capture GP10 set pulse, RUN_LATCH, HW_FAULT_N, and rail enables. Exercise ON/OFF, STOP, control brownout, input interruption with USB maintained, eFuse fault, and independent core OVP. Confirm fault recovery never restarts the rails without a new ON command and STOP cannot be overridden by a set pulse. |
| Failed startup | Verify incomplete discharge, configuration mismatch, active fault, and failed latch readback leave both supplies disabled with reset asserted. Confirm there is no automatic set-pulse retry. Verify host-timeout shutdown clears the latch. |
| I/O enable | Measure EN relative to local VIN during cold start, rapid input loss, and command transitions. Include SS/TR and the intended temperature range. |
| Regulation | Use a local load to measure 0.30, 0.50, 0.75, 1.00, and 1.20 V at light load and increasing current, including the 10 A continuous design target. Record operating temperature and protection settings. |
| Range changes | Verify explicit SET across feedback scales checks the running state, asserts reset, disables outputs, confirms discharge and configuration readback, and restarts with one set pulse. An existing fault must stop the sequence and require a new ON command. |
| Loop stability | Measure gain and phase for each fitted capacitor population and feedback scale. Use ≥45° phase margin and ≥10 dB gain margin as engineering review criteria. |
| Load transients | Apply measured current steps at the socket with 100 ns and 1 µs edge settings and 10, 20, 50, and 100 µs pulse widths. Record actual edge rate, droop, overshoot, recovery, and repetition rate. |
| Reset | Test local and remote reset, simultaneous assertion, GPIO high impedance, disconnected remote cable, and remote-source power loss. Capture the actual J1.54 waveform. |
| Power-qualified reset | Capture CORE_PG/IO_VALID and reset during supply transients. Measure short events directly; separate combinational reset behavior from faults that clear the run latch. |
| Telemetry | Calibrate voltage, shunt readings, zero-current offset, and board-temperature readings. Record instrument settings and temperature. |
| ASIC operation | Establish power and clock, reset the DUT, then characterize voltage, frequency, workload, errors, and temperature. Include nominal operation and selected low-voltage and boost points. |
| Sustained operation | Run selected operating points for eight hours, logging resets, errors, supply extrema, current, temperature, and airflow. |

Choose pulsed-load amplitude and duty cycle within the configured input, current, and thermal limits. The 10 A continuous target is not an instantaneous current clamp or a required load at every voltage. Numerical droop acceptance limits are not assigned; use the measurements to assess board delivery and the observed ASIC operating region.

Measure rising and falling load edges. Trigger actual ASIC captures on kernel start and completion. Test isolated kernels and repeated workloads with different idle intervals. Probe socket power and ground locally and document bandwidth and probe loading.

## Test record

Each record should identify the board and DUT, hardware revision, fitted capacitor population, controller revision, register readback, clock settings, input wiring, load waveform, probe locations, instrument configuration, and temperature. Attach the waveforms supporting supply extrema and reset events. Keep board-side observations separate from inferred die behavior.
