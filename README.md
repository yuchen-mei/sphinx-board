# Sphinx ASIC Test Board

Sphinx is a test board for voltage, frequency, power, and energy-efficiency characterization of a TSMC N7 ASIC. The nominal operating point is 0.75 V core supply, approximately 5 W during kernel execution, and a target clock frequency of 1 GHz. A local programmable regulator, distributed decoupling, and differential feedback at the socket provide the board-level power delivery path.

Hardware: **V2**. This package contains the current schematic project, local KiCad libraries, BOM, schematic exports, and design documentation. The [Pico controller source](../controller/README.md) is maintained alongside this package. There is no V2 PCB, completed host test application, or board measurement evidence in the current repository.

## Design files

Open [schematic/sphinx_power_v2.kicad_pro](schematic/sphinx_power_v2.kicad_pro) in KiCad 10.

| File | Contents |
|---|---|
| [Schematic PDF](schematic/exports/sphinx_power_v2.pdf) | Eleven schematic sheets |
| [XML netlist](schematic/exports/sphinx_power_v2.net.xml) | Component connections |
| [Parts catalog](schematic/bom/parts_catalog.json) | Exact parts, assembly options, and application notes |
| [Purchase list](schematic/bom/BUY_LIST.csv) | Quantities for five boards and spares |
| [Component list](schematic/bom/component_list.csv) | Schematic components and fields |
| [Documentation](docs/README.md) | Requirements, interfaces, layout constraints, and verification |
| [Maintenance](CONTRIBUTING.md) | Editing and validation procedure |

## Operating scope

The core regulator covers 0.30–1.20 V. The lower end supports low-voltage energy-efficiency measurements. The conservative continuous-current design target is 10 A. I/O operates at a fixed 1.8 V. The supported operating region is determined experimentally for each device and workload; the regulator range does not define an ASIC voltage rating.

The board uses explicit `SET` / `ON` commands to program and enable the supplies. Once a command completes, the regulator and board-powered GPIO expander retain the voltage, enable and explicit reset state while 12 V remains valid. Pico restart, USB disconnect, firmware stop or Pico removal does not change that state. The [autonomous power contract](docs/AUTONOMOUS_POWER.md) defines the hardware, recovery rules and acceptance tests. Independent protection and the STOP button remain active without Pico. DUT reset is a separate, active-high control: the local button, remote optocoupler, or an explicit Pico command asserts it. With valid VIO and no request, reset is released without depending on the Pico, power-good signals, or run-latch state.

Functionality testing runs one kernel and checks its output. Power testing runs a large back-to-back kernel loop and reads averaged voltage, current, and power after operation settles. Ordinary PG/undervoltage observations, PMBus warnings, and USB inactivity are reported without resetting or shutting down the DUT. Independent board core/I/O overvoltage and local temperature protection clear the hardware run latch. The core regulator and input eFuse also retain their own protection; a regulator-only fault can stop Core without clearing I/O. STOP and latched protective trips require a new explicit `ON`; internally latched eFuse faults can require cycling the 12 V input. Full board-power loss returns to OFF. Partial input brownouts are outside the state-retention guarantee and must be characterized; regulator and control-domain resets need not occur together.

The 10 A target still requires PCB resistance, loop stability, transient, socket/package, and sustained thermal qualification. Controller commissioning and calibration are required before unrestricted operation; a passing source-level check does not establish board readiness.

The controller follows the [startup interface](docs/RESET_AND_CONTROL.md). File checksums and verification scope are recorded in [PROVENANCE.json](PROVENANCE.json).
