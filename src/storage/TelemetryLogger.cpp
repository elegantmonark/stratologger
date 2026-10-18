/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#include "TelemetryLogger.h"

#include "config.h"

namespace {
constexpr char CSV_HEADER[] =
    "PACKET_ID,TIMESTAMP_MS,TEMP_C,HUMIDITY_PCT,PRESSURE_HPA,ALTITUDE_M,"
    "ACCEL_X_MS2,ACCEL_Y_MS2,ACCEL_Z_MS2,GYRO_X_RADS,GYRO_Y_RADS,"
    "GYRO_Z_RADS,CHECKSUM_HEX\n";
}

uint8_t TelemetryLogger::begin(SPIClass& spi) {
  pinMode(Config::PIN_SD_CS, OUTPUT);
  digitalWrite(Config::PIN_SD_CS, HIGH);
  digitalWrite(Config::PIN_TFT_CS, HIGH);

  if (!SD.begin(Config::PIN_SD_CS, spi, Config::SD_SPI_HZ)) {
    return FAULT_SD;
  }
  if (SD.cardType() == CARD_NONE || !selectFileName()) {
    SD.end();
    return FAULT_SD;
  }

  file_ = SD.open(fileName_, FILE_WRITE);
  if (!file_ || !writeHeader()) {
    close();
    SD.end();
    return FAULT_SD;
  }

  ready_ = true;
  refreshSpace();
  return FAULT_NONE;
}

bool TelemetryLogger::selectFileName() {
  for (uint16_t index = 1; index <= 999; ++index) {
    snprintf(fileName_, sizeof(fileName_), "/LOG_%03u.CSV", index);
    if (!SD.exists(fileName_)) {
      return true;
    }
  }
  return false;
}

bool TelemetryLogger::writeHeader() {
  const size_t expected = sizeof(CSV_HEADER) - 1;
  const size_t written = file_.print(CSV_HEADER);
  file_.flush();
  return written == expected;
}

bool TelemetryLogger::append(const TelemetrySample& sample) {
  if (!ready_ || !file_) {
    ++writeErrors_;
    return false;
  }

  char line[256];
  const int length = snprintf(
      line, sizeof(line),
      "%lu,%lu,%.2f,%.2f,%.2f,%.2f,%.3f,%.3f,%.3f,%.4f,%.4f,%.4f,%08lX\n",
      static_cast<unsigned long>(sample.packetId),
      static_cast<unsigned long>(sample.timestampMs), sample.temperatureC,
      sample.humidityPct, sample.pressureHpa, sample.altitudeM, sample.accelX,
      sample.accelY, sample.accelZ, sample.gyroX, sample.gyroY, sample.gyroZ,
      static_cast<unsigned long>(sample.checksum));

  if (length <= 0 || static_cast<size_t>(length) >= sizeof(line) ||
      file_.write(reinterpret_cast<const uint8_t*>(line), length) !=
          static_cast<size_t>(length)) {
    ++writeErrors_;
    return false;
  }

  // At 2 Hz this intentionally favours impact/power-loss survival over speed.
  file_.flush();
  return true;
}

void TelemetryLogger::refreshSpace() {
  if (!ready_) {
    return;
  }
  totalBytes_ = SD.totalBytes();
  const uint64_t used = SD.usedBytes();
  freeBytes_ = totalBytes_ > used ? totalBytes_ - used : 0;
}

void TelemetryLogger::close() {
  if (file_) {
    file_.flush();
    file_.close();
  }
  ready_ = false;
}

