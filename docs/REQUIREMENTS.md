# Design Requirements

## Experiment

The board supports characterization of a TSMC N7 ASIC across core voltage, clock frequency, and workload. Kernel execution lasts tens of thousands to hundreds of thousands of cycles. Power delivery must accommodate both the active load and the transitions at kernel start and completion.

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

Minimize routine experiment steps: one `ON` command performs configuration checks and starts the supplies. Hardware faults must stop the supplies independently of software and must not automatically restart them when the fault clears. A new explicit `ON` command from the user or experiment script requests recovery.

## Power delivery

Minimize board resistance and transient voltage excursions through local regulation, short current paths, distributed capacitance, and socket-side differential feedback. Evaluate voltage at multiple socket power/ground groups under static and pulsed loads. Record droop, overshoot, recovery time, and reset activity. Numerical droop acceptance limits are not specified.

The feedback endpoint is on the PCB. Socket contacts, bond wires, and the on-chip power grid lie beyond that endpoint. Package and socket replacement are design options. The package concerns are bond-wire geometry and encapsulant thermal conductivity; no numerical parasitic or thermal model is assigned without corresponding data.

## Reset and sequencing

DUT reset is active high at 1.8 V. The clock must run during reset. Reset release is asynchronous; no clock-synchronized release is required by the experiment. Manual reset and remote reset use pulses with ample duration rather than a minimum-cycle pulse. No numerical minimum pulse width is specified.

There is no experiment-specific requirement for the relative Core/I/O power sequence or inter-rail delay. The controller must maintain reset during power transitions and establish valid supplies and a running clock before completing the DUT reset procedure. Hardware reset on invalid power remains part of the design.

## Thermal characterization

Measure regulator, inductor, capacitor, socket, and package temperatures at the selected voltage, frequency, workload, and airflow. The board NTC measures local board temperature. No die junction-temperature limit is assigned in this specification.

Characterize continuous operation at selected operating points for eight hours, recording functional errors, resets, supply extrema, current, and temperature. Determine the usable operating region from measurements rather than extrapolating the 5 W nominal point.
