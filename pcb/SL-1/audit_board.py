"""Audit SL-1 pad assignments and export routing geometry for inspection.

Author: Trishan Biswas
Project started: February 2026
Status: Ongoing. Run with KiCad's bundled Python; DRC is a separate check.
"""

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

# Independently transcribed interface requirements, rather than importing the
# generator's net tables. Empty pads on module sockets are intentional unused IO.
EXPECTED = {
    "J1": {1: "+3V3", 5: "SCREEN_BUTTON", 6: "BATTERY_SENSE", 14: "GND", 15: "VIN_5V"},
    "J2": {1: "GND", 2: "SPI_MOSI", 3: "I2C_SCL", 6: "I2C_SDA", 7: "GND",
           8: "SPI_MISO", 9: "SPI_SCK", 10: "SD_CS", 13: "TFT_RST", 14: "TFT_DC", 15: "TFT_CS"},
    "J3": {1: "+3V3", 2: "I2C_SDA", 3: "GND", 4: "I2C_SCL"},
    "J4": {1: "+3V3", 2: "GND", 3: "I2C_SCL", 4: "I2C_SDA"},
    "J5": {1: "+3V3", 2: "GND", 3: "SPI_MOSI", 4: "GND", 5: "SPI_MISO", 6: "GND",
           7: "SPI_SCK", 8: "GND", 9: "SD_CS", 10: "TFT_RST", 11: "TFT_DC",
           12: "+3V3", 13: "TFT_CS", 14: "GND"},
    "J6": {1: "SCREEN_BUTTON", 2: "GND"},
    "J7": {1: "+5V_EXT", 2: "GND"},
    "J8": {1: "BAT_RAW", 2: "GND"},
    "F1": {1: "+5V_EXT", 2: "+5V_FUSED"},
    "D1": {1: "VIN_5V", 2: "+5V_FUSED"},  # SMA pad 1 is cathode.
    "R2": {1: "+3V3", 2: "SCREEN_BUTTON"},
    "R3": {1: "BAT_RAW", 2: "BATTERY_SENSE"},
    "R4": {1: "BATTERY_SENSE", 2: "GND"},
    "C1": {1: "BATTERY_SENSE", 2: "GND"},
    "C2": {1: "+3V3", 2: "GND"},
    "C3": {1: "+3V3", 2: "GND"},
}

PIN_CONSTANTS = {
    "PIN_I2C_SDA": 21, "PIN_I2C_SCL": 22, "PIN_SPI_SCK": 18,
    "PIN_SPI_MISO": 19, "PIN_SPI_MOSI": 23, "PIN_TFT_CS": 15,
    "PIN_SD_CS": 5, "PIN_SCREEN_BUTTON": 34, "PIN_BATTERY_ADC": 35,
}

COMMON_DOIT = {
    "J1": {4: "SCREEN_BUTTON", 5: "BATTERY_SENSE", 14: "GND", 15: "VIN_5V"},
    "J2": {1: "SPI_MOSI", 2: "I2C_SCL", 5: "I2C_SDA", 6: "SPI_MISO",
           7: "SPI_SCK", 8: "SD_CS", 11: "TFT_RST", 12: "TFT_DC",
           13: "TFT_CS", 14: "GND", 15: "+3V3"},
}


