# Validation record

## Software checks

The following checks were run on 18 October 2026 from the repository root:

```text
pio run
python -m unittest discover -s tools -p "test_*.py"
```

The ESP32 firmware compiled successfully using the pinned `esp32dev` environment.
Reported static usage was 27,032 bytes of RAM from 327,680 bytes and 424,509 bytes of
flash from 1,310,720 bytes. Both CSV-validator unit tests passed.

## Hardware evidence

No hardware validation result is published at this revision. A result should be added
only when the matching circuit photograph, firmware revision, test conditions, and
output file are available.

## Acceptance requirements

A breadboard configuration is accepted only after it has:

1. completed ten consecutive boots without an unexplained reset;
2. identified all three I2C sensors at their expected addresses;
3. rendered each display screen and switched screens from the physical button;
4. created a new SD log on each boot without overwriting earlier data;
5. produced a five-minute CSV with no malformed rows or checksum errors; and
6. recorded supply voltage, ambient pressure, wiring revision, and firmware revision.

The broader mission tests remain defined in `test-plan.md` and are not implied by a
successful bench test.

