# Electrical integration

**Fabrication hold:** the ESP32 socket map below is the legacy assumption, now
known to differ from the common 30-pin DOIT module. Confirm the actual board before
rerouting. Do not fabricate or power this carrier on the basis of these socket labels.
See [the audit](../pcb/SL-1/review/PCB_AUDIT.md).

The permanent electrical assembly is based on the custom motherboard in
[`pcb/SL-1/`](../pcb/SL-1/README.md). The ESP32 and sensor boards plug into female
headers so a failed module can be replaced without discarding the motherboard.

## Board architecture

| Area | Implementation |
|---|---|
| Controller | Socketed 30-pin ESP32 DevKit V1 with USB access at the enclosure edge |
| Environmental sensing | AHT20/BMP280 on a 1x4 male header at the ventilated edge |
| Inertial sensing | Socketed GY-521 near the payload's mechanical centre with axes marked |
| Display and storage | Lid-mounted ST7789V/microSD assembly connected through a keyed 2x7 harness |
| User interface | Enclosure-mounted screen button connected through a two-pin header |
| Power | USB through the ESP32 or protected regulated 5 V through a fused, diode-isolated input |
| Battery measurement | Separate protected-cell sense input and 100 kOhm / 100 kOhm ADC divider |
| Service access | Socketed modules and labelled connectors remain directly probeable |

The SL-1 outline is 90 by 70 mm with four 3.2 mm mounting holes. The
environmental sensor and ESP32 antenna areas are kept clear for the enclosure vent
and radio path respectively.

The present J1/J2 assignments are a legacy map and do not match the common 30-pin
DOIT DevKit V1. Do not fabricate or power this board until the exact ESP32 pin order
is confirmed and the socket map and routing are corrected. The 25.4 mm socket-row
pitch and approximate 32 mm body guide do not confirm fit; measure the exact board,
including body width, header offsets, USB connector and antenna edge.

## Remote TFT connection

The keyed 2x7 motherboard connector carries:

| Pin | Signal | Pin | Signal |
|---:|---|---:|---|
| 1 | 3.3 V / TFT VCC | 2 | GND |
| 3 | SPI MOSI | 4 | GND |
| 5 | SPI MISO | 6 | GND |
| 7 | SPI SCK | 8 | GND |
| 9 | SD CS | 10 | TFT RST |
| 11 | TFT DC | 12 | 3.3 V / backlight |
| 13 | TFT CS | 14 | GND |

Fourteen-pin ST7789 boards do not use a universal header order. The display harness
must therefore be mapped from these signal names to the exact silk labels on the
module. TFT and SD share SCK, MOSI and MISO, while their chip-select lines stay
separate. Keep the harness no longer than 100 mm; the interleaved ground conductors
are part of the design, not spare wires.

On the current display, the first five male pins (`T_IRQ`, `T_DO`, `T_DIN`, `T_CS`
and `T_CLK`) are unused touch signals. The remaining display pins connect by signal
name. The four female `SD_*` pins expose the TFT board's built-in card socket and can
receive the shared SPI lines plus GPIO5 for `SD_CS`.

The standalone TF-card reader is not fitted on SL-1. Use the TFT board's built-in
socket for logging.

## Power boundaries

The motherboard accepts **regulated 5 V only** at its external power connector. A
resettable fuse limits input faults and the Schottky diode blocks reverse current
toward the external supply. This does not establish USB power-source isolation on
an unknown DevKit clone. Use only one power source at a time until the exact
DevKit power schematic is verified. Raw Li-ion or LiPo voltage is not a motherboard power input.

J7 (`5V POWER`) is a two-wire input: regulated `+5 V` and `GND`. F1 is a 750 mA
resettable PTC fuse in series with that input; it trips under sustained overload and
recovers after the fault is removed. It is not a switch or charger. Use a matching
JST-XH 2-pin pigtail or soldered, strain-relieved 22–24 AWG wires. The board uses a
JST-XH footprint, so a Dupont jumper does not mate with it reliably.

J8 (`BAT SENSE`) is a separate, measurement-only two-wire input: protected single-cell
`BAT+` and `GND`. The 100 kOhm / 100 kOhm divider feeds GPIO35 at half the cell
voltage. It supports a 1-cell Li-ion/LiPo pack (about 3.2–4.2 V), not a 2-cell pack.
It does not power the payload. Power the payload from a regulated 5 V boost converter
connected to J7; connect the cell to J8 for voltage measurement. Use a second JST-XH
pigtail or soldered, strain-relieved pair and observe polarity. Grounds are common on
the PCB, but keep each connector's pair together in the wiring.

## Before ordering

Print the board at 1:1 scale from KiCad and place the exact ESP32, AHT20/BMP280 and
GY-521 modules over it. Confirm row spacing, header order, body overhang, USB access
and installed height. The routed board passes KiCad DRC, but generic breakout-board
dimensions are not controlled by SL-1 and still require this physical fit check.
