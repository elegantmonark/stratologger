/*
 * High-altitude telemetry payload
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#pragma once

#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <Wire.h>

#include "telemetry_types.h"

class SensorManager {
 public:
  uint8_t begin(TwoWire& wire = Wire);
  bool read(TelemetrySample& sample);

 private:
  Adafruit_BMP280 bmp_;
  Adafruit_AHTX0 aht_;
  Adafruit_MPU6050 mpu_;
  bool bmpReady_ = false;
  bool ahtReady_ = false;
  bool mpuReady_ = false;
};

