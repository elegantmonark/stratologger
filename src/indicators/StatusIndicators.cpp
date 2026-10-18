/*
 * High-altitude telemetry payload
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#include "StatusIndicators.h"

#include "config.h"
#include "telemetry_types.h"

void StatusIndicators::begin() {
  pinMode(Config::PIN_LED, OUTPUT);
  digitalWrite(Config::PIN_LED, LOW);
  ledcSetup(Config::BUZZER_LEDC_CHANNEL, 1000,
            Config::BUZZER_LEDC_RESOLUTION);
  ledcAttachPin(Config::PIN_BUZZER, Config::BUZZER_LEDC_CHANNEL);
}

void StatusIndicators::toneFor(uint16_t frequencyHz, uint16_t durationMs) {
  ledcWriteTone(Config::BUZZER_LEDC_CHANNEL, frequencyHz);
  delay(durationMs);
  ledcWriteTone(Config::BUZZER_LEDC_CHANNEL, 0);
}

void StatusIndicators::update() {
  if (ledOn_ && static_cast<int32_t>(millis() - ledOffAtMs_) >= 0) {
    digitalWrite(Config::PIN_LED, LOW);
    ledOn_ = false;
  }
}

void StatusIndicators::heartbeat() {
  digitalWrite(Config::PIN_LED, HIGH);
  ledOn_ = true;
  ledOffAtMs_ = millis() + 12UL;
}

void StatusIndicators::allOkMelody() {
  constexpr uint16_t notes[] = {880, 1175, 1568};
  for (const uint16_t note : notes) {
    toneFor(note, 90);
    delay(60);
  }
}

void StatusIndicators::blinkCode(uint8_t count) {
  for (uint8_t i = 0; i < count; ++i) {
    digitalWrite(Config::PIN_LED, HIGH);
    delay(180);
    digitalWrite(Config::PIN_LED, LOW);
    delay(180);
  }
  delay(650);
}

[[noreturn]] void StatusIndicators::faultLoop(uint8_t faults) {
  for (uint8_t i = 0; i < 5; ++i) {
    toneFor(220, 350);
    delay(250);
  }

  while (true) {
    if (faults & FAULT_BMP280) blinkCode(1);
    if (faults & FAULT_AHT20) blinkCode(2);
    if (faults & FAULT_MPU6050) blinkCode(3);
    if (faults & FAULT_SD) blinkCode(4);
    if (faults & FAULT_DISPLAY) blinkCode(5);
    delay(1200);
  }
}

