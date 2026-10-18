/*
 * Stratologger
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#pragma once

#include <TFT_eSPI.h>

#include <array>

#include "config.h"
#include "telemetry_types.h"

template <size_t N>
class FloatRingBuffer {
 public:
  void push(float value) {
    values_[head_] = value;
    head_ = (head_ + 1U) % N;
    if (count_ < N) ++count_;
  }

  size_t size() const { return count_; }

  float oldestAt(size_t index) const {
    const size_t start = count_ == N ? head_ : 0;
    return values_[(start + index) % N];
  }

 private:
  std::array<float, N> values_{};
  size_t head_ = 0;
  size_t count_ = 0;
};

class DisplayManager {
 public:
  DisplayManager();

  bool begin();
  void showBootMessage(const char* message);
  void render(const TelemetrySample& sample, const SystemStats& stats,
              UiScreen screen);

 private:
  using GraphBuffer = FloatRingBuffer<Config::GRAPH_POINTS>;

  void capture(const TelemetrySample& sample);
  void drawHeader(const char* title, const SystemStats& stats);
  void drawLive(const TelemetrySample& sample, const SystemStats& stats);
  void drawImu(const TelemetrySample& sample, const SystemStats& stats);
  void drawSystem(const TelemetrySample& sample, const SystemStats& stats);
  void drawArcGauge(int16_t cx, int16_t cy, int16_t radius, float value);
  void drawGraph(int16_t x, int16_t y, int16_t w, int16_t h,
                 const GraphBuffer& values, uint16_t color,
                 const char* label);
  void drawCard(int16_t x, int16_t y, int16_t w, int16_t h,
                const char* label, const char* value, uint16_t valueColor);
  void drawHorizon(int16_t x, int16_t y, int16_t w, int16_t h,
                   float rollDeg, float pitchDeg);
  void drawMagnitudeBar(int16_t x, int16_t y, int16_t w, float magnitudeG,
                        float peakG);

  TFT_eSPI tft_;
  TFT_eSprite frame_;
  bool frameReady_ = false;
  uint32_t lastCapturedPacket_ = UINT32_MAX;

  uint16_t bg_ = TFT_BLACK;
  uint16_t panel_ = TFT_DARKGREY;
  uint16_t green_ = TFT_GREEN;
  uint16_t amber_ = TFT_YELLOW;
  uint16_t red_ = TFT_RED;
  uint16_t primary_ = TFT_WHITE;
  uint16_t secondary_ = TFT_LIGHTGREY;
  uint16_t grid_ = TFT_DARKGREY;
  uint16_t cyan_ = TFT_CYAN;
  uint16_t blue_ = TFT_BLUE;
  uint16_t magenta_ = TFT_MAGENTA;

  GraphBuffer altitude_;
  GraphBuffer accelX_;
  GraphBuffer accelY_;
  GraphBuffer accelZ_;
  GraphBuffer gyroX_;
  GraphBuffer gyroY_;
  GraphBuffer gyroZ_;
};

