# Stratologger SL-1 PCB

> **FABRICATION HOLD — 27 October 2026:** the existing ESP32 socket map does
> not match the common 30-pin DOIT DevKit V1. The exact module has not yet been
> confirmed. Do not order the existing Gerber ZIP. See [the audit](review/PCB_AUDIT.md).
> `release-status.json` blocks the fabrication script until the pin map and routing
> have been corrected and reviewed. The current board contains the new silkscreen logo.

SL-1 is a 90 by 70 mm, two-layer carrier board for the Stratologger payload. The
ESP32 and sensors remain replaceable, while the TFT and its onboard microSD socket
mount in the enclosure lid and connect through a short keyed harness.

## Board layout

- 30-pin ESP32 DevKit V1 on two 1x15 female sockets, with USB at the board edge.
- AHT20/BMP280 on a 1x4 male header ordered `VDD, SDA, GND, SCL`.
- GY-521 on a 1x8 female socket ordered `VCC, GND, SCL, SDA, XDA, XCL, AD0, INT`.
- Keyed 2x7 IDC connector for the lid-mounted TFT and onboard microSD socket.
- Header for the lid-mounted screen button and its required GPIO34 pull-up.
- Fused, Schottky-isolated regulated 5 V input and a separate battery-sense input.
- Ground planes on both copper layers and a copper keep-out below the ESP32 antenna.
- Four 3.2 mm non-plated mounting holes for M3 hardware.

The AHT20/BMP280 pin legend sits beside the header, outside the nominal breakout
outline, so the module should not cover it when plugged in. Check the exact module
overhang against the 1:1 board print.

The separate TF-card reader is not used. CSV logging uses the card socket already
fitted to the TFT module.

### ESP32 socket order

The following is the **legacy assumed map in the current file**, not a confirmed
DevKit V1 pinout. With USB facing the lower edge, both socket rows start at the
end opposite USB. The common DOIT module differs from this map:

| Socket | Pin order |
|---|---|
| Left (J1) | 3V3, EN, GPIO36, GPIO39, GPIO34, GPIO35, GPIO32, GPIO33, GPIO25, GPIO26, GPIO27, GPIO14, GPIO12, GND, VIN |
| Right (J2) | GND, GPIO23, GPIO22, GPIO1, GPIO3, GPIO21, GND, GPIO19, GPIO18, GPIO5, GPIO17, GPIO16, GPIO4, GPIO2, GPIO15 |

The intended GPIO functions match the firmware, but the socket positions below
must be corrected against the actual module before they can implement those functions.

## Electrical review

KiCad 10 reports:

- 0 DRC violations;
- 0 unconnected pads; and
- 0 footprint errors.

The historical report is in `manufacturing/Stratologger_SL1-drc.rpt`; the latest
logo-board report is in `review/logo-board-drc.rpt`. Passing DRC confirms
the routed board against the configured electrical rules; it does not prove that a
generic plug-in module has the same body dimensions as the one on hand.

## Required physical fit check

Do this before uploading the Gerber ZIP to a fabricator:

1. Print `Stratologger_SL1.kicad_pcb` from KiCad at exactly 1:1 scale.
2. Confirm the ESP32 has 30 pins and 25.4 mm between its two header rows.
3. Place the exact ESP32, AHT20/BMP280 and GY-521 over the print.
4. Check every pin-1 position, header order, module overhang and USB clearance.
5. Confirm the enclosure can accept the 90 by 70 mm outline and M3 hole centres.
6. Check the display harness pin map in `../../tft/README.md` with a multimeter.

If any module does not align, edit the source and regenerate the release package;
do not bend module pins to force a fit.

## Files

- `Stratologger_SL1.kicad_pcb`: editable routed KiCad board.
- `Stratologger_SL1.kicad_pro`: KiCad project settings.
- `generate_stratologger_pcb.py`: reproducible board generator.
- `manufacturing/`: Gerbers, drill files, DRC report, assembly BOM and order notes.
- `manufacturing/Stratologger_SL1-fabrication.zip`: file to upload after the fit check.

## Regenerating

The generator retains the unverified legacy map. Regenerating it does not resolve
the fabrication hold. Use `audit_board.py` to expose the module-map mismatch;
exit code 2 denotes the pending fabrication hold.

Run from this directory with KiCad 10 installed:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\generate_stratologger_pcb.py
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --refill-zones --output .\manufacturing\Stratologger_SL1-drc.rpt .\Stratologger_SL1.kicad_pcb
```

The fabrication defaults are 2 layers, 1.6 mm FR-4, 1 oz copper, lead-free HASL,
green solder mask and white silkscreen. No controlled impedance, castellations,
edge plating or via-in-pad process is required.
