/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#pragma once

#include <FS.h>
#include <SD.h>
#include <SPI.h>

#include "telemetry_types.h"

class TelemetryLogger {
 public:
  uint8_t begin(SPIClass& spi);
  bool append(const TelemetrySample& sample);
  void refreshSpace();
  void close();

  bool isReady() const { return ready_; }
  const char* fileName() const { return fileName_; }
  uint32_t writeErrors() const { return writeErrors_; }
  uint64_t totalBytes() const { return totalBytes_; }
  uint64_t freeBytes() const { return freeBytes_; }

 private:
  bool selectFileName();
  bool writeHeader();

  File file_;
  char fileName_[20] = "---";
  bool ready_ = false;
  uint32_t writeErrors_ = 0;
  uint64_t totalBytes_ = 0;
  uint64_t freeBytes_ = 0;
};

