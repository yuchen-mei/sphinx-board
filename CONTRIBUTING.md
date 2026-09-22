# Repository Maintenance

Edit the current V2 KiCad project under `schematic/` in place. Keep the schematic, local libraries, exact manufacturer part numbers, assembly options, and documentation consistent.

1. Update the affected sheets and component fields. Distinguish fitted parts from DNP positions. Test pads and net ties are PCB features and do not add purchase quantities.
2. Update the parts catalog and the affected BOM exports. Preserve exact ordering codes and package variants.
3. Run KiCad ERC after schematic edits. Export the PDF and XML netlist, inspect the affected pages, and compare the connections with the intended change.
4. Record validation results with their scope. A schematic check, simulation, and board measurement are separate forms of evidence.
5. For control changes, also verify the companion firmware against the retained-state and read-only-rejoin contract in `docs/AUTONOMOUS_POWER.md`. The firmware lives in `../controller`; run its tests from the workspace parent. Do not deploy it onto the former direct-GPIO schematic.
6. Update the checksums in `PROVENANCE.json` after modifying design files or exports. Review and save the current files together.

With KiCad CLI on `PATH`, run these commands from the repository root:

```sh
kicad-cli sch erc --severity-all --format json -o docs/evidence/erc.json schematic/sphinx_power_v2.kicad_sch
kicad-cli sch export netlist --format kicadxml -o schematic/exports/sphinx_power_v2.net.xml schematic/sphinx_power_v2.kicad_sch
kicad-cli sch export pdf -o schematic/exports/sphinx_power_v2.pdf schematic/sphinx_power_v2.kicad_sch
python3 tools/verify_control_connectivity.py
```

Write documentation in English. Describe the current V2 circuit in the present tense. State requirements, configured values, measured results, and unavailable data explicitly. Include calculations only when their inputs apply to this design. Keep documentation focused on the current design and validation.

Keep firmware, generated fabrication files, editor state, credentials, and local caches outside this schematic repository.
