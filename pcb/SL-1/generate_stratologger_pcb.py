"""Generate the routed Stratologger SL-1 motherboard in KiCad.

Run with KiCad's bundled Python interpreter so the pcbnew module and standard
footprint libraries are available. The generated board contains module sockets,
support circuitry, routed copper, ground planes, mechanical outlines and electrical
net assignments.

Author: Trishan Biswas
Project started: February 2026
Status: Ongoing
"""

from pathlib import Path
import json

import pcbnew


PROJECT_NAME = "Stratologger_SL1"
OUTPUT_DIR = Path(__file__).resolve().parent
BOARD_PATH = OUTPUT_DIR / f"{PROJECT_NAME}.kicad_pcb"
PROJECT_PATH = OUTPUT_DIR / f"{PROJECT_NAME}.kicad_pro"
KICAD_FOOTPRINT_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

MM = pcbnew.FromMM
BOARD_X = 20.0
BOARD_Y = 20.0
BOARD_W = 90.0
BOARD_H = 70.0


def point(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x_mm), MM(y_mm))


def add_line(board, start, end, layer=pcbnew.F_SilkS, width=0.2):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(start)
    shape.SetEnd(end)
    shape.SetLayer(layer)
    shape.SetWidth(MM(width))
    board.Add(shape)
    return shape


def add_rectangle(board, x1, y1, x2, y2, layer=pcbnew.F_SilkS, width=0.2):
    corners = [
        point(x1, y1),
        point(x2, y1),
        point(x2, y2),
        point(x1, y2),
    ]
    for index in range(4):
        add_line(board, corners[index], corners[(index + 1) % 4], layer, width)


def add_stratologger_logo(board):
    """Small balloon, telemetry pulse and horizon, drawn only on front silk."""
    # This patch of board is clear of pads and component bodies. The printed
    # logo has no copper, solder-mask opening, drill or electrical connection.
    circle = pcbnew.PCB_SHAPE(board)
    circle.SetShape(pcbnew.SHAPE_T_CIRCLE)
    circle.SetCenter(point(87.5, 71.0))
    circle.SetEnd(point(89.7, 71.0))
    circle.SetLayer(pcbnew.F_SilkS)
    circle.SetWidth(MM(0.22))
    board.Add(circle)
    for start, end in (
        ((85.9, 72.5), (86.8, 74.6)),
        ((89.1, 72.5), (88.2, 74.6)),
        ((86.8, 74.6), (88.2, 74.6)),
        ((88.2, 74.6), (88.2, 75.5)),
        ((88.2, 75.5), (86.8, 75.5)),
        ((86.8, 75.5), (86.8, 74.6)),
        ((87.5, 68.8), (87.5, 73.0)),
    ):
        add_line(board, point(*start), point(*end), width=0.22)
    pulse = ((80.0, 75.2), (81.4, 75.2), (82.0, 74.5), (82.7, 76.0),
             (83.5, 73.8), (84.3, 75.2), (85.5, 75.2))
    for start, end in zip(pulse, pulse[1:]):
        add_line(board, point(*start), point(*end), width=0.22)
    add_line(board, point(89.5, 75.2), point(94.5, 75.2), width=0.22)
    add_line(board, point(80.0, 77.0), point(94.5, 77.0), width=0.22)


