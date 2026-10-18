# Electrical and perfboard assembly

## Layout strategy

Use the ESP32 and TFT as removable assemblies on female headers. Put the display in
the lid and connect it to the main perfboard with a short keyed harness; this keeps
the TFT a physically replaceable subsystem as well as a separate software module.

A practical top-view placement on a roughly 90 x 70 mm perfboard is:

```text
 USB/opening edge
 ┌──────────────────────────────────────────────────────────┐
 │ [ESP32 DevKit on sockets]       [TFT/SD harness header]  │
 │                                                          │
 │ [AHT+BMP]  airflow edge          [MPU6050, axes marked]   │
 │                                                          │
 │ [power switch] [5 V boost]       [button/LED/buzzer hdr] │
 │ [battery/charge connector]       [ADC divider + 100 nF]  │
 └──────────────────────────────────────────────────────────┘
```

Place the BMP280/AHT20 at a vented enclosure edge, away from the ESP32 regulator,
boost converter, TFT backlight and battery. Place the MPU6050 near the enclosure's
mechanical centre, flat and square to the intended X/Y axes. Label those axes on the
board and enclosure before calibration.

## Suggested construction order

1. Print the netlist and continuity-check the unpowered perfboard rails.
2. Fit sockets and headers. Do not permanently solder the ESP32, sensors or TFT.
3. Build GND and 3V3 rails with wire thick enough for the load; add 100 uF bulk
   capacitance and one 100 nF capacitor at each sensor/display connector.
4. Wire I2C as a short daisy chain. Check whether both breakout boards include
   pull-ups; their parallel value should normally remain above about 2 kohm.
5. Wire the three shared VSPI lines, then the separate TFT and SD control lines.
   Keep SCK short, avoid large loops, and route a ground conductor with the TFT loom.
6. Add the GPIO34 button and its physical 10 kohm pull-up to 3V3.
7. Add the battery divider: protected BAT+ to 100 kohm, midpoint to GPIO35, then
   100 kohm and 100 nF in parallel from midpoint to GND.
8. Fit LED and passive piezo. If the buzzer is magnetic or draws more than roughly
   8 mA, drive it with an NPN transistor/MOSFET and a base/gate resistor instead.
9. Build and verify the protected-cell/charger/boost section separately. Adjust it
   to 5.0 V before connecting `VIN`.
10. Inspect for solder bridges, then continuity-test every row of `netlist.csv`
    with the ESP32 and battery removed.

## TFT harness

Fourteen-pin ST7789 boards do not use a universal pin order. Match the silk-screened
**signal names**, not physical pin numbers. Some boards label MOSI as SDA or DIN and
SCK as SCL/CLK. The display and SD socket share SCK/MOSI; the SD socket must also
return MISO. Keep both CS wires distinct and never tie them low.

## Bring-up checkpoints

Power each stage from a current-limited USB supply first:

- Bare power board: 3.3 V and 5 V rails in tolerance, no heating.
- ESP32 only: serial boot and upload reliable.
- I2C only: addresses 0x38, 0x68, and BMP280 at 0x76 or 0x77.
- TFT only: boot message has correct rotation and colour. If red/blue are swapped,
  add `-D TFT_RGB_ORDER=TFT_BGR` to `platformio.ini`.
- SD only: a new log appears after every reset and older files remain intact.
- Full assembly: test from USB, then from the standalone supply.

Measure the actual cell voltage with a multimeter and adjust
`BATTERY_CALIBRATION` until the System screen agrees. Secure the battery mechanically;
do not rely on solder joints or wires to restrain it during the drop test.

