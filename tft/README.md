# TFT/display subsystem

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
#define SPI_FREQUENCY 40000000
#define SPI_READ_FREQUENCY 6000000
#define SPI_TOUCH_FREQUENCY 2500000
```

Rotation 1 makes the screen 320 x 240. Rendering uses a 320 x 240, 8-bit sprite
(about 75 KiB) and pushes one complete frame at 2 Hz to reduce flicker. The altitude
and IMU ring buffers each contain 120 points.

The TFT and onboard SD slot share SCK, MOSI and MISO but have separate chip selects.
Every display and SD operation is performed sequentially from the main loop. Do not
move one of them into an independent task unless access to the entire SPI transaction
is protected by the same mutex.

## Screen contract

- **Live:** altitude gauge/readout, 60-second altitude trace, environmental cards,
  mission timer, load alert, artificial horizon, packet and log status.
- **IMU:** six 60-second traces, current acceleration magnitude and peak g.
- **System:** raw readings, battery, SD capacity, uptime and integrity counters.

The artificial horizon is gravity-derived. It is useful when motion is slow, but
linear acceleration during a drop or bicycle test will temporarily distort pitch
and roll; this is expected without a fused attitude filter.

