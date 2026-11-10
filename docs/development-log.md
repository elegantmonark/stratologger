# Development log

This record separates completed design work from physical results that still require
evidence.

## February 2026: project start

The project began as an ESP32 telemetry payload combining environmental sensing,
inertial measurement, removable storage, a local mission display, and a protective
enclosure. The initial architecture separated the electrical, display, mechanical,
and software work so that each subsystem could be replaced or tested independently.

## October 2026: repository baseline

The first repository baseline established:

- a fixed pin map for the shared I2C and VSPI buses;
- sensor acquisition for the AHT20, BMP280, and MPU6050;
- 500 ms CSV logging with non-overwriting filenames and per-row checksums;
- three display screens for live telemetry, IMU detail, and system status;
- TFT and serial boot-fault reporting;
- an electrical BOM, netlist, and signal-level wiring diagram;
- a parametric two-part PETG enclosure; and
- host-side validation for CSV structure, sequence, timestamps, and checksums.

The firmware builds successfully for the PlatformIO `esp32dev` environment. This is
a software result only. No hardware operation, enclosure fit, battery endurance, or
mission test is claimed without a corresponding photograph, log, or measurement.

## Current direction

The breadboard and perfboard stages were replaced by a custom motherboard. SL-1 uses
socketed modules, a keyed 2x7 TFT/SD harness, protected regulated-power input, battery
sensing and four M3 mounting holes within a 90 by 70 mm outline.

SL-1 is routed with two ground planes and an ESP32 antenna keep-out. KiCad reports
zero DRC violations, zero unconnected pads and zero footprint errors. Gerber and drill
files exist as historical outputs. Fabrication is blocked by the ESP32 socket-map
mismatch recorded in the [PCB audit](../pcb/SL-1/review/PCB_AUDIT.md). Confirm the
exact module pinout and dimensions, correct the mapping and routing, then regenerate
and review the manufacturing package. Hardware operation requires assembly and bench testing.

