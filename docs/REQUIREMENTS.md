# Design Requirements

## Experiment

The board supports characterization of a TSMC N7 ASIC across core voltage, clock frequency, and workload. Functionality testing runs a kernel once and compares its output with the expected result. Power testing runs the kernel in a large back-to-back loop, waits for steady operation, and reads averaged voltage, current, and power. Power delivery must accommodate both the sustained load and the transitions at kernel start and completion.

| Parameter | Requirement or experiment input |
|---|---|
| Nominal core voltage | 0.75 V |
| Active core power | Approximately 5 W at the nominal operating point, supplied as an experiment input |
| Nominal active current | Approximately 6.67 A, calculated as 5 W / 0.75 V |
| Clock frequency | 1 GHz target; higher frequencies are characterization points |
| Core adjustment range | 0.30–1.20 V; default sweep increment 50 mV |
| Continuous core current | 10 A conservative board design target |
| I/O supply | Fixed 1.8 V; 1 A provisioned load budget |
| Input supply | 12 V nominal; 11.5–13 V operating target at the input terminals |
| Control | Pico USB ON/OFF, hardware fault latch and STOP, local and remote DUT reset |
| Telemetry | Core and I/O voltage/current, plus board temperature |
| Initial build | Five boards plus component spares |

The adjustment range is a superset of the intended experimental operating points. The 0.30 V lower limit supports low-voltage energy-efficiency measurements. Approximately 1.0 V is an empirically supported boost point for the available devices. No device absolute-maximum voltage is specified. Select boost voltage, frequency, and workload per device and record the measured operating conditions.

I/O voltage is fixed because the experiment does not require an I/O voltage sweep and the I/O load is small. The 1 A budget is provisioning, not a measured I/O consumption value.

Minimize routine experiment steps: one `ON` command performs configuration checks and starts the supplies. Reset is a separate explicit user or experiment-script action. Ordinary power-good loss, undervoltage, voltage deviation, PMBus warnings, and a missing USB host heartbeat are recorded without resetting the DUT or stopping an ongoing experiment. These observations can be the intended result of voltage/frequency characterization.

Retain protection against damaging overvoltage, overtemperature, and excessive current, together with explicit `OFF` and hardware STOP. A latched protective trip or STOP must not restart the supplies automatically when its cause clears; a new explicit `ON` requests recovery. Regulator/eFuse intrinsic undervoltage lockout and loss of control power remain physical operating constraints. An intrinsic input UVLO interruption can recover if the control supply and run latch remain valid; it is not an ASIC power-good interlock or an explicit reset request.

## Power delivery

Minimize board resistance and transient voltage excursions through local regulation, short current paths, distributed capacitance, and socket-side differential feedback. Evaluate voltage at multiple socket power/ground groups under static and pulsed loads. Record droop, overshoot, recovery time, and reset activity. Numerical droop acceptance limits are not specified.

The feedback endpoint is on the PCB. Socket contacts, bond wires, and the on-chip power grid lie beyond that endpoint. Package and socket replacement are design options. The package concerns are bond-wire geometry and encapsulant thermal conductivity; no numerical parasitic or thermal model is assigned without corresponding data.

## Reset and sequencing

DUT reset is active high at 1.8 V. The clock must run during reset. Reset release is asynchronous; no clock-synchronized release is required by the experiment. Manual reset and remote reset use pulses with ample duration rather than a minimum-cycle pulse. No numerical minimum pulse width is specified.

There is no experiment-specific requirement for the relative Core/I/O power sequence or inter-rail delay. With valid VIO and no explicit reset request, the hardware holds DUT reset released, including when the Pico is unprogrammed or its GPIO is high impedance. Neither power-good signals, the run latch, voltage deviations, nor automatic power sequencing asserts reset. Reset is asserted only by the local button, remote optocoupler input, or an explicit Pico reset command. Its 1.8 V high level depends on VIO being present; behavior during a collapsing or absent VIO is not a guaranteed logic level.

For an intentional DUT reset, establish the supplies and run the external clock, then explicitly assert and release reset. `ON`, `OFF`, and a voltage-range change do not insert a reset pulse. A range change that requires disabling the supplies can destroy DUT state; the experiment script decides when to reset and reload the kernel afterward.

## Thermal characterization

Measure regulator, inductor, capacitor, socket, and package temperatures at the selected voltage, frequency, workload, and airflow. The board NTC measures local board temperature. No die junction-temperature limit is assigned in this specification.

Characterize continuous operation at selected operating points for eight hours, recording functional errors, resets, supply extrema, current, and temperature. Determine the usable operating region from measurements rather than extrapolating the 5 W nominal point.
