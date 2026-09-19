# Sphinx ASIC Test Board

Sphinx is a test board for voltage, frequency, power, and energy-efficiency characterization of a TSMC N7 ASIC. The nominal operating point is 0.75 V core supply, approximately 5 W during kernel execution, and a target clock frequency of 1 GHz. A local programmable regulator, distributed decoupling, and differential feedback at the socket provide the board-level power delivery path.

Hardware: **V2**. This repository contains the current schematic project, local KiCad libraries, BOM, schematic exports, and design documentation. PCB layout and firmware are outside its scope. Board measurements are not yet available.

## Design files

Open [schematic/sphinx_power_v2.kicad_pro](schematic/sphinx_power_v2.kicad_pro) in KiCad 10.

| File | Contents |
|---|---|
| [Schematic PDF](schematic/exports/sphinx_power_v2.pdf) | Nine schematic sheets |
| [XML netlist](schematic/exports/sphinx_power_v2.net.xml) | Component connections |
| [Parts catalog](schematic/bom/parts_catalog.json) | Exact parts, assembly options, and application notes |
| [Purchase list](schematic/bom/BUY_LIST.csv) | Quantities for five boards and spares |
| [Component list](schematic/bom/component_list.csv) | Schematic components and fields |
| [Documentation](docs/README.md) | Requirements, interfaces, layout constraints, and verification |
| [Maintenance](CONTRIBUTING.md) | Editing and validation procedure |

## Operating scope

The core regulator covers 0.30–1.20 V. The lower end supports low-voltage energy-efficiency measurements. The conservative continuous-current design target is 10 A. I/O operates at a fixed 1.8 V. The supported operating region is determined experimentally for each device and workload; the regulator range does not define an ASIC voltage rating.

The board uses a single controller `ON` command to start an experiment, with a hardware fault latch and STOP button. It also provides power-qualified reset, a local reset button, an optocoupler input for remote reset, and socket-side voltage and reset measurement access. After a fault, a new `ON` command can restart the board once the fault is resolved; faults latched inside the eFuse may require cycling the 12 V input.

The controller follows the [startup interface](docs/RESET_AND_CONTROL.md). File checksums and verification scope are recorded in [PROVENANCE.json](PROVENANCE.json).
