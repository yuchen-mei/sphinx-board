# Sphinx V1 Archive

This branch contains the first-generation Sphinx passive adapter board. External supplies feed the 0V75 and 1V8 rails directly. The board includes the socket, signal connectors, decoupling capacitors, and manual reset circuit.

The current programmable-power schematic project is on [main](https://github.com/yuchen-mei/sphinx-board/tree/main).

## Files

Open [board/sphinx_board.kicad_pro](board/sphinx_board.kicad_pro) in KiCad.

| File | Contents |
|---|---|
| [Schematic](board/sphinx_board.kicad_sch) | Original V1 circuit |
| [PCB](board/sphinx_board.kicad_pcb) | Original V1 layout |
| [CSV BOM](board/sphinx_board.csv) | Component list |
| [Sphinx BOM.xlsx](board/Sphinx%20BOM.xlsx) | Source BOM workbook |
| [sphinx_board BOM updated.xlsx](board/sphinx_board%20BOM%20updated.xlsx) | Additional source BOM workbook |

The six board files are preserved byte for byte. [ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json) records their SHA-256 checksums. The archive date is 2026-09-18. The BOM workbooks are source records; no final fitted-population designation is assigned to either workbook.

The KiCad files contain embedded symbols and footprints. Their referenced external `my_symbols` and `my_footprints` libraries are not included. Restore or explicitly define those libraries before updating components from a library.

## Maintenance

`legacy-v1-archive` is the fixed source snapshot. Documentation may be maintained on `legacy/v1`; the six board files remain immutable. Start a separate branch from the archive tag for electrical or layout changes.

This branch and `main` have independent histories. The V1 PCB applies only to the V1 passive adapter.
