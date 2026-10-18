# Verification and mission test plan

Record firmware commit, enclosure revision, SD-card identity, battery identity,
ambient pressure and test operator in the logbook for every run.

## Bench acceptance

- Confirm three-beep boot and each deliberate 1/2/3/4 fault code by unplugging one
  module at a time with power removed.
- Power-cycle ten times and confirm ten unique log files with valid headers.
- Compare both temperatures, pressure and battery voltage with reference instruments.
- Leave stationary for five minutes; confirm acceleration magnitude near 1 g and
  stable pitch/roll after mounting alignment is accounted for.
- Exercise the screen button for 100 transitions with no resets or SD errors.
- Run `validate_log.py` and require zero malformed rows and checksum errors.

## Elevator

Calibrate local reference pressure immediately before the run. Keep the unit still
at each floor for 20 seconds. Compare plateau changes, not just absolute altitude.

## Thermal transition

Use a sealed bag to prevent condensation before moving a cold payload into warm,
humid air. Keep the cell within its manufacturer's discharge temperature limits.
Log at least ten minutes at each plateau and note sensor lag and self-heating.

## Bicycle vibration

Use two independent restraints and keep the payload away from wheels and controls.
Record mounting orientation and sampling rate. The 2 Hz mission log cannot support
meaningful vibration FFT above 1 Hz; for this test, a future high-rate IMU mode
(for example 200 Hz binary logging) is required. Do not claim vibration spectra from
the present 500 ms CSV stream.

## Drop

Use a sacrificial enclosure and an inert mass or protected cell under controlled
conditions. Drop onto a contained test surface, never near people. Inspect cell,
wiring, solder joints and SD retention after every impact. Retire any dented,
punctured, swollen or hot cell immediately using the locally approved procedure.

## Endurance

Run in a fire-resistant location with temperature monitoring. Record start/end cell
voltage, log duration, missing deadlines, file size, resets and final free space.
Do not leave an unproven charging circuit unattended overnight.

## Corruption stress

Work on a copied CSV. Flip digits, remove a row, duplicate a packet ID and truncate
the final line. The validator must report checksum, gap/duplicate, and malformed-row
errors. Abrupt-power tests should use a current-limited bench supply, not repeated
battery disconnection.

