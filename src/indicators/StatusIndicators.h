/*
 * High-altitude telemetry payload
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#pragma once

#include <Arduino.h>

class StatusIndicators {
 public:
  void begin();
  void update();
  void heartbeat();
  void allOkMelody();
  [[noreturn]] void faultLoop(uint8_t faults);

 private:
  void toneFor(uint16_t frequencyHz, uint16_t durationMs);
  void blinkCode(uint8_t count);
  uint32_t ledOffAtMs_ = 0;
  bool ledOn_ = false;
};

