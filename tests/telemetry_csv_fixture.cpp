// Stratologger serializer checks and synthetic data for host validation.
// Author: Trishan Biswas. Project started: February 2026.

#include <assert.h>
#include <locale.h>
#include <string.h>
#include "telemetry_csv.h"

int main(int argc, char** argv) {
  setlocale(LC_NUMERIC, "C");
  const unsigned long count = argc > 1 ? strtoul(argv[1], nullptr, 10) : 100000;
  const bool legacy = argc > 2 && strcmp(argv[2], "legacy") == 0;
  TelemetrySample s;
  char row[256];
  char tiny[4];
  assert(formatTelemetryCsv(tiny, sizeof(tiny), s) >= 4);
  s.temperatureC = 3.0e20F;
  assert(formatTelemetryCsv(row, sizeof(row), s) == -1);

  puts("PACKET_ID,TIMESTAMP_MS,TEMP_C,HUMIDITY_PCT,PRESSURE_HPA,ALTITUDE_M,"
       "ACCEL_X_MS2,ACCEL_Y_MS2,ACCEL_Z_MS2,GYRO_X_RADS,GYRO_Y_RADS,"
       "GYRO_Z_RADS,CHECKSUM_HEX");
  for (unsigned long i = 0; i < count; ++i) {
    // These smooth inputs exercise decimal boundaries. They are not flight data.
    const float phase = static_cast<float>(i) * 0.017F;
    s.packetId = static_cast<uint32_t>(i + 1);
    s.timestampMs = static_cast<uint32_t>((i + 1) * 500UL);
    s.temperatureC = 20.005F + 3.0F * sinf(phase);
    s.humidityPct = 45.5F + 10.0F * sinf(phase * 0.7F);
    s.pressureHpa = 1012.75F + 2.0F * cosf(phase);
    s.altitudeM = 4.0F + 0.5F * sinf(phase);
    s.accelX = 0.2F * sinf(phase);
    s.accelY = -0.3F * cosf(phase);
    s.accelZ = 9.81F + 0.1F * sinf(phase);
    s.gyroX = 0.0125F * sinf(phase);
    s.gyroY = -0.025F * cosf(phase);
    s.gyroZ = 0.002F * sinf(phase);
    int length;
    if (legacy) {
      // Reproduce the previous logger format with its checksum before rounding.
      length = snprintf(row, sizeof(row),
          "%lu,%lu,%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%.4f,%.4f,%.4f,%08lX\n",
          static_cast<unsigned long>(s.packetId),
          static_cast<unsigned long>(s.timestampMs), s.temperatureC,
          s.humidityPct, s.pressureHpa, s.altitudeM, s.accelX, s.accelY,
          s.accelZ, s.gyroX, s.gyroY, s.gyroZ,
          static_cast<unsigned long>(calculateChecksum(s)));
    } else {
      length = formatTelemetryCsv(row, sizeof(row), s);
    }
    assert(length > 0 && static_cast<size_t>(length) < sizeof(row));
    fputs(row, stdout);
  }
}
