# SL-1 audit — 27 October 2026

## Decision: hold fabrication

The current file has internally consistent routing, but it is not ready to order.
Its J1/J2 socket assignments differ from the common 30-pin DOIT DevKit V1. The
exact physical module remains unverified. Do not substitute the 38-pin
Espressif DevKitC header table for a 30-pin board.

The original board passes filled-zone KiCad 10.0.1 DRC with zero violations and
zero unconnected items. The independent pad audit checks 78 pads and 15 firmware
constants. Its legacy-interface comparison passes; its common-DOIT comparison
does not. Exit code 2 is an intentional fabrication hold, not a passing release.

## Socket mismatch

Pin numbers here start at the antenna end on each socket, viewing the component
side with USB at the bottom. These are physical socket positions, not GPIO numbers.

| Connection | Current PCB assumption | Common 30-pin DOIT position |
|---|---|---|
| 3.3 V rail | J1.1 | J2.15 |
| Button GPIO34 | J1.5 | J1.4 |
| Battery ADC GPIO35 | J1.6 | J1.5 |
| SPI MOSI GPIO23 | J2.2 | J2.1 |
| I2C SCL GPIO22 | J2.3 | J2.2 |
| I2C SDA GPIO21 | J2.6 | J2.5 |
| SPI MISO GPIO19 | J2.8 | J2.6 |
| SPI SCK GPIO18 | J2.9 | J2.7 |
| SD CS GPIO5 | J2.10 | J2.8 |
| TFT reset GPIO4 | J2.13 | J2.11 |
| TFT DC GPIO2 | J2.14 | J2.12 |
| TFT CS GPIO15 | J2.15 | J2.13 |

In particular, on the common module J1.1 is EN and J2.1 is GPIO23. The current
carrier places its +3V3 net on EN and a ground net on GPIO23. It also connects
TFT_DC to the common module's J2.14 ground position and TFT_CS to its J2.15 3V3
position. This can load or ground outputs and does not power peripherals correctly.

This comparison is a reference for identifying the error. It does not identify the
actual board. Confirm its labels and row spacing directly before correcting the
footprint and releasing manufacturing data.

## Routing appearance and electrical review

The red and blue lines in the routing preview are traces on different copper layers.
Crossings on different layers are allowed without a via. A DRC-clean path can still
connect to the wrong physical module pin.

| Net | Total routed copper length | Review |
|---|---:|---|
| SCREEN_BUTTON | 187.64 mm | Avoidable perimeter detour; shorten during socket correction |
| +3V3 | 303.76 mm across all branches | Long distribution path; improve placement and supply delivery |
| SPI_MOSI | 66.35 mm | Longest SPI data path; inspect with complete lid harness |
| SPI_SCK | 35.75 mm | No DRC error; 20 MHz display still requires bench checks |
| BATTERY_SENSE | 90.33 mm across branches | Long analogue trace; bring filter/divider closer to ADC if practical |

Lengths are summed copper segments, not propagation simulations or measured
end-to-end lengths for branched nets. The traces use nonuniform angles, which are
visually awkward but are not automatically an electrical fault at these interfaces.
The corrected design should use shorter paths and consistent 45-degree bends.

Other checks still required:

- Measure ESP32 row spacing; 25.4 mm is an assumption in this file.
- Confirm each breakout's orientation and pin order, including J3 and J4.
- Check the actual GY-521 supply path; its regulator may affect operation at 3.3 V input.
- Measure 3.3 V at the TFT/SD during writes; the DevKit regulator also powers these loads.
- Check TFT VCC and LED input requirements and whether either needs extra regulation
  or backlight current limiting on the actual module.
- Confirm the unused touch controller does not drive shared MISO. Check both TFT
  and SD deselect behaviour; add a touch-CS pull-up if the fitted controller requires it.
- Inspect boot/download behaviour with GPIO2/5/15 attached; these include ESP32 strapping pins.
- D1's cathode is assigned to VIN_5V, anode to +5V_FUSED, as intended. It blocks
  reverse current to J7 but does not independently guarantee isolation from USB.
- Inspect enclosure USB access: the current DevKit body/cable drawings are nominal.
- Check local bypass/bulk capacitance at the display connector and ground return
  paths when rerouting; DRC does not measure transient voltage or signal ringing.

## Logo

A small balloon, telemetry pulse and horizon icon was added in native KiCad front
silkscreen beside the existing STRATOLOGGER wordmark. Minimum stroke is 0.22 mm.
It changes no copper, drill or solder-mask geometry. The unchanged original board
is preserved as `original-before-logo.kicad_pcb`. See [the preview](logo-board.png).
The existing manufacturing ZIP predates the logo and remains on hold.

## Required design corrections

1. Confirm both complete ESP32 header rows and measure row spacing.
2. Create/review a proper socket schematic with those exact physical pins.
3. Correct the socket mapping and audit expectations, then reroute power and signals.
4. Review board/module clearances at 1:1 scale; rerun pad audit and filled-zone DRC.
5. Release new Gerbers only after the hold is resolved. Assemble one PCB and test
   rails, boot, sensors, TFT, SD and logging before claiming hardware operation.

## References

- [Espressif DevKitC header and power guidance](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html): a different board format, not a 30-pin socket definition.
- [Joy-IT NodeMCU ESP32 manufacturer manual](https://joy-it.net/files/files/Produkte/SBC-NodeMCU-ESP32/SBC-NodeMCU-ESP32-Manual-2021-06-29.pdf): an example of a module-specific pinout that must be checked against the fitted hardware.
- [Espressif schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html): strapping pins and ADC guidance.
