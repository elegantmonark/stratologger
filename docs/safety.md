# Safety

## Electrical bring-up

Disconnect power before changing wiring. Check continuity and rail resistance before
first power-up, then use USB or a current-limited bench supply for staged bring-up.
All sensor and logic connections in this design operate at 3.3 V.

GPIO2, GPIO5, and GPIO15 are ESP32 strapping pins. External circuitry must not force
them to an incompatible level during reset. If programming fails, remove power,
disconnect the display harness, upload the firmware, and reconnect only while unpowered.

## Lithium cells

Do not connect a bare one-cell Li-ion or LiPo battery directly to the ESP32 `VIN` pin.
Use a protected cell, a compatible charger/protection circuit, and a converter suitable
for the intended supply path. Verify polarity and output voltage with a multimeter before
connecting the ESP32. Do not charge or operate a damaged, swollen, punctured, or unusually
warm cell.

## Mechanical tests

Secure the battery independently of its wires and solder joints. Perform impact and
vehicle-mounted tests in a controlled area away from people, traffic, and rotating parts.
Inspect the cell and all restraints after each impact.

## Environmental tests

Prevent condensation when moving cold electronics into warm humid air. Keep the battery
within its manufacturer's temperature limits. Do not leave an unqualified charging or
power circuit unattended during an endurance run.

## Intended use

This is an engineering prototype, not certified flight hardware or a safety-critical
instrument. Deployment must comply with the rules applicable to the chosen vehicle,
location, altitude, radio equipment, and battery transport.

