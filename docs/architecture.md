# System architecture

```text
 Protected cell ── charger/protection ── 5 V boost ── ESP32 VIN
       │                                         ├── 3V3 sensor rail
       └── 100k/100k divider ── GPIO35          └── control + storage

 I2C (21/22) ── AHT20 + BMP280 ── MPU6050

 VSPI (18/23/19) ─┬─ ST7789V, CS15, DC2, RST4
                   └─ TFT-board SD socket, CS5

 GPIO34 ── screen button        GPIO25 ── LED
 GPIO26 ── passive piezo
```

## Firmware flow

`main.cpp` is a non-blocking scheduler after boot. Every 500 ms it reads all sensors,
derives attitude and load, calculates the checksum, appends and flushes one CSV row,
updates system counters, renders the active display screen, and pulses the LED.

The modules have narrow ownership:

- `SensorManager` owns I2C sensor drivers and physical-unit conversion.
- `TelemetryLogger` owns SD mounting, file naming, serialization and flushes.
- `DisplayManager` owns TFT_eSPI, the frame sprite and all graph buffers.
- `StatusIndicators` owns the LED and buzzer.
- `telemetry_types.h` is the data contract shared by those modules.

TFT and SD calls are kept serial in one loop because they share the VSPI peripheral.
Moving display rendering to the second ESP32 core would require a bus mutex and adds
little at a 2 Hz update rate.

## Error counters

- `DROP` counts missed 500 ms scheduler deadlines. This is the meaningful local
  equivalent of packet loss because there is no radio receiver in the current design.
- `CRC` counts an in-memory checksum mismatch. It should remain zero.
- `WRITE` counts failed or truncated SD writes.

The host validator additionally detects checksum corruption, malformed rows,
duplicate or missing packet IDs, and backwards timestamps after a mission.

## Checksum definition

The checksum is a 32-bit XOR. Packet ID and timestamp are used directly; signed
scaled values are converted to their two's-complement `uint32_t` representation.

| Field group | Scale |
|---|---:|
| Temperature, humidity, pressure, altitude | 100 |
| Acceleration XYZ | 1000 |
| Gyroscope XYZ | 10000 |

Non-finite values map to `0x80000000`. `CHECKSUM_HEX` is written as eight uppercase
hex digits. XOR is useful for simple corruption exercises but is not cryptographic;
CRC-32 is the natural future upgrade if the file format may change.

