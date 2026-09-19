#!/usr/bin/env python3
"""Check the current V2 control electrical contract and procurement records.

Run from any directory with Python 3; no third-party packages, Git history, or
network are required. The exported netlist, catalog, purchase list, and existing
ERC report are inputs. This does not regenerate exports or test a physical board.
"""

import argparse
import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

NETLIST_PATH = "schematic/exports/sphinx_power_v2.net.xml"
# Reviewed physical connections, including complete fault and enable interfaces.
# Update this contract only after reviewing an intentional electrical change.
CONTROL_PIN_CONTRACT = {'C306': {'1': 'VIN12', '2': 'IO_EN_INHIBIT'},
 'C307': {'1': 'IO_EN', '2': 'GND'},
 'C506': {'1': '3V3_CTRL', '2': 'GND'},
 'J1': {'54': 'reset'},
 'J602': {'1': 'ZED_3V3', '2': 'ZED_RESET_OD'},
 'Q301': {'1': 'IO_EN_CTRL', '2': 'GND', '3': 'IO_EN_PULLDOWN'},
 'Q302': {'1': 'IO_EN_INHIBIT', '2': 'GND', '3': 'IO_EN'},
 'Q601': {'1': 'RESET_BASE', '2': 'GND', '3': 'reset'},
 'R210': {'1': 'CORE_EN', '2': 'GND'},
 'R211': {'1': '3V3_CTRL', '2': 'CORE_PG'},
 'R303': {'1': 'IO_EN', '2': 'GND'},
 'R305': {'1': 'VIN12', '2': 'IO_EN'},
 'R306': {'1': 'VIN12', '2': 'IO_EN_INHIBIT'},
 'R307': {'1': 'IO_EN_CTRL', '2': 'GND'},
 'R308': {'1': 'IO_EN_INHIBIT', '2': 'IO_EN_PULLDOWN'},
 'R411': {'1': 'RESET_RELEASE', '2': 'GND'},
 'R503': {'1': '0V75', '2': 'CORE_OV_SENSE'},
 'R504': {'1': 'CORE_OV_SENSE', '2': 'GND'},
 'R506': {'1': '3V3_CTRL', '2': 'HW_FAULT_N'},
 'R507': {'1': 'RUN_SET', '2': 'GND'},
 'R509': {'1': 'CORE_REQ', '2': 'GND'},
 'R510': {'1': 'IO_REQ', '2': 'GND'},
 'R511': {'1': '1V8', '2': 'IO_UV_SENSE'},
 'R512': {'1': 'IO_UV_SENSE', '2': 'GND'},
 'R513': {'1': '3V3_CTRL', '2': 'IO_VALID'},
 'R514': {'1': 'VIN12', '2': 'VIN12_UV_SENSE'},
 'R515': {'1': 'VIN12_UV_SENSE', '2': 'GND'},
 'R602': {'1': '1V8', '2': 'reset'},
 'R603': {'1': 'RESET_RELEASE_OK', '2': 'RESET_BASE'},
 'R604': {'1': 'RESET_BASE', '2': 'GND'},
 'R605': {'1': 'ZED_3V3', '2': 'ZED_OPTO_A'},
 'SW502': {'1': 'HW_FAULT_N', '2': 'GND'},
 'SW601': {'1': 'RESET_BASE', '2': 'GND'},
 'U101': {'1': 'INPUT_UVLO',
          '2': 'INPUT_OVLO',
          '3': 'unconnected-(U101-AUXOFF-Pad3)',
          '4': 'HW_FAULT_N',
          '5': 'VIN_FUSED',
          '6': 'VIN12',
          '7': 'INPUT_DVDT',
          '8': 'GND',
          '9': 'INPUT_ILM',
          '10': 'unconnected-(U101-ITIMER-Pad10)'},
 'U201': {'1': 'CORE_PG', '27': 'CORE_EN', '33': 'CORE_SENSE_P', '34': 'CORE_SENSE_N'},
 'U301': {'13': 'IO_EN', '14': '1V8'},
 'U401': {'4': 'CORE_REQ',
          '5': 'IO_REQ',
          '6': 'RESET_RELEASE',
          '7': 'RUN_LATCH',
          '9': 'CORE_PG',
          '10': 'IO_VALID',
          '11': 'HW_FAULT_N',
          '14': 'RUN_SET',
          '20': 'HW_FAULT_N',
          '36': '3V3_CTRL'},
 'U501': {'1': 'HW_FAULT_N',
          '2': 'GND',
          '3': 'REF1V242',
          '4': 'CORE_OV_SENSE',
          '5': 'REF1V242',
          '6': '3V3_CTRL'},
 'U502': {'1': 'HW_FAULT_N',
          '2': 'GND',
          '3': '3V3_CTRL',
          '4': 'unconnected-(U502-CT-Pad4)',
          '5': '3V3_CTRL',
          '6': '3V3_CTRL'},
 'U503': {'1': 'RUN_SET_CLEAN',
          '2': '3V3_CTRL',
          '3': 'unconnected-(U503-Q_N-Pad3)',
          '4': 'GND',
          '5': 'RUN_LATCH',
          '6': 'HW_CLEAR_N',
          '7': '3V3_CTRL',
          '8': '3V3_CTRL'},
 'U504': {'1': 'RUN_LATCH',
          '2': 'CORE_REQ',
          '3': 'CORE_EN',
          '4': 'RUN_LATCH',
          '5': 'IO_REQ',
          '6': 'IO_EN_CTRL',
          '7': 'GND',
          '8': 'RESET_PERMIT',
          '9': 'RUN_LATCH',
          '10': 'RESET_RELEASE',
          '11': 'unconnected-(U504-4Y-Pad11)',
          '12': 'GND',
          '13': 'GND',
          '14': '3V3_CTRL'},
 'U506': {'1': 'CORE_PG',
          '2': 'GND',
          '3': 'IO_VALID',
          '4': 'RESET_RELEASE_OK',
          '5': '3V3_CTRL',
          '6': 'RESET_PERMIT'},
 'U507': {'1': 'RUN_SET',
          '2': 'GND',
          '3': 'HW_FAULT_N',
          '4': 'HW_CLEAR_N',
          '5': '3V3_CTRL',
          '6': 'RUN_SET_CLEAN'},
 'U508': {'1': 'IO_VALID',
          '2': 'GND',
          '3': 'IO_UV_SENSE',
          '4': 'IO_UV_REF',
          '5': 'IO_UV_REF',
          '6': '3V3_CTRL'},
 'U509': {'1': 'HW_FAULT_N',
          '2': 'GND',
          '3': 'VIN12_UV_SENSE',
          '4': 'VIN12_UV_REF',
          '5': 'VIN12_UV_REF',
          '6': '3V3_CTRL'},
 'U601': {'1': 'ZED_OPTO_A', '2': 'ZED_RESET_OD', '3': 'GND', '4': 'RESET_BASE'}}

