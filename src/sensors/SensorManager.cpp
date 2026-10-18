/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#include "SensorManager.h"

#include <math.h>

#include "config.h"

uint8_t SensorManager::begin(TwoWire& wire) {
  uint8_t faults = FAULT_NONE;

  // Common BMP280 combo boards use either address depending on SDO strapping.
  bmpReady_ = bmp_.begin(0x76) || bmp_.begin(0x77);
  if (!bmpReady_) {
    faults |= FAULT_BMP280;
  } else {
    bmp_.setSampling(Adafruit_BMP280::MODE_NORMAL,
                     Adafruit_BMP280::SAMPLING_X2,
                     Adafruit_BMP280::SAMPLING_X16,
                     Adafruit_BMP280::FILTER_X16,
                     Adafruit_BMP280::STANDBY_MS_500);
  }

  ahtReady_ = aht_.begin(&wire);
  if (!ahtReady_) {
    faults |= FAULT_AHT20;
  }

  mpuReady_ = mpu_.begin(0x68, &wire);
  if (!mpuReady_) {
    faults |= FAULT_MPU6050;
  } else {
    mpu_.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu_.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu_.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  return faults;
}

bool SensorManager::read(TelemetrySample& sample) {
  if (!(bmpReady_ && ahtReady_ && mpuReady_)) {
    return false;
  }

  sensors_event_t humidityEvent;
  sensors_event_t ahtTempEvent;
  sensors_event_t accelEvent;
  sensors_event_t gyroEvent;
  sensors_event_t mpuTempEvent;

  aht_.getEvent(&humidityEvent, &ahtTempEvent);
  mpu_.getEvent(&accelEvent, &gyroEvent, &mpuTempEvent);

  sample.temperatureC = ahtTempEvent.temperature;
  sample.humidityPct = humidityEvent.relative_humidity;
  sample.bmpTemperatureC = bmp_.readTemperature();
  sample.pressureHpa = bmp_.readPressure() / 100.0F;
  sample.altitudeM = bmp_.readAltitude(Config::SEA_LEVEL_PRESSURE_HPA);
  sample.accelX = accelEvent.acceleration.x;
  sample.accelY = accelEvent.acceleration.y;
  sample.accelZ = accelEvent.acceleration.z;
  sample.gyroX = gyroEvent.gyro.x;
  sample.gyroY = gyroEvent.gyro.y;
  sample.gyroZ = gyroEvent.gyro.z;

  const float magnitudeMs2 = sqrtf(sample.accelX * sample.accelX +
                                   sample.accelY * sample.accelY +
                                   sample.accelZ * sample.accelZ);
  sample.accelMagnitudeG = magnitudeMs2 / SENSORS_GRAVITY_STANDARD;
  sample.rollDeg = atan2f(sample.accelY, sample.accelZ) * 180.0F / PI;
  sample.pitchDeg = atan2f(-sample.accelX,
                          sqrtf(sample.accelY * sample.accelY +
                                sample.accelZ * sample.accelZ)) *
                    180.0F / PI;

  return isfinite(sample.temperatureC) && isfinite(sample.humidityPct) &&
         isfinite(sample.pressureHpa) && isfinite(sample.accelMagnitudeG);
}

