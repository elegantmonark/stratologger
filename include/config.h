/*
 * High-altitude telemetry payload
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#pragma once

#include <Arduino.h>

namespace Config {

// Shared I2C bus.
constexpr uint8_t PIN_I2C_SDA = 21;
constexpr uint8_t PIN_I2C_SCL = 22;

// Shared VSPI bus. TFT pin macros live in platformio.ini for TFT_eSPI.
constexpr uint8_t PIN_SPI_SCK = 18;
constexpr uint8_t PIN_SPI_MISO = 19;
constexpr uint8_t PIN_SPI_MOSI = 23;
constexpr uint8_t PIN_TFT_CS = 15;
constexpr uint8_t PIN_SD_CS = 5;

constexpr uint8_t PIN_LED = 25;
constexpr uint8_t PIN_BUZZER = 26;
constexpr uint8_t PIN_SCREEN_BUTTON = 34;  // External 10 kOhm pull-up required.
constexpr uint8_t PIN_BATTERY_ADC = 35;

constexpr uint32_t SERIAL_BAUD = 115200;
constexpr uint32_t SAMPLE_INTERVAL_MS = 500;
constexpr uint32_t BUTTON_DEBOUNCE_MS = 40;
constexpr uint32_t SD_SPI_HZ = 10000000;
constexpr uint16_t GRAPH_POINTS = 120;

// Calibrate this against a known local pressure for useful absolute altitude.
constexpr float SEA_LEVEL_PRESSURE_HPA = 1013.25F;
constexpr float ALTITUDE_GAUGE_MIN_M = -50.0F;
constexpr float ALTITUDE_GAUGE_MAX_M = 3000.0F;

// Battery divider: BAT+ -- R_TOP -- GPIO35 -- R_BOTTOM -- GND.
constexpr float BATTERY_R_TOP_OHM = 100000.0F;
constexpr float BATTERY_R_BOTTOM_OHM = 100000.0F;
constexpr float BATTERY_CALIBRATION = 1.000F;
constexpr float BATTERY_EMPTY_V = 3.20F;
constexpr float BATTERY_FULL_V = 4.20F;

constexpr uint8_t BUZZER_LEDC_CHANNEL = 0;
constexpr uint8_t BUZZER_LEDC_RESOLUTION = 8;

}  // namespace Config

