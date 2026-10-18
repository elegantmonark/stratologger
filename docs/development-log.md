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
- LED and buzzer boot diagnostics;
- an electrical BOM, netlist, and signal-level wiring diagram;
- a parametric two-part PETG enclosure; and
- host-side validation for CSV structure, sequence, timestamps, and checksums.

The firmware builds successfully for the PlatformIO `esp32dev` environment. This is
a software result only. No hardware operation, enclosure fit, battery endurance, or
mission test is claimed without a corresponding photograph, log, or measurement.

## Current direction

The next engineering stage is staged physical bring-up: bare ESP32 upload, I2C sensor
verification, shared-SPI display and SD verification, controls, then an extended USB
bench run. Perfboard transfer and enclosure fitting follow only after that configuration
is stable.

