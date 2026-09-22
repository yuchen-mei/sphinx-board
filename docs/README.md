# Design Documentation

These documents describe the V2 schematic design and its required behavior. Start with the circuit description and operating procedure if you know the ASIC but are new to the board. Completed design checks and pending board measurements are distinguished in the verification document.

| Document | Scope |
|---|---|
| [Requirements](REQUIREMENTS.md) | Experiment, operating range, and design objectives |
| [Circuit description](DESIGN.md) | Power paths, protection, and telemetry |
| [Autonomous power](AUTONOMOUS_POWER.md) | Retained power/reset state, independent protection, command completion, and Pico-loss acceptance tests |
| [Power configuration](POWER_CONFIGURATION.md) | PMBus address, capacitor populations, and compensation settings |
| [Reset and control](RESET_AND_CONTROL.md) | Controller ON/OFF, fault latch, STOP, and local/remote reset |
| [I/O enable interface](IO_ENABLE.md) | Circuit connections and transient verification |
| [Layout requirements](LAYOUT_HANDOFF.md) | Power delivery, probing, signals, and mechanical integration |
| [Verification](VALIDATION.md) | Schematic evidence and board measurement plan |
| [Final source review](FINAL_REVIEW_2026-09-22.md) | Completed independent review, corrections, and remaining physical qualification |
| [References](REFERENCES.md) | Manufacturer documents and their applicability |

The [schematic](../schematic/exports/sphinx_power_v2.pdf), [netlist](../schematic/exports/sphinx_power_v2.net.xml), [parts catalog](../schematic/bom/parts_catalog.json), and [component list](../schematic/bom/component_list.csv) define component population and connections. Sheet 09 covers autonomous control and sheet 10 independent protection. Use [current generated evidence](VALIDATION.md) for design counts and check results; this documentation does not maintain duplicate fixed totals.

The normal workflow is one checked `ON`, an explicit reset with the external clock running, then either one kernel for functional correctness or a large back-to-back kernel loop followed by steady voltage/current/power measurements. Once a power command succeeds, continuously valid 12 V and healthy hardware retain operation through Pico inactivity, USB disconnection, reboot, or loss of Pico power. Complete board input loss defaults OFF when power returns. Measurements are requested when needed; they are not a power-sustain heartbeat.