def add_text(
    board,
    text,
    x_mm,
    y_mm,
    size=1.0,
    layer=pcbnew.F_SilkS,
    thickness=0.16,
    rotation=0,
):
    size = max(size, 0.8)
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(point(x_mm, y_mm))
    item.SetLayer(layer)
    item.SetTextSize(point(size, size))
    item.SetTextThickness(MM(thickness))
    item.SetTextAngle(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    board.Add(item)
    return item


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def load_footprint(
    board,
    library,
    name,
    reference,
    value,
    x_mm,
    y_mm,
    nets,
    rotation=0,
    reference_visible=True,
):
    library_path = KICAD_FOOTPRINT_ROOT / f"{library}.pretty"
    footprint = pcbnew.FootprintLoad(str(library_path), name)
    if footprint is None:
        raise RuntimeError(f"Could not load {library}:{name}")

    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(point(x_mm, y_mm))
    footprint.SetOrientationDegrees(rotation)
    board.Add(footprint)
    footprint.Reference().SetVisible(reference_visible)
    footprint.Value().SetVisible(False)

    for pad in footprint.Pads():
        number = str(pad.GetNumber())
        if number in nets and nets[number] is not None:
            pad.SetNet(nets[number])

    return footprint


def add_test_point(board, reference, label, x_mm, y_mm, net):
    footprint = load_footprint(
        board,
        "TestPoint",
        "TestPoint_THTPad_D2.0mm_Drill1.0mm",
        reference,
        label,
        x_mm,
        y_mm,
        {"1": net},
        reference_visible=False,
    )
    add_text(board, label, x_mm, y_mm - 2.0, 0.65, thickness=0.12)
    return footprint


def add_track(board, net, coordinates, layer=pcbnew.F_Cu, width=0.4):
    """Add a routed polyline to one copper layer."""
    for start, end in zip(coordinates, coordinates[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(point(*start))
        track.SetEnd(point(*end))
        track.SetLayer(layer)
        track.SetWidth(MM(width))
        track.SetNet(net)
        board.Add(track)


def add_via(board, net, x_mm, y_mm, diameter=0.8, drill=0.4):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x_mm, y_mm))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetWidth(MM(diameter))
    via.SetDrill(MM(drill))
    via.SetNet(net)
    board.Add(via)
    return via


def add_ground_zone(board, net, layer):
    """Add a ground plane inside the board edge."""
    coordinates = (
        (23.4, 20.4), (106.6, 20.4), (109.6, 23.4), (109.6, 86.6),
        (106.6, 89.6), (23.4, 89.6), (20.4, 86.6), (20.4, 23.4),
    )
    zone = board.AddArea(
        None,
        net.GetNetCode(),
        layer,
        point(*coordinates[0]),
        pcbnew.ZONE_BORDER_DISPLAY_STYLE_DIAGONAL_EDGE,
    )
    zone.SetNet(net)
    zone.SetLocalClearance(MM(0.25))
    zone.SetThermalReliefGap(MM(0.3))
    zone.SetThermalReliefSpokeWidth(MM(0.4))
    for coordinate in coordinates[1:]:
        zone.AppendCorner(point(*coordinate), -1)
    zone.Outline().Outline(0).SetClosed(True)
    return zone


def add_antenna_keepout(board, layer):
    """Keep both copper pours and routed copper below the ESP32 antenna."""
    coordinates = ((38.0, 20.4), (60.0, 20.4), (60.0, 35.5), (38.0, 35.5))
    zone = board.AddArea(
        None,
        0,
        layer,
        point(*coordinates[0]),
        pcbnew.ZONE_BORDER_DISPLAY_STYLE_DIAGONAL_EDGE,
    )
    zone.SetIsRuleArea(True)
    zone.SetDoNotAllowTracks(True)
    zone.SetDoNotAllowVias(True)
    zone.SetDoNotAllowZoneFills(True)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowFootprints(False)
    for coordinate in coordinates[1:]:
        zone.AppendCorner(point(*coordinate), -1)
    zone.Outline().Outline(0).SetClosed(True)
    return zone


def add_board_outline(board):
    # Chamfered corners are robust to manufacture and fit a compact enclosure.
    corners = [
        point(23, 20),
        point(107, 20),
        point(110, 23),
        point(110, 87),
        point(107, 90),
        point(23, 90),
        point(20, 87),
        point(20, 23),
    ]
    for index in range(len(corners)):
        add_line(
            board,
            corners[index],
            corners[(index + 1) % len(corners)],
            pcbnew.Edge_Cuts,
            0.2,
        )


def add_module_guides(board):
    # Common 30-pin ESP32 DevKit V1 envelope; verify the user's exact board.
    add_rectangle(board, 33.0, 24.0, 65.0, 78.5, pcbnew.Dwgs_User, 0.28)
    add_rectangle(board, 41.0, 73.5, 57.0, 81.0, pcbnew.Dwgs_User, 0.2)
    add_text(board, "USB ACCESS", 49.0, 76.5, 0.8)
    add_text(board, "ESP32 DEVKIT 30-PIN", 49.0, 26.5, 0.9)

    # Antenna region: keep metal, battery and enclosure fasteners away.
    add_rectangle(board, 33.0, 24.0, 65.0, 36.0, pcbnew.Dwgs_User, 0.25)
    add_text(board, "ANTENNA KEEP-OUT", 49.0, 29.8, 0.72)

    # Approximate module bodies, separate from the plated socket rows.
    add_rectangle(board, 70.5, 22.5, 94.0, 38.5, pcbnew.Dwgs_User, 0.2)
    add_text(board, "AHT20 + BMP280", 82.3, 37.0, 0.72)
    add_text(board, "VENT EDGE", 82.3, 21.5, 0.65)

    add_rectangle(board, 69.5, 41.0, 94.5, 59.0, pcbnew.Dwgs_User, 0.2)
    add_text(board, "MPU6050 GY-521", 82.0, 57.5, 0.72)
    add_text(board, "+X ->", 89.0, 53.0, 0.65)
    add_text(board, "+Y ^", 82.0, 40.0, 0.65)


def write_project_file():
    project = {
        "board": {},
        "boards": [],
        "cvpcb": {},
        "erc": {},
        "libraries": {},
        "meta": {"filename": PROJECT_PATH.name, "version": 1},
        "net_settings": {},
        "pcbnew": {},
        "schematic": {},
        "text_variables": {},
    }
    PROJECT_PATH.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")


def main():
    board = pcbnew.BOARD()
    design_settings = board.GetDesignSettings()
    design_settings.SetBoardThickness(MM(1.6))
    design_settings.m_MinSilkTextHeight = MM(0.6)
    design_settings.m_MinSilkTextThickness = MM(0.1)

    title = board.GetTitleBlock()
    title.SetTitle("Stratologger SL-1 modular payload motherboard")
    title.SetDate("2026-10-24")
    title.SetCompany("Trishan Biswas")
    title.SetComment(0, "90 x 70 mm two-layer routed motherboard")
    title.SetComment(1, "Socketed modules and lid-mounted TFT/SD connection")
    title.SetComment(2, "Verify plug-in module fit at 1:1 scale before ordering")

    net_names = (
        "+5V_EXT",
        "+5V_FUSED",
        "VIN_5V",
        "+3V3",
        "GND",
        "I2C_SDA",
        "I2C_SCL",
        "SPI_SCK",
        "SPI_MOSI",
        "SPI_MISO",
        "TFT_CS",
        "TFT_DC",
        "TFT_RST",
        "SD_CS",
        "SCREEN_BUTTON",
        "BAT_RAW",
        "BATTERY_SENSE",
    )
    nets = {name: add_net(board, name) for name in net_names}

    add_board_outline(board)
    add_module_guides(board)

    # LEGACY UNVERIFIED SOCKET MAP: this does not match the common 30-pin DOIT
    # pin order. Confirm the actual module and reroute before fabrication.
    load_footprint(
        board,
        "Connector_PinSocket_2.54mm",
        "PinSocket_1x15_P2.54mm_Vertical",
        "J1",
        "ESP32_LEFT",
        36.3,
        31.5,
        {
            "1": nets["+3V3"],          # 3V3
            "5": nets["SCREEN_BUTTON"], # GPIO34
            "6": nets["BATTERY_SENSE"], # GPIO35
            "14": nets["GND"],
            "15": nets["VIN_5V"],
        },
    )
    load_footprint(
        board,
        "Connector_PinSocket_2.54mm",
        "PinSocket_1x15_P2.54mm_Vertical",
        "J2",
        "ESP32_RIGHT",
        61.7,
        31.5,
        {
            "1": nets["GND"],
            "2": nets["SPI_MOSI"],       # GPIO23
            "3": nets["I2C_SCL"],        # GPIO22
            "6": nets["I2C_SDA"],        # GPIO21
            "7": nets["GND"],
            "8": nets["SPI_MISO"],       # GPIO19
            "9": nets["SPI_SCK"],        # GPIO18
            "10": nets["SD_CS"],         # GPIO5
            "13": nets["TFT_RST"],       # GPIO4
            "14": nets["TFT_DC"],        # GPIO2
            "15": nets["TFT_CS"],        # GPIO15
        },
    )

    # Environmental sensor male header, ordered top-to-bottom as marked on the module.
    load_footprint(
        board,
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x04_P2.54mm_Vertical",
        "J3",
        "AHT20_BMP280",
        78.0,
        25.5,
        {
            "1": nets["+3V3"],
            "2": nets["I2C_SDA"],
            "3": nets["GND"],
            "4": nets["I2C_SCL"],
        },
    )
    # Keep the pin legend outside the breakout's assumed body outline so it
    # remains readable after the module is plugged onto the male header.
    for label, y_mm in (("VDD", 25.5), ("SDA", 28.04), ("GND", 30.58), ("SCL", 33.12)):
        add_text(board, label, 66.0, y_mm, 0.8)

    # Inertial sensor socket.
    load_footprint(
        board,
        "Connector_PinSocket_2.54mm",
        "PinSocket_1x08_P2.54mm_Vertical",
        "J4",
        "MPU6050_GY521",
        72.0,
        43.0,
        {
            "1": nets["+3V3"],
            "2": nets["GND"],
            "3": nets["I2C_SCL"],
            "4": nets["I2C_SDA"],
        },
        rotation=90,
    )

    # Keyed ribbon cable to the lid-mounted TFT and its onboard SD socket.
    # Ground conductors sit between the three high-speed SPI signals.
    load_footprint(
        board,
        "Connector_IDC",
        "IDC-Header_2x07_P2.54mm_Vertical",
        "J5",
        "REMOTE_TFT_SD",
        97.0,
        42.0,
        {
            "1": nets["+3V3"],
            "2": nets["GND"],
            "3": nets["SPI_MOSI"],
            "4": nets["GND"],
            "5": nets["SPI_MISO"],
            "6": nets["GND"],
            "7": nets["SPI_SCK"],
            "8": nets["GND"],
            "9": nets["SD_CS"],
            "10": nets["TFT_RST"],
            "11": nets["TFT_DC"],
            "12": nets["+3V3"],
            "13": nets["TFT_CS"],
            "14": nets["GND"],
        },
    )
    add_text(board, "TFT + SD", 108.0, 50.0, 0.72, rotation=90)
    add_text(board, "2x7 IDC", 106.0, 62.0, 0.65, rotation=90)
    add_text(board, "PIN 1", 93.0, 40.3, 0.65)

    # The enclosure-mounted screen-selection button connects here.
    load_footprint(
        board,
        "Connector_PinHeader_2.54mm",
        "PinHeader_1x02_P2.54mm_Vertical",
        "J6",
        "REMOTE_BUTTON",
        101.0,
        31.0,
        {"1": nets["SCREEN_BUTTON"], "2": nets["GND"]},
        rotation=90,
    )
    load_footprint(
        board,
        "Resistor_SMD",
        "R_0805_2012Metric",
        "R2",
        "10k BUTTON PULLUP",
        90.0,
        28.0,
        {"1": nets["+3V3"], "2": nets["SCREEN_BUTTON"]},
        rotation=90,
        reference_visible=False,
    )

    # The Schottky blocks reverse current toward the external 5 V input.
    # USB/external source isolation also depends on the exact DevKit circuitry.
    load_footprint(
        board,
        "Connector_JST",
        "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
        "J7",
        "REGULATED_5V_IN",
        34.5,
        85.0,
        {"1": nets["+5V_EXT"], "2": nets["GND"]},
        rotation=180,
        reference_visible=False,
    )
    load_footprint(
        board,
        "Fuse",
        "Fuse_1812_4532Metric",
        "F1",
        "0.75A PTC",
        40.5,
        84.0,
        {"1": nets["+5V_EXT"], "2": nets["+5V_FUSED"]},
    )
    load_footprint(
        board,
        "Diode_SMD",
        "D_SMA",
        "D1",
        "SS34",
        47.5,
        84.0,
        {"1": nets["VIN_5V"], "2": nets["+5V_FUSED"]},
        rotation=180,
    )
    add_text(board, "5V POWER", 34.5, 89.0, 0.68)

    # Separate protected-cell sense input; this connector does not power the PCB.
    load_footprint(
        board,
        "Connector_JST",
        "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
        "J8",
        "BATTERY_SENSE_ONLY",
        57.0,
        85.0,
        {"1": nets["BAT_RAW"], "2": nets["GND"]},
        rotation=180,
        reference_visible=False,
    )
    load_footprint(
        board,
        "Resistor_SMD",
        "R_0805_2012Metric",
        "R3",
        "100k 1%",
        64.0,
        83.0,
        {"1": nets["BAT_RAW"], "2": nets["BATTERY_SENSE"]},
    )
    load_footprint(
        board,
        "Resistor_SMD",
        "R_0805_2012Metric",
        "R4",
        "100k 1%",
        70.0,
        83.0,
        {"1": nets["BATTERY_SENSE"], "2": nets["GND"]},
    )
    load_footprint(
        board,
        "Capacitor_SMD",
        "C_0805_2012Metric",
        "C1",
        "100nF",
        70.0,
        87.0,
        {"1": nets["BATTERY_SENSE"], "2": nets["GND"]},
    )
    add_text(board, "BAT SENSE", 57.0, 89.0, 0.65)

    # Local supply stabilization and optional bus pull-ups.
    load_footprint(
        board,
        "Capacitor_THT",
        "CP_Radial_D6.3mm_P2.50mm",
        "C2",
        "100uF 6.3V",
        80.0,
        82.0,
        {"1": nets["+3V3"], "2": nets["GND"]},
        rotation=90,
    )
    for reference, x_mm, y_mm in (("C3", 84.0, 30.5),):
        load_footprint(
            board,
            "Capacitor_SMD",
            "C_0805_2012Metric",
            reference,
            "100nF",
            x_mm,
            y_mm,
            {"1": nets["+3V3"], "2": nets["GND"]},
            rotation=90,
            reference_visible=False,
        )

    # Four non-plated mechanical holes for the enclosure standoffs.
    for reference, x_mm, y_mm in (
        ("H1", 24.5, 24.5),
        ("H2", 105.5, 24.5),
        ("H3", 24.5, 85.5),
        ("H4", 105.5, 85.5),
    ):
        load_footprint(
            board,
            "MountingHole",
            "MountingHole_3.2mm_M3",
            reference,
            "M3",
            x_mm,
            y_mm,
            {},
            reference_visible=False,
        )

    # Permanent board markings.
    add_text(board, "STRATOLOGGER", 91.0, 84.5, 1.35, thickness=0.24)
    add_text(board, "SL-1  |  2026", 91.0, 87.0, 0.78)
    add_text(board, "TRISHAN BISWAS", 96.0, 22.0, 0.65)
    add_stratologger_logo(board)

    # Protected 5 V input and isolated ESP32 VIN rail.
    add_track(board, nets["+5V_EXT"], [(34.5, 85.0), (36.0, 84.0), (38.36, 84.0)], width=1.0)
    add_track(board, nets["+5V_FUSED"], [(42.64, 84.0), (45.5, 84.0)], width=1.0)
    add_track(
        board,
        nets["VIN_5V"],
        [(49.5, 84.0), (49.5, 79.0), (40.0, 74.0), (36.3, 70.0), (36.3, 67.06)],
        width=1.0,
    )

    # Battery measurement divider and ADC filter.
    add_track(board, nets["BAT_RAW"], [(57.0, 85.0), (59.0, 83.0), (63.09, 83.0)], width=0.5)
    add_track(
        board,
        nets["BATTERY_SENSE"],
        [(64.91, 83.0), (66.0, 80.0)],
        width=0.4,
    )
    add_via(board, nets["BATTERY_SENSE"], 66.0, 80.0)
    add_track(
        board,
        nets["BATTERY_SENSE"],
        [(66.0, 80.0), (31.0, 80.0), (31.0, 44.2), (36.3, 44.2)],
        pcbnew.B_Cu,
        0.4,
    )
    add_track(board, nets["BATTERY_SENSE"], [(64.91, 83.0), (69.09, 83.0)], width=0.4)
    add_track(board, nets["BATTERY_SENSE"], [(64.91, 83.0), (66.5, 87.0), (69.05, 87.0)], width=0.4)

    # I2C branches to both removable sensors.
    add_track(
        board,
        nets["I2C_SCL"],
        [(61.7, 36.58), (66.0, 36.58), (70.0, 36.0), (74.0, 36.0), (78.0, 33.12)],
    )
    add_track(board, nets["I2C_SCL"], [(74.0, 36.0), (76.0, 39.0), (77.08, 43.0)])
    add_track(
        board,
        nets["I2C_SDA"],
        [(61.7, 44.2), (66.0, 44.2), (70.0, 46.0), (79.62, 46.0), (79.62, 43.0)],
    )
    add_track(board, nets["I2C_SDA"], [(79.62, 43.0), (82.0, 40.0), (82.0, 28.04), (78.0, 28.04)])

    # Display data lines. SCK and control lines use the bottom layer where needed
    # to avoid crossings; the connector's intervening grounds limit crosstalk.
    add_track(
        board,
        nets["SPI_SCK"],
        [(61.7, 51.82), (66.0, 51.82), (70.0, 53.0), (90.0, 49.62), (97.0, 49.62)],
        pcbnew.B_Cu,
    )
    add_track(
        board,
        nets["SPI_MOSI"],
        [(61.7, 34.04), (65.0, 34.04), (65.0, 23.0), (92.0, 23.0), (94.0, 27.0), (94.0, 44.54), (97.0, 44.54)],
    )
    add_track(
        board,
        nets["SPI_MISO"],
        [(61.7, 49.28), (66.0, 49.28), (70.0, 47.0), (88.0, 47.08), (97.0, 47.08)],
    )
    add_track(
        board,
        nets["SD_CS"],
        [(61.7, 54.36), (66.0, 56.0), (88.0, 52.16), (97.0, 52.16)],
    )
    add_track(
        board,
        nets["TFT_RST"],
        [(61.7, 61.98), (70.0, 62.0), (90.0, 60.0), (104.0, 60.0), (104.0, 52.16), (99.54, 52.16)],
    )
    add_track(
        board,
        nets["TFT_DC"],
        [(61.7, 64.52), (70.0, 64.52), (90.0, 56.0), (97.0, 54.7)],
        pcbnew.B_Cu,
    )
    add_track(
        board,
        nets["TFT_CS"],
        [(61.7, 67.06), (68.0, 69.0), (82.0, 69.0), (92.0, 60.0), (97.0, 57.24)],
        pcbnew.B_Cu,
    )

    # GPIO34 has no internal pull-up. The long button run stays at the perimeter.
    add_track(
        board,
        nets["SCREEN_BUTTON"],
        [(36.3, 41.66), (27.0, 41.66), (27.0, 74.0), (33.0, 74.0)],
        pcbnew.F_Cu,
        0.3,
    )
    add_via(board, nets["SCREEN_BUTTON"], 33.0, 74.0)
    add_track(board, nets["SCREEN_BUTTON"], [(33.0, 74.0), (104.0, 74.0)], pcbnew.B_Cu, 0.3)
    add_via(board, nets["SCREEN_BUTTON"], 104.0, 74.0)
    add_track(board, nets["SCREEN_BUTTON"], [(104.0, 74.0), (106.0, 74.0), (106.0, 34.0)], width=0.3)
    add_via(board, nets["SCREEN_BUTTON"], 106.0, 34.0)
    add_track(board, nets["SCREEN_BUTTON"], [(106.0, 34.0), (101.0, 34.0), (101.0, 31.0)], pcbnew.B_Cu, 0.3)
    add_track(board, nets["SCREEN_BUTTON"], [(101.0, 31.0), (101.0, 27.0), (88.0, 27.09)], pcbnew.B_Cu, 0.3)
    add_via(board, nets["SCREEN_BUTTON"], 88.0, 27.09)
    add_track(board, nets["SCREEN_BUTTON"], [(88.0, 27.09), (90.0, 27.09)], width=0.3)

    # 3.3 V distribution starts at the DevKit's pin 1, outside the antenna keep-out.
    add_track(board, nets["+3V3"], [(36.3, 31.5), (22.0, 34.0), (22.0, 82.0), (80.0, 82.0)], pcbnew.B_Cu, 0.8)
    add_track(
        board,
        nets["+3V3"],
        [(80.0, 82.0), (92.0, 80.0), (108.0, 74.0), (108.0, 40.0), (100.0, 38.0), (97.0, 42.0)],
        pcbnew.B_Cu,
        0.8,
    )
    add_track(board, nets["+3V3"], [(100.0, 38.0), (85.0, 38.0), (85.0, 25.5), (78.0, 25.5)], pcbnew.B_Cu, 0.8)
    add_track(board, nets["+3V3"], [(85.0, 38.0), (72.0, 38.0), (72.0, 43.0)], pcbnew.B_Cu, 0.8)
    add_track(board, nets["+3V3"], [(78.0, 25.5), (86.0, 24.0), (86.0, 33.0), (84.0, 33.0)], pcbnew.B_Cu, 0.6)
    add_via(board, nets["+3V3"], 84.0, 33.0)
    add_track(board, nets["+3V3"], [(84.0, 33.0), (84.0, 31.45)], width=0.6)
    add_track(board, nets["+3V3"], [(84.0, 31.45), (86.0, 33.0), (90.0, 28.91)], width=0.6)
    add_track(board, nets["+3V3"], [(108.0, 74.0), (105.0, 66.0), (105.0, 54.7), (99.54, 54.7)], pcbnew.B_Cu, 0.8)

    add_ground_zone(board, nets["GND"], pcbnew.F_Cu)
    add_ground_zone(board, nets["GND"], pcbnew.B_Cu)
    add_antenna_keepout(board, pcbnew.F_Cu)
    add_antenna_keepout(board, pcbnew.B_Cu)

    pcbnew.SaveBoard(str(BOARD_PATH), board)
    write_project_file()
    print(BOARD_PATH)
    print(PROJECT_PATH)


if __name__ == "__main__":
    main()
