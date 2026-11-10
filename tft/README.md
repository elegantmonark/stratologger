# TFT/display subsystem

## Display demo

The [display demo](../src/demo/display_demo.cpp) runs the existing three screen UI
with generated readings. It does not read sensors or the SD card. The header says
`DEMO`, the footer says `SYNTHETIC`, and the status page marks battery and SD as
`NOT TESTED`.

To compile and upload it from the project root:

```text
pio run -e display-demo
pio run -e display-demo --target upload
pio device monitor -b 115200
```

Use USB power for this first check. Connect the display using its actual signal
labels, not a guessed pin order: VCC and LED to 3.3 V, GND to GND, SCK to GPIO18,
SDI or MOSI to GPIO23, DC to GPIO2, RESET to GPIO4, and CS to GPIO15. The SD socket
and sensors can stay disconnected. The screen rotates through live, IMU and system
views every eight seconds. Send `n` over serial to change screens manually.

GPIO34 cannot use an internal pull-up. If you wire a button to it, add the external
10 kOhm pull-up described in the hardware plan and compile with
`-D STRATO_DEMO_BUTTON=1` in the demo build flags. By default, the demo does not
read the unconnected button pin. The normal firmware is still built with
`pio run -e esp32dev`.

If the screen is blank, check 3.3 V at VCC and LED, common ground, and the signal
labels before changing the code. A successful compile only verifies the software
build. Record a photo and the wiring used when you run it on the actual display.

The display subsystem consists of the lid-mounted ST7789V/SD board, its keyed cable,
the TFT_eSPI compile-time setup in `platformio.ini`, and `DisplayManager` in
`src/ui/`. It consumes completed telemetry snapshots and never talks to sensors or
formats CSV data.

## TFT_eSPI setup

PlatformIO defines the equivalent of this `User_Setup.h` without modifying a package:

```cpp
#define ST7789_DRIVER
#define TFT_WIDTH  240
#define TFT_HEIGHT 320
#define TFT_MOSI   23
#define TFT_SCLK   18
#define TFT_CS     15
#define TFT_DC      2
#define TFT_RST     4
#define TFT_MISO   19
#define SPI_FREQUENCY 20000000
#define SPI_READ_FREQUENCY 6000000
#define SPI_TOUCH_FREQUENCY 2500000
```

Rotation 1 makes the screen 320 x 240. Rendering uses a 320 x 240, 8-bit sprite
(about 75 KiB) and pushes one complete frame at 2 Hz to reduce flicker. The altitude
and IMU ring buffers each contain 120 points.

The 20 MHz clock is intentional. The display sits in the lid and is connected by a
short harness, so the lower rate provides more signal margin than the module's
bench-top 40 MHz setting.

The TFT and onboard SD slot share SCK, MOSI and MISO but have separate chip selects.
Every display and SD operation is performed sequentially from the main loop. Do not
move one of them into an independent task unless access to the entire SPI transaction
is protected by the same mutex.

## Physical header mapping

The 14 male pins on the display board run from top to bottom as follows:

| Position | Module label | Stratologger connection |
|---:|---|---|
| 1 | `T_IRQ` | Not connected |
| 2 | `T_DO` | Not connected |
| 3 | `T_DIN` | Not connected |
| 4 | `T_CS` | Not connected |
| 5 | `T_CLK` | Not connected |
| 6 | `SDO (MISO)` | GPIO19 / shared SPI MISO |
| 7 | `LED` | 3.3 V |
| 8 | `SCK` | GPIO18 / shared SPI clock |
| 9 | `SDI (MOSI)` | GPIO23 / shared SPI MOSI |
| 10 | `DC` | GPIO2 |
| 11 | `RESET` | GPIO4 |
| 12 | `CS` | GPIO15 |
| 13 | `GND` | GND |
| 14 | `VCC` | 3.3 V |

The first five pins belong to the optional touch-controller interface and remain
unconnected because Stratologger does not use touch input.

The four female pins for the TFT board's built-in card socket run top to bottom as:

| Position | Module label | Stratologger connection |
|---:|---|---|
| 1 | `SD_SCK` | GPIO18 / shared SPI clock |
| 2 | `SD_MISO` | GPIO19 / shared SPI MISO |
| 3 | `SD_MOSI` | GPIO23 / shared SPI MOSI |
| 4 | `SD_CS` | GPIO5 |

The card socket is general-purpose storage. In this project it can hold the CSV
telemetry logs; it is not required for the TFT to display graphics.

The lid harness therefore needs a female connector for the TFT's 14 male pins and a
male connector for the four female `SD_*` pins. The four SD pins carry signals only;
the card socket receives power and ground through the main TFT header.

### SL-1 J5 cable map

J5 is a keyed 2x7 header. Keep the finished harness at or below 100 mm and verify
continuity before connecting either board.

| J5 pin | Signal | TFT end |
|---:|---|---|
| 1 | 3.3 V | Main pin 14 `VCC` |
| 2, 4, 6, 8, 14 | GND | Splice to main pin 13 `GND` |
| 3 | MOSI | Main pin 9 and SD pin 3 |
| 5 | MISO | Main pin 6 and SD pin 2 |
| 7 | SCK | Main pin 8 and SD pin 1 |
| 9 | SD CS | SD pin 4 |
| 10 | TFT reset | Main pin 11 |
| 11 | TFT DC | Main pin 10 |
| 12 | Backlight 3.3 V | Main pin 7 `LED` |
| 13 | TFT CS | Main pin 12 |

The multiple ground conductors are intentional. Keep them separate through the
ribbon and join them only at the TFT end. Main pins 1 through 5 remain empty.

The separate TF-card reader is not used by SL-1. Logging uses the socket already on
the TFT board.

## Screen contract

- **Live:** altitude gauge/readout, 60-second altitude trace, environmental cards,
  mission timer, load alert, artificial horizon, packet and log status.
- **IMU:** six 60-second traces, current acceleration magnitude and peak g.
- **System:** raw readings, battery, SD capacity, uptime and integrity counters.

The artificial horizon is gravity-derived. It is useful when motion is slow, but
linear acceleration during a drop or bicycle test will temporarily distort pitch
and roll; this is expected without a fused attitude filter.

