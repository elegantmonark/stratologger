/*
 * Stratologger display demo
 * Author: Trishan Biswas
 * Project started: February 2026
 * This is synthetic data. It does not read the sensors or SD card.
 */

#include <Arduino.h>
#include <math.h>
#include "config.h"
#include "telemetry_types.h"
#include "../ui/DisplayManager.h"

#ifndef STRATO_DEMO_BUTTON
#define STRATO_DEMO_BUTTON 0
#endif

namespace {
DisplayManager display;
TelemetrySample sample;
SystemStats stats;
UiScreen screen = UiScreen::Live;
uint32_t nextFrame = 0;
uint32_t nextPage = 0;
#if STRATO_DEMO_BUTTON
bool lastReading = HIGH;
bool stableReading = HIGH;
uint32_t lastChange = 0;
#endif

void changePage() {
  screen = static_cast<UiScreen>(
      (static_cast<uint8_t>(screen) + 1U) % static_cast<uint8_t>(UiScreen::Count));
  nextPage = millis() + 8000UL;
  Serial.printf("Demo page %u\n", static_cast<unsigned>(screen));
}

void updateSample(uint32_t now) {
  const float t = now / 1000.0F;
  const float slow = sinf(t * 0.22F);
  ++sample.packetId;
  sample.timestampMs = now;
  sample.temperatureC = 22.0F + 1.4F * slow;
  sample.bmpTemperatureC = sample.temperatureC - 0.3F;
  sample.humidityPct = 48.0F + 3.0F * sinf(t * 0.13F);
  sample.pressureHpa = 1013.2F + 0.8F * sinf(t * 0.09F);
  sample.altitudeM = 175.0F + 35.0F * slow;
  sample.accelX = 0.4F * sinf(t * 0.8F);
  sample.accelY = 0.3F * cosf(t * 0.6F);
  sample.accelZ = 9.81F + 0.12F * sinf(t * 0.4F);
  sample.gyroX = 0.025F * sinf(t * 0.7F);
  sample.gyroY = 0.018F * cosf(t * 0.5F);
  sample.gyroZ = 0.011F * sinf(t * 0.4F);
  sample.accelMagnitudeG = sqrtf(sample.accelX * sample.accelX +
                                 sample.accelY * sample.accelY +
                                 sample.accelZ * sample.accelZ) / 9.80665F;
  sample.rollDeg = 8.0F * sinf(t * 0.45F);
  sample.pitchDeg = 6.0F * cosf(t * 0.32F);
  stats.uptimeMs = now;
  if (sample.accelMagnitudeG > stats.peakG) stats.peakG = sample.accelMagnitudeG;
}
}

void setup() {
  Serial.begin(Config::SERIAL_BAUD);
  Serial.println("Stratologger display demo. All measurements are synthetic.");
  Serial.println("Send n over serial to change screen. Screens also rotate every 8 s.");
#if STRATO_DEMO_BUTTON
  pinMode(Config::PIN_SCREEN_BUTTON, INPUT);
#endif
  pinMode(Config::PIN_SD_CS, OUTPUT);
  digitalWrite(Config::PIN_SD_CS, HIGH);
  stats.demoMode = true;
  if (!display.begin()) {
    Serial.println("Display setup failed. Check the display wiring and 3.3 V supply.");
    return;
  }
  display.showBootMessage("DISPLAY DEMO / SYNTHETIC");
  delay(1000);
  nextFrame = millis();
  nextPage = millis() + 8000UL;
}

void loop() {
  const uint32_t now = millis();
  while (Serial.available()) {
    if (Serial.read() == 'n') changePage();
  }
#if STRATO_DEMO_BUTTON
  const bool reading = digitalRead(Config::PIN_SCREEN_BUTTON);
  if (reading != lastReading) lastChange = now;
  if (now - lastChange >= Config::BUTTON_DEBOUNCE_MS && reading != stableReading) {
    stableReading = reading;
    if (stableReading == LOW) changePage();
  }
  lastReading = reading;
#endif
  if (static_cast<int32_t>(now - nextPage) >= 0) changePage();
  if (static_cast<int32_t>(now - nextFrame) >= 0) {
    updateSample(now);
    display.render(sample, stats, screen);
    nextFrame = now + 500UL;
  }
  delay(5);
}
