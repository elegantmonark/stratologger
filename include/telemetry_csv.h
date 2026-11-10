/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 */

#pragma once

#include <stdio.h>
#include <stdlib.h>
#include "telemetry_types.h"

// Check the values that will actually be saved, after decimal rounding.
inline int formatTelemetryCsv(char* line, size_t capacity,
                              const TelemetrySample& sample) {
  char fields[224];
  const int length = snprintf(
      fields, sizeof(fields),
      "%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%.4f,%.4f,%.4f",
      sample.temperatureC, sample.humidityPct, sample.pressureHpa,
      sample.altitudeM, sample.accelX, sample.accelY, sample.accelZ,
      sample.gyroX, sample.gyroY, sample.gyroZ);
  if (length < 0 || static_cast<size_t>(length) >= sizeof(fields)) return -1;

  constexpr double scales[] = {100, 100, 100, 100, 1000, 1000, 1000,
                               10000, 10000, 10000};
  uint32_t checksum = sample.packetId ^ sample.timestampMs;
  const char* cursor = fields;
  for (unsigned int i = 0; i < 10; ++i) {
    char* end = nullptr;
    const double value = strtod(cursor, &end);
    if (end == cursor || (i < 9 ? *end != ',' : *end != '\0')) return -1;
    if (!isfinite(value)) {
      checksum ^= 0x80000000UL;
    } else {
      const double rounded = round(value * scales[i]);
      if (rounded < -2147483648.0 || rounded > 2147483647.0) return -1;
      checksum ^= static_cast<uint32_t>(static_cast<int32_t>(rounded));
    }
    cursor = end + (i < 9 ? 1 : 0);
  }
  return snprintf(line, capacity, "%lu,%lu,%s,%08lX\n",
                  static_cast<unsigned long>(sample.packetId),
                  static_cast<unsigned long>(sample.timestampMs), fields,
                  static_cast<unsigned long>(checksum));
}
