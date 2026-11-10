# SL-1 manufacturing and ordering

> **DO NOT ORDER THIS REVISION.** The existing ZIP and Gerbers predate the
> 27 October 2026 pinout audit and the new logo. They are retained as historical
> outputs. The ESP32 socket map must be confirmed and corrected before a new
> fabrication package is released. See [the audit](../review/PCB_AUDIT.md).

`Stratologger_SL1-fabrication.zip` is the bare-board upload package. It contains only
Gerber and Excellon drill data. Do not upload the KiCad source or the full repository
to the board manufacturer's order form.

## Mandatory check before purchase

The electrical design is routed and DRC-clean, but ESP32 and sensor breakout boards
are sold in several physical layouts. Print the KiCad board at 1:1 and place the exact
modules on the paper. Confirm all header positions, pin 1, board overhangs and USB
clearance before spending money. A DRC result cannot detect a differently sized
third-party module.

## Recommended first order

Use a small bare-board batch and hand-assemble the first unit.

| Order field | SL-1 selection |
|---|---|
| Quantity | 5 boards |
| Board size | 90 x 70 mm; verify the site detects this |
| Layers | 2 |
| Material | FR-4 |
| Thickness | 1.6 mm |
| Copper weight | 1 oz |
| Solder mask | Green |
| Silkscreen | White |
| Surface finish | Lead-free HASL |
| Minimum rules | Manufacturer standard |
| Via treatment | Tented |
| Impedance control | No |
| Gold fingers | No |
| Castellated holes | No |
| Edge plating | No |
| Panelisation | Single board; let the factory panelise |
| Stencil | No for the first hand-built unit |
| Assembly service | No for the first order |

The board uses ordinary dimensions and processes; paying for tighter trace rules,
controlled impedance or exotic finish does not improve this design. ENIG is an
optional appearance/storage upgrade, not an electrical requirement.

## Ordering steps

1. Complete the physical fit check in `../README.md`.
2. Open a PCB quotation page. JLCPCB is a sensible low-volume default; PCBWay is a
   useful comparison if shipping is better to your address.
3. Upload `Stratologger_SL1-fabrication.zip`.
4. Confirm the detected outline is one chamfered 90 x 70 mm board with two copper
   layers and four non-plated M3 holes.
5. Apply the settings in the table above.
6. Open the manufacturer's Gerber viewer. Inspect both copper layers, both masks,
   top silkscreen, the outline and the two drill files.
7. Check that there is no copper under the ESP32 antenna rectangle and that J5 pin 1
   is marked.
8. Decline PCB assembly and a stencil for the first batch. The plug-in modules and
   through-hole sockets make manual assembly more practical.
9. Compare the complete checkout price and delivery estimate, not only the headline
   board price. Choose tracked shipping if the schedule matters.
10. Save the order preview and wait for the manufacturer's file review before treating
    the board as in production.

Current ordering references:

- [JLCPCB ordering guide](https://jlcpcb.com/help/article/how-do-i-place-an-order)
- [JLCPCB Gerber preparation](https://jlcpcb.com/help/article/gerber-files-preparation)
- [PCBWay layer guidance](https://www.pcbway.com/helpcenter/layers_issues/Please_clarify_1_layer_or_2_layer.html)

## Parts purchase

Order the PCB first only after the module fit check. Buy the parts in
`assembly-bom.csv` from a traceable electronics supplier where practical. Buy the
exact 30-pin ESP32, GY-521 and AHT20/BMP280 boards used for the paper check; visually
similar listings can have different dimensions or pin orders.

The TFT harness is custom. Its motherboard end uses one 2x7 female IDC socket. At the
lid, use a 1x14 female housing for the TFT male header and a 1x4 male plug for the SD
header. Keep it at or below 100 mm, splice the shared SPI and ground conductors only at
the TFT end, and continuity-test every pin before applying power.

## Incoming-board inspection

Before soldering, inspect one board for shorts, damaged plating, broken outline tabs,
silkscreen legibility and hole size. Check resistance between 3.3 V and GND, then
between VIN and GND. Assemble the low-profile SMD parts first, followed by the fuse,
diode, connectors and module sockets. Power the empty board from a current-limited
5 V supply before installing the ESP32 or sensors.
