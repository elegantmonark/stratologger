/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>

#include <algorithm>

#include "config.h"
#include "indicators/StatusIndicators.h"
#include "sensors/SensorManager.h"
#include "storage/TelemetryLogger.h"
#include "telemetry_types.h"
#include "ui/DisplayManager.h"

namespace {
SensorManager sensors;
TelemetryLogger logger;
DisplayManager display;
StatusIndicators indicators;

TelemetrySample latest;
SystemStats stats;
UiScreen currentScreen = UiScreen::Live;
uint32_t nextSampleMs = 0;
uint32_t lastSpaceRefreshMs = 0;
uint32_t lastButtonChangeMs = 0;
bool lastButtonReading = HIGH;
bool stableButtonState = HIGH;

float readBatteryVoltage() {
  const uint32_t adcMillivolts = analogReadMilliVolts(Config::PIN_BATTERY_ADC);
  const float dividerRatio =
      (Config::BATTERY_R_TOP_OHM + Config::BATTERY_R_BOTTOM_OHM) /
      Config::BATTERY_R_BOTTOM_OHM;
  return (adcMillivolts / 1000.0F) * dividerRatio *
         Config::BATTERY_CALIBRATION;
}

void updateButton(uint32_t now) {
  const bool reading = digitalRead(Config::PIN_SCREEN_BUTTON);
  if (reading != lastButtonReading) {
    lastButtonReading = reading;
    lastButtonChangeMs = now;
  }
  if ((now - lastButtonChangeMs) >= Config::BUTTON_DEBOUNCE_MS &&
      reading != stableButtonState) {
    stableButtonState = reading;
    if (stableButtonState == LOW) {
      const uint8_t next =
          (static_cast<uint8_t>(currentScreen) + 1U) %
          static_cast<uint8_t>(UiScreen::Count);
      currentScreen = static_cast<UiScreen>(next);
      display.render(latest, stats, currentScreen);
    }
  }
}

void refreshStats(uint32_t now) {
  stats.uptimeMs = now;
  stats.logWriteErrors = logger.writeErrors();
  stats.sdLogging = logger.isReady() && logger.writeErrors() == 0;
  stats.logFileName = logger.fileName();
  stats.batteryVoltage = readBatteryVoltage();
  if (now - lastSpaceRefreshMs >= 10000UL) {
    logger.refreshSpace();
    lastSpaceRefreshMs = now;
  }
  stats.sdTotalBytes = logger.totalBytes();
  stats.sdFreeBytes = logger.freeBytes();
}
}  // namespace

void setup() {
  Serial.begin(Config::SERIAL_BAUD);
  indicators.begin();

  pinMode(Config::PIN_SCREEN_BUTTON, INPUT);  // GPIO34 has no internal pull-up.
  pinMode(Config::PIN_BATTERY_ADC, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(Config::PIN_BATTERY_ADC, ADC_11db);

  Wire.begin(Config::PIN_I2C_SDA, Config::PIN_I2C_SCL);
  Wire.setClock(400000);
  SPI.begin(Config::PIN_SPI_SCK, Config::PIN_SPI_MISO, Config::PIN_SPI_MOSI);

  uint8_t faults = FAULT_NONE;
  if (!display.begin()) faults |= FAULT_DISPLAY;
  display.showBootMessage("INITIALISING SENSORS");
  faults |= sensors.begin(Wire);
  display.showBootMessage("MOUNTING SD CARD");
  faults |= logger.begin(SPI);

  if (faults != FAULT_NONE) {
    Serial.printf("Boot fault mask: 0x%02X\n", faults);
    indicators.faultLoop(faults);
  }

  indicators.allOkMelody();
  nextSampleMs = millis();
  lastSpaceRefreshMs = millis() - 10000UL;
}

void loop() {
  const uint32_t now = millis();
  indicators.update();
  updateButton(now);

  if (static_cast<int32_t>(now - nextSampleMs) < 0) {
    delay(1);
    return;
  }

  const uint32_t lateness = now - nextSampleMs;
  if (lateness >= Config::SAMPLE_INTERVAL_MS) {
    const uint32_t missed = lateness / Config::SAMPLE_INTERVAL_MS;
    stats.droppedDeadlines += missed;
    nextSampleMs += missed * Config::SAMPLE_INTERVAL_MS;
  }
  nextSampleMs += Config::SAMPLE_INTERVAL_MS;

  latest.packetId++;
  latest.timestampMs = now;
  if (!sensors.read(latest)) {
    Serial.println("Sensor read failed");
  }
  latest.checksum = calculateChecksum(latest);
  if (calculateChecksum(latest) != latest.checksum) {
    ++stats.checksumErrors;
  }
  if (!logger.append(latest)) {
    Serial.println("SD log write failed");
  }
  stats.peakG = std::max(stats.peakG, latest.accelMagnitudeG);
  refreshStats(now);
  display.render(latest, stats, currentScreen);
  indicators.heartbeat();
}

