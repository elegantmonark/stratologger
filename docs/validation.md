# Validation record

## Software checks

On 6 November 2026, the ESP32 firmware build succeeded with the revised CSV
serializer. A native C++ fixture generated 100,000 synthetic rows for each serializer.
The old version showed 512 checksum mismatches; the revised version showed zero.
All 19 controlled fault cases met their expectations and all five host validator
tests passed. See [the result and methods](../results/log-validation/README.md).

The separate display demo is prepared and compiled, but its screen and harness have
not yet been tested in person. It must not be treated as a successful display test.

The following checks were run on 18 October 2026 from the repository root:

```text
pio run
python -m unittest discover -s tools -p "test_*.py"
```

The ESP32 firmware compiled successfully using the pinned `esp32dev` environment.
Reported static usage was 27,032 bytes of RAM from 327,680 bytes and 424,509 bytes of
flash from 1,310,720 bytes. Both CSV-validator unit tests passed.

## PCB design checks

On 24 October 2026, the routed SL-1 board was checked in KiCad 10 after refilling
both ground planes. The report contains zero DRC violations, zero unconnected pads
and zero footprint errors. The saved report is
`../pcb/SL-1/manufacturing/Stratologger_SL1-drc.rpt`.

## Hardware evidence

### 27 October 2026: fabrication hold and independent review

The original board again passed filled-zone DRC (0 violations, 0 unconnected items).
A separate audit checked 78 pads against the legacy repository connection tables and
15 firmware pin constants. Those checks agree internally, but inspection against the
common 30-pin DOIT pinout revealed a different physical socket mapping. Internal
consistency therefore does not establish correct wiring to the intended module.

The new balloon/telemetry logo is drawn on front silkscreen only. Copper is preserved.
The post-logo DRC report is `../pcb/SL-1/review/logo-board-drc.rpt`.
Manufacturing export is blocked by `../pcb/SL-1/release-status.json` until the exact
ESP32 module is identified and the socket map and routing are corrected. The
existing fabrication ZIP remains a historical pre-audit output and must not be ordered.

See [the findings and next steps](../pcb/SL-1/review/PCB_AUDIT.md).

No hardware validation result is published at this revision. A result should be added
only when the matching circuit photograph, firmware revision, test conditions, and
output file are available.

## Acceptance requirements

An assembled PCB configuration is accepted only after it has:

1. completed ten consecutive boots without an unexplained reset;
2. identified all three I2C sensors at their expected addresses;
3. rendered each display screen and switched screens from the physical button;
4. created a new SD log on each boot without overwriting earlier data;
5. produced a five-minute CSV with no malformed rows or checksum errors; and
6. recorded supply voltage, ambient pressure, wiring revision, and firmware revision.

The broader mission tests remain defined in `test-plan.md` and are not implied by a
successful bench test.