def xy(position):
    return [round(pcbnew.ToMM(position.x), 6), round(pcbnew.ToMM(position.y), 6)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=ROOT / "Stratologger_SL1.kicad_pcb")
    parser.add_argument("--output", type=Path, default=ROOT / "review" / "board-audit.json")
    args = parser.parse_args()
    board = pcbnew.LoadBoard(str(args.board))
    footprints = {item.GetReference(): item for item in board.GetFootprints()}
    errors = []
    pad_records = []
    for reference, expected in EXPECTED.items():
        if reference not in footprints:
            errors.append(f"Missing footprint {reference}")
            continue
        seen = set()
        for pad in footprints[reference].Pads():
            number = int(pad.GetNumber())
            actual = pad.GetNetname()
            required = expected.get(number, "")
            seen.add(number)
            if actual != required:
                errors.append(f"{reference}.{number}: {actual!r}, expected {required!r}")
            pad_records.append({"reference": reference, "pad": number, "net": actual,
                                "xy_mm": xy(pad.GetPosition()), "size_mm": xy(pad.GetSize()),
                                "drill_mm": xy(pad.GetDrillSize())})
        if expected.keys() - seen:
            errors.append(f"Missing pads on {reference}: {expected.keys() - seen}")
    for reference in footprints.keys() - EXPECTED.keys():
        if not reference.startswith("H"):
            errors.append(f"Unaudited footprint {reference}")

    config = (REPO / "include" / "config.h").read_text(encoding="utf-8")
    platform = (REPO / "platformio.ini").read_text(encoding="utf-8")
    for constant, expected in PIN_CONSTANTS.items():
        match = re.search(rf"\b{constant}\s*=\s*(\d+)", config)
        if not match or int(match.group(1)) != expected:
            errors.append(f"Firmware mismatch: {constant}")
    for constant, expected in {"TFT_MOSI": 23, "TFT_SCLK": 18, "TFT_CS": 15,
                               "TFT_DC": 2, "TFT_RST": 4, "TFT_MISO": 19}.items():
        if not re.search(rf"-D\s+{constant}={expected}\b", platform):
            errors.append(f"TFT build mismatch: {constant}")

    totals = defaultdict(float)
    widths = defaultdict(set)
    tracks, vias = [], []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            vias.append({"net": item.GetNetname(), "xy_mm": xy(item.GetPosition()),
                         "diameter_mm": pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu))})
            continue
        start, end = xy(item.GetStart()), xy(item.GetEnd())
        length = math.dist(start, end)
        net = item.GetNetname()
        width = pcbnew.ToMM(item.GetWidth())
        totals[net] += length
        widths[net].add(round(width, 3))
        tracks.append({"net": net, "start_mm": start, "end_mm": end,
                       "layer": board.GetLayerName(item.GetLayer()), "width_mm": width})
    graphics = []
    for item in board.GetDrawings():
        if isinstance(item, pcbnew.PCB_TEXT):
            graphics.append({"type": "text", "text": item.GetText(), "layer": board.GetLayerName(item.GetLayer()),
                             "xy_mm": xy(item.GetPosition()), "size_mm": xy(item.GetTextSize())})
        elif isinstance(item, pcbnew.PCB_SHAPE):
            graphics.append({"type": "shape", "shape": int(item.GetShape()),
                             "layer": board.GetLayerName(item.GetLayer()),
                             "start_mm": xy(item.GetStart()), "end_mm": xy(item.GetEnd()),
                             "width_mm": pcbnew.ToMM(item.GetWidth())})

    metrics = {net: {"total_copper_length_mm": round(length, 2), "widths_mm": sorted(widths[net])}
               for net, length in sorted(totals.items())}
    module_mismatches = []
    for reference, expected in COMMON_DOIT.items():
        if reference not in footprints:
            continue
        for pad in footprints[reference].Pads():
            number = int(pad.GetNumber())
            required = expected.get(number, "")
            if pad.GetNetname() != required:
                module_mismatches.append({"pad": f"{reference}.{number}",
                                          "board_net": pad.GetNetname(),
                                          "required_for_common_doit": required})
    release = json.loads((ROOT / "release-status.json").read_text(encoding="utf-8"))
    result = {"board": args.board.name, "kicad_version": pcbnew.GetBuildVersion(),
              "errors": errors, "checked_pad_count": len(pad_records),
              "fabrication_approved": release["fabrication_approved"],
              "release_status": release["status"],
              "common_doit_pinout_mismatches": module_mismatches,
              "checked_firmware_constants": len(PIN_CONSTANTS) + 6,
              "track_metrics": metrics, "pads": pad_records, "tracks": tracks,
              "vias": vias, "graphics": graphics,
              "limits": ["Pad assignments and firmware mapping only; run KiCad DRC separately.",
                         "No measured module dimensions, physical operation or signal-integrity measurement.",
                         "Ground connectivity is checked by filled-zone DRC; this export omits zone polygons."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"errors": errors, "checked_pad_count": len(pad_records),
                      "fabrication_approved": release["fabrication_approved"],
                      "release_status": release["status"],
                      "common_doit_pinout_mismatch_count": len(module_mismatches),
                      "checked_firmware_constants": result["checked_firmware_constants"],
                      "track_metrics": metrics}, indent=2))
    if errors:
        raise SystemExit(1)
    if module_mismatches or not release["fabrication_approved"]:
        raise SystemExit(2)  # An electrically consistent legacy map is still blocked.


if __name__ == "__main__":
    main()
