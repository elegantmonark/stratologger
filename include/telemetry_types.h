/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#pragma once

#include <Arduino.h>
#include <math.h>

enum FaultBit : uint8_t {
  FAULT_NONE = 0,
  FAULT_BMP280 = 1U << 0,
  FAULT_AHT20 = 1U << 1,
  FAULT_MPU6050 = 1U << 2,
  FAULT_SD = 1U << 3,
  FAULT_DISPLAY = 1U << 4,
};

enum class UiScreen : uint8_t {
  Live = 0,
  Imu = 1,
  System = 2,
  Count = 3,
};

struct TelemetrySample {
  uint32_t packetId = 0;
  uint32_t timestampMs = 0;
  float temperatureC = NAN;
  float humidityPct = NAN;
  float pressureHpa = NAN;
  float altitudeM = NAN;
  float bmpTemperatureC = NAN;
  float accelX = NAN;
  float accelY = NAN;
  float accelZ = NAN;
  float gyroX = NAN;
  float gyroY = NAN;
  float gyroZ = NAN;
  float accelMagnitudeG = NAN;
  float rollDeg = NAN;
  float pitchDeg = NAN;
  uint32_t checksum = 0;
};

struct SystemStats {
  uint32_t uptimeMs = 0;
  uint32_t droppedDeadlines = 0;
  uint32_t checksumErrors = 0;
  uint32_t logWriteErrors = 0;
  uint64_t sdTotalBytes = 0;
  uint64_t sdFreeBytes = 0;
  float batteryVoltage = NAN;
  float peakG = 0.0F;
  bool sdLogging = false;
  const char* logFileName = "---";
};

inline uint32_t scaledChecksumValue(float value, float scale) {
  if (!isfinite(value)) {
    return 0x80000000UL;
  }
  const int32_t scaled = static_cast<int32_t>(lroundf(value * scale));
  return static_cast<uint32_t>(scaled);
}

inline uint32_t calculateChecksum(const TelemetrySample& s) {
  uint32_t checksum = s.packetId ^ s.timestampMs;
  checksum ^= scaledChecksumValue(s.temperatureC, 100.0F);
  checksum ^= scaledChecksumValue(s.humidityPct, 100.0F);
  checksum ^= scaledChecksumValue(s.pressureHpa, 100.0F);
  checksum ^= scaledChecksumValue(s.altitudeM, 100.0F);
  checksum ^= scaledChecksumValue(s.accelX, 1000.0F);
  checksum ^= scaledChecksumValue(s.accelY, 1000.0F);
  checksum ^= scaledChecksumValue(s.accelZ, 1000.0F);
  checksum ^= scaledChecksumValue(s.gyroX, 10000.0F);
  checksum ^= scaledChecksumValue(s.gyroY, 10000.0F);
  checksum ^= scaledChecksumValue(s.gyroZ, 10000.0F);
  return checksum;
}

