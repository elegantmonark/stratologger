# Limitations

## Physical validation is pending

The source code, wiring documents, and enclosure model do not by themselves prove that
the assembled payload works. The current revision has no published breadboard photo,
perfboard photo, physical enclosure fit, or sensor capture.

## Barometric altitude requires calibration

BMP280 altitude is calculated from atmospheric pressure and a configured sea-level
reference. Weather changes and an incorrect reference pressure can shift the reported
altitude. Relative changes are generally more useful than an uncalibrated absolute
value.

## Attitude is gravity-derived

Roll and pitch use the accelerometer only. Bicycle vibration, impact, or other linear
acceleration changes the apparent gravity vector and temporarily distorts the displayed
attitude. The present firmware does not implement a fused attitude filter.

## The mission log is low-rate

The 500 ms interval provides two samples per second. It is appropriate for environmental
and slow altitude changes but cannot support a vibration spectrum above 1 Hz. A separate
high-rate IMU logging mode is required for the planned vibration study.

## Integrity checks are not authentication

The per-row XOR detects many simple editing and transmission errors. It is weaker than
CRC-32 and does not protect against deliberate modification.

## Power and endurance are unqualified

The standalone cell, protection, charging, conversion, thermal behaviour, and operating
duration have not yet been validated as a complete system. USB operation does not
establish standalone endurance.

## Mechanical dimensions are nominal

Generic ESP32 and ST7789 modules vary between manufacturers. The current enclosure must
be updated from measured board, connector, mounting-hole, and installed-height values
before final printing.