U504_PINMAP = {
    "1": ("1A", "RUN_LATCH", "input"),
    "2": ("1B", "CORE_REQ", "input"),
    "3": ("1Y", "CORE_EN", "output"),
    "4": ("2A", "RUN_LATCH", "input"),
    "5": ("2B", "IO_REQ", "input"),
    "6": ("2Y", "IO_EN_CTRL", "output"),
    "7": ("GND", "GND", "power_in"),
    "8": ("3Y", "RESET_PERMIT", "output"),
    "9": ("3A", "RUN_LATCH", "input"),
    "10": ("3B", "RESET_RELEASE", "input"),
    "11": ("4Y", "unconnected-(U504-4Y-Pad11)", "output+no_connect"),
    "12": ("4A", "GND", "input"),
    "13": ("4B", "GND", "input"),
    "14": ("VCC", "3V3_CTRL", "power_in"),
}
NONPURCHASE_REFS = {
    "NT601", "NT602", "TP4", "TP607", "TP7", "TP801",
    "TP802", "TP803", "TP804", "TP805", "TP806",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_netlist(data):
    root = ET.fromstring(data)
    components = {item.get("ref"): item for item in root.find("components")}
    pins, nodes, nets = {}, {}, {}
    for net in root.find("nets"):
        name = net.get("name")
        if name in nets:
            raise ValueError(f"Duplicate net name: {name}")
        nets[name] = net
        for node in net:
            key = (node.get("ref"), node.get("pin"))
            if key in pins:
                raise ValueError(f"Pin appears on multiple nets: {key}")
            pins[key], nodes[key] = name, node
    return root, components, pins, nodes, nets


def mpn(component):
    prop = component.find("property[@name='MPN']")
    return prop.get("value") if prop is not None else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional evidence JSON path")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    output = args.output or project / "docs/evidence/hardware_review.json"
    current = (project / NETLIST_PATH).read_bytes()
    new_root, new_comps, new_pins, new_nodes, new_nets = parse_netlist(current)
    errors = []
    expected = {(ref, pin): net for ref, pins in CONTROL_PIN_CONTRACT.items()
                for pin, net in pins.items()}
    pin_differences = [
        {"reference": ref, "pin": pin, "expected": net,
         "actual": new_pins.get((ref, pin))}
        for (ref, pin), net in expected.items()
        if new_pins.get((ref, pin)) != net
    ]
    exact_nets = (
        "RUN_SET", "RUN_SET_CLEAN", "RUN_LATCH", "HW_FAULT_N", "HW_CLEAR_N",
        "CORE_EN", "CORE_REQ", "IO_REQ", "IO_EN_CTRL", "IO_EN", "IO_EN_PULLDOWN",
        "IO_EN_INHIBIT", "RESET_PERMIT", "RESET_RELEASE", "RESET_RELEASE_OK",
        "RESET_BASE", "ZED_OPTO_A", "ZED_3V3", "ZED_RESET_OD", "reset",
        "CORE_PG", "IO_VALID", "CORE_OV_SENSE", "VIN12_UV_SENSE", "IO_UV_SENSE",
    )
    net_member_differences = []
    for net in exact_nets:
        wanted = {key for key, value in expected.items() if value == net}
        actual = {key for key, value in new_pins.items() if value == net}
        # Reset also has dedicated probe access, specified separately below.
        if net == "reset":
            wanted.add(("TP7", "1"))
        if wanted != actual:
            net_member_differences.append({"net": net, "missing": sorted(wanted-actual),
                                           "unexpected": sorted(actual-wanted)})
    if pin_differences or net_member_differences:
        errors.append("The current netlist differs from the reviewed control electrical contract.")
    if len(new_comps) != 219 or len(new_nets) != 119:
        errors.append("Current V2 component/net counts differ from 219/119.")
    physical_pin_differences = []
    for pin, (function, net, pin_type) in U504_PINMAP.items():
        node = new_nodes.get(("U504", pin))
        if node is None or (
            new_pins[("U504", pin)] != net
            or node.get("pinfunction") != f"{function}_{pin}"
            or node.get("pintype") != pin_type
        ):
            physical_pin_differences.append(pin)
    u504 = new_comps.get("U504")
    if u504 is None or (
        mpn(u504) != "74LVC08AT14-13"
        or u504.findtext("value") != "74LVC08AT14-13"
        or u504.findtext("footprint") != "Sphinx_V2:Package_SO__TSSOP-14_4.4x5mm_P0.65mm"
        or physical_pin_differences
    ):
        errors.append("U504 part, package, physical pin function, or pin type mismatch.")
    if new_nodes.get(("U503", "3")) is None or new_nodes[("U503", "3")].get("pintype") != "output+no_connect":
        errors.append("U503 Q-bar must be explicitly unconnected.")
    catalog_path = project / "schematic/bom/parts_catalog.json"
    buy_path = project / "schematic/bom/BUY_LIST.csv"
    catalog_bytes, buy_bytes = catalog_path.read_bytes(), buy_path.read_bytes()
    catalog = json.loads(catalog_bytes)
    parts = catalog["parts"]
    catalog_refs, bom_differences = {}, []
    for part in parts:
        refs, dnp = part["references"], part["dnp_references"]
        if len(refs) != part["quantity_per_board"] or len(refs) - len(dnp) != part["fitted_per_board"]:
            bom_differences.append([part["mpn"], "catalog reference/fitted count mismatch"])
        for ref in refs:
            if ref in catalog_refs:
                bom_differences.append([ref, "duplicate catalog reference"])
            catalog_refs[ref] = part["mpn"]
            if ref not in new_comps or mpn(new_comps[ref]) != part["mpn"]:
                bom_differences.append([ref, part["mpn"], mpn(new_comps[ref]) if ref in new_comps else None])
    nonpurchase = set(new_comps) - set(catalog_refs)
    if nonpurchase != NONPURCHASE_REFS:
        bom_differences.append(["nonpurchase reference set", sorted(nonpurchase)])
    with buy_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(parts):
        bom_differences.append(["CSV and catalog row count mismatch"])
    for part, row in zip(parts, rows):
        for field in row:
            expected_value = part.get(field)
            if isinstance(expected_value, list):
                expected_value = " ".join(expected_value)
            else:
                expected_value = "" if expected_value is None else str(expected_value)
            if row[field] != expected_value:
                bom_differences.append([part["mpn"], field, expected_value, row[field]])
    if bom_differences:
        errors.append("BOM/netlist/CSV mismatch.")
    erc_path = project / "docs/evidence/erc.json"
    erc_bytes = erc_path.read_bytes()
    erc = json.loads(erc_bytes)
    violations = [violation for sheet in erc.get("sheets", [])
                  for violation in sheet.get("violations", [])]
    if not erc.get("sheets") or violations:
        errors.append("The existing ERC report is missing sheets or reports violations.")
    report = {
        "review": "Current V2 hardware control electrical contract and BOM audit",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "PASS" if not errors else "FAIL",
        "reproduce": "python3 tools/verify_control_connectivity.py",
        "current": {"path": NETLIST_PATH, "sha256": sha256(current),
                    "components": len(new_comps), "nets": len(new_nets)},
        "connectivity": {
            "netlist_pins": len(new_pins), "contract_pins_checked": len(expected),
            "full_control_pin_contract": CONTROL_PIN_CONTRACT,
            "exact_net_membership_checked": list(exact_nets),
            "pin_differences": pin_differences,
            "net_member_differences": net_member_differences,
            "scope": "Fault detectors, STOP, hardware clear, run-set pulse, run latch, all enable/reset gates, I/O-enable interface, local/remote reset, and controller interfaces.",
        },
        "U504": {
            "manufacturer": "Diodes Incorporated", "mpn": "74LVC08AT14-13",
            "package": "TSSOP-14; 4.4 x 5 mm body; 0.65 mm pitch",
            "datasheet": "https://www.diodes.com/datasheet/download/74LVC08A.pdf",
            "datasheet_revision": "DS35261 Rev. 4-2, September 2023",
            "source_checked_on": "2026-09-19",
            "datasheet_pages": {"pinmap": 2, "drive_and_Ioff": 4, "ordering": 7, "package": 8},
            "physical_pinmap": {pin: {"function": f, "net": n, "type": t}
                                for pin, (f, n, t) in U504_PINMAP.items()},
            "physical_pin_differences": physical_pin_differences,
            "drive_assessment": "R307 load <=3.6/(270*0.99)=13.47 mA. At VCC=3 V, the conservative 24 mA drive row specifies VOH >=2.2 V through 85 C and >=2.0 V through 125 C, above Q301's 1.8 V gate-drive test point. This does not establish full-temperature MOSFET or transient performance.",
            "power_off_assessment": "At VCC=0 and VI/VO=0..3.6 V, Ioff <=10 uA through 85 C and <=20 uA through 125 C. Existing output pull-downs remain. This is not a brownout or board-transient guarantee.",
        },
        "fault_behavior": {
            "assessment": "STOP and hardware-fault detectors clear U503 asynchronously through U507. Fault recovery creates no RUN_SET rising edge and therefore does not set the latch by itself.",
            "firmware_condition": "No automatic RUN_SET pulses after a fault, boot or reconnect; a fresh ON request is required. A faulty controller can issue another pulse, so the circuit is not an independent prohibition of all controller-initiated restarts.",
            "reset_qualifier_limit": "CORE_PG and IO_VALID are combinational reset qualifiers; their recovery is not latched by U503.",
        },
        "bom": {
            "catalog_path": "schematic/bom/parts_catalog.json", "catalog_sha256": sha256(catalog_bytes),
            "buy_list_path": "schematic/bom/BUY_LIST.csv", "buy_list_sha256": sha256(buy_bytes),
            "catalog_order_lines": len(parts), "csv_order_lines": len(rows),
            "purchased_component_references": len(catalog_refs),
            "nonpurchase_references": sorted(nonpurchase),
            "mpn_references_checked": len(catalog_refs),
            "alignment_differences": bom_differences,
        },
        "erc": {"path": "docs/evidence/erc.json", "sha256": sha256(erc_bytes),
                "reported_violations": len(violations), "reported_date": erc.get("date"),
                "ignored_checks": erc.get("ignored_checks", []),
                "regenerated_by_this_script": False},
        "physical_tests_performed": False,
        "firmware_tests_performed_by_this_script": False,
        "limitations": [
            "No board measurements, analog simulation, thermal qualification, or real-device firmware execution.",
            "The script checks exported XML and existing ERC evidence; regenerate both after schematic edits. Firmware tests and visual review are separate checks.",
            "Datasheet drive and power-off review is recorded here; no network or stock check is performed by this script.",
        ],
        "errors": errors,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"{report['result']}: {len(expected)} contract pins, {len(catalog_refs)} procurement MPNs, {len(rows)} order lines, {len(violations)} ERC violations")
    print(f"Evidence: {output}")
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
