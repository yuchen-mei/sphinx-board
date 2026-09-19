# Design Documentation

These documents describe the current V2 hardware.

| Document | Scope |
|---|---|
| [Requirements](REQUIREMENTS.md) | Experiment, operating range, and design objectives |
| [Circuit description](DESIGN.md) | Power paths, protection, and telemetry |
| [Power configuration](POWER_CONFIGURATION.md) | PMBus address, capacitor populations, and compensation settings |
| [Reset and control](RESET_AND_CONTROL.md) | Controller ON/OFF, fault latch, STOP, and local/remote reset |
| [I/O enable interface](IO_ENABLE.md) | Circuit connections and transient verification |
| [Layout requirements](LAYOUT_HANDOFF.md) | Power delivery, probing, signals, and mechanical integration |
| [Verification](VALIDATION.md) | Schematic evidence and board measurement plan |
| [References](REFERENCES.md) | Manufacturer documents and their applicability |

The [schematic](../schematic/exports/sphinx_power_v2.pdf), [parts catalog](../schematic/bom/parts_catalog.json), and [component list](../schematic/bom/component_list.csv) define the current component population and connections.
