# PETG enclosure

`enclosure.scad` generates a vented base and display lid. It is a parametric first-fit
model because generic ESP32 DevKit V1, combo-sensor and 14-pin ST7789 boards do not
share guaranteed dimensions or mounting-hole locations.

## Measure before final export

Update the parameter block for:

- perfboard outline, hole inset and installed component height;
- active TFT viewing area and the module's four mounting-hole centres;
- USB connector centre/height with the ESP32 installed on headers;
- button bushing diameter and power-switch body;
- battery holder envelope and wire bend radius.

Open the file in OpenSCAD, set `part` to `"base"` or `"lid"`, render with F6, and
export STL. `"print_both"` places both parts on the bed for inspection.

## PETG starting profile

- 0.20 mm layers, 4 perimeters, 5 top/bottom layers, 25–35% infill.
- Print the base open-side up and the lid exterior-side up as generated.
- Use a brim if the lid corners lift. Tune temperatures to the filament vendor.
- Drill/ream screw and button holes to final fit; printed holes usually close up.
- Use washers or heat-set inserts rather than repeatedly threading PETG directly.

The left-side vents are for the environmental sensor. Do not pot or foam over that
area. A hydrophobic membrane can reduce splash/dust exposure but adds sensor lag.
Keep the battery restrained by a proper holder plus a nonconductive strap or foam
preload. The model's small blocks are location stops, not crashworthy retention.

Print a 3–5 mm high draft or just the lid first to verify connectors, TFT window and
holes before committing to the full enclosure. PETG is tougher than PLA but the
assembly still needs a controlled drop-test progression.

