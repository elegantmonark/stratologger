/*
 * High-altitude telemetry payload
 * Author: Trishan Biswas
 * Project started: February 2026
 * Status: Ongoing
 */

#include "DisplayManager.h"

#include <algorithm>
#include <math.h>

namespace {
constexpr int16_t SCREEN_W = 320;
constexpr int16_t SCREEN_H = 240;
constexpr float DEG_TO_RAD_F = PI / 180.0F;

float clampFloat(float value, float low, float high) {
  return std::max(low, std::min(value, high));
}

void formatDuration(uint32_t milliseconds, char* output, size_t outputSize) {
  const uint32_t seconds = milliseconds / 1000UL;
  const uint32_t hours = seconds / 3600UL;
  const uint32_t minutes = (seconds / 60UL) % 60UL;
  const uint32_t remainingSeconds = seconds % 60UL;
  snprintf(output, outputSize, "%02lu:%02lu:%02lu",
           static_cast<unsigned long>(hours),
           static_cast<unsigned long>(minutes),
           static_cast<unsigned long>(remainingSeconds));
}
}  // namespace

DisplayManager::DisplayManager() : frame_(&tft_) {}

bool DisplayManager::begin() {
  pinMode(Config::PIN_TFT_CS, OUTPUT);
  digitalWrite(Config::PIN_TFT_CS, HIGH);
  pinMode(Config::PIN_SD_CS, OUTPUT);
  digitalWrite(Config::PIN_SD_CS, HIGH);

  tft_.init();
  tft_.setRotation(1);
  tft_.fillScreen(TFT_BLACK);

  bg_ = tft_.color565(10, 10, 15);
  panel_ = tft_.color565(20, 22, 28);
  green_ = tft_.color565(0, 255, 136);
  amber_ = tft_.color565(255, 179, 0);
  red_ = tft_.color565(255, 59, 48);
  primary_ = tft_.color565(224, 224, 224);
  secondary_ = tft_.color565(136, 136, 136);
  grid_ = tft_.color565(45, 48, 56);
  cyan_ = tft_.color565(0, 190, 255);
  blue_ = tft_.color565(60, 110, 255);
  magenta_ = tft_.color565(230, 80, 255);

  // A full 8-bit frame is 75 KiB and prevents visible whole-screen flicker.
  frame_.setColorDepth(8);
  frameReady_ = frame_.createSprite(SCREEN_W, SCREEN_H) != nullptr;
  if (!frameReady_) {
    tft_.setTextColor(TFT_RED, TFT_BLACK);
    tft_.drawString("DISPLAY BUFFER FAILED", 10, 10, 2);
  }
  return frameReady_;
}

void DisplayManager::showBootMessage(const char* message) {
  if (!frameReady_) return;
  frame_.fillSprite(bg_);
  frame_.setTextColor(green_, bg_);
  frame_.setTextDatum(MC_DATUM);
  frame_.drawString("HIGH ALTITUDE PAYLOAD", SCREEN_W / 2, 85, 2);
  frame_.setTextColor(primary_, bg_);
  frame_.drawString(message, SCREEN_W / 2, 122, 2);
  frame_.pushSprite(0, 0);
}

void DisplayManager::capture(const TelemetrySample& sample) {
  if (sample.packetId == lastCapturedPacket_) return;
  lastCapturedPacket_ = sample.packetId;
  altitude_.push(sample.altitudeM);
  accelX_.push(sample.accelX);
  accelY_.push(sample.accelY);
  accelZ_.push(sample.accelZ);
  gyroX_.push(sample.gyroX);
  gyroY_.push(sample.gyroY);
  gyroZ_.push(sample.gyroZ);
}

void DisplayManager::render(const TelemetrySample& sample,
                            const SystemStats& stats, UiScreen screen) {
  if (!frameReady_) return;
  capture(sample);
  frame_.fillSprite(bg_);

  switch (screen) {
    case UiScreen::Live:
      drawLive(sample, stats);
      break;
    case UiScreen::Imu:
      drawImu(sample, stats);
      break;
    case UiScreen::System:
      drawSystem(sample, stats);
      break;
    default:
      break;
  }
  frame_.pushSprite(0, 0);
}

void DisplayManager::drawHeader(const char* title, const SystemStats& stats) {
  frame_.fillRect(0, 0, SCREEN_W, 20, panel_);
  frame_.setTextDatum(ML_DATUM);
  frame_.setTextColor(primary_, panel_);
  frame_.drawString(title, 5, 10, 2);
  frame_.setTextDatum(MR_DATUM);
  frame_.setTextColor(stats.sdLogging ? green_ : red_, panel_);
  frame_.drawString(stats.sdLogging ? "SD LOG" : "SD ERR", 315, 10, 2);
}

void DisplayManager::drawArcGauge(int16_t cx, int16_t cy, int16_t radius,
                                  float value) {
  const float normalized = clampFloat(
      (value - Config::ALTITUDE_GAUGE_MIN_M) /
          (Config::ALTITUDE_GAUGE_MAX_M - Config::ALTITUDE_GAUGE_MIN_M),
      0.0F, 1.0F);
  const uint16_t activeColor =
      normalized < 0.70F ? green_ : (normalized < 0.90F ? amber_ : red_);
  constexpr float startDeg = 140.0F;
  constexpr float sweepDeg = 260.0F;
  const float activeEnd = startDeg + sweepDeg * normalized;

  for (int angle = static_cast<int>(startDeg);
       angle <= static_cast<int>(startDeg + sweepDeg); angle += 3) {
    const float radians = angle * DEG_TO_RAD_F;
    const uint16_t color = angle <= activeEnd ? activeColor : grid_;
    for (int thickness = 0; thickness < 5; ++thickness) {
      const int16_t r = radius - thickness;
      frame_.drawPixel(cx + lroundf(cosf(radians) * r),
                       cy + lroundf(sinf(radians) * r), color);
    }
  }
}

void DisplayManager::drawGraph(int16_t x, int16_t y, int16_t w, int16_t h,
                               const GraphBuffer& values, uint16_t color,
                               const char* label) {
  frame_.drawRect(x, y, w, h, grid_);
  frame_.setTextDatum(TL_DATUM);
  frame_.setTextColor(secondary_, bg_);
  frame_.drawString(label, x + 3, y + 2, 1);

  if (values.size() < 2) return;
  float minimum = INFINITY;
  float maximum = -INFINITY;
  for (size_t i = 0; i < values.size(); ++i) {
    const float value = values.oldestAt(i);
    if (isfinite(value)) {
      minimum = std::min(minimum, value);
      maximum = std::max(maximum, value);
    }
  }
  if (!isfinite(minimum) || !isfinite(maximum)) return;
  if (maximum - minimum < 0.01F) {
    maximum += 0.5F;
    minimum -= 0.5F;
  } else {
    const float padding = (maximum - minimum) * 0.08F;
    maximum += padding;
    minimum -= padding;
  }

  const int16_t plotTop = y + 12;
  const int16_t plotBottom = y + h - 3;
  const int16_t plotHeight = std::max<int16_t>(1, plotBottom - plotTop);
  int16_t previousX = x + 2;
  int16_t previousY = plotBottom;
  bool havePrevious = false;
  for (size_t i = 0; i < values.size(); ++i) {
    const float value = values.oldestAt(i);
    if (!isfinite(value)) {
      havePrevious = false;
      continue;
    }
    const int16_t px = x + 2 + static_cast<int16_t>(
                                  (w - 5) * i / std::max<size_t>(1, values.size() - 1));
    const int16_t py = plotBottom - static_cast<int16_t>(
                                      (value - minimum) * plotHeight /
                                      (maximum - minimum));
    if (havePrevious) frame_.drawLine(previousX, previousY, px, py, color);
    previousX = px;
    previousY = py;
    havePrevious = true;
  }
}

void DisplayManager::drawCard(int16_t x, int16_t y, int16_t w, int16_t h,
                              const char* label, const char* value,
                              uint16_t valueColor) {
  frame_.fillRoundRect(x, y, w, h, 3, panel_);
  frame_.setTextDatum(ML_DATUM);
  frame_.setTextColor(secondary_, panel_);
  frame_.drawString(label, x + 4, y + h / 2, 2);
  frame_.setTextDatum(MR_DATUM);
  frame_.setTextColor(valueColor, panel_);
  frame_.drawString(value, x + w - 4, y + h / 2, 2);
}

void DisplayManager::drawHorizon(int16_t x, int16_t y, int16_t w, int16_t h,
                                 float rollDeg, float pitchDeg) {
  frame_.drawRoundRect(x, y, w, h, 4, grid_);
  const int16_t cx = x + w / 2;
  const int16_t cy = y + h / 2;
  const float roll = clampFloat(rollDeg, -60.0F, 60.0F) * DEG_TO_RAD_F;
  const float pitchOffset = clampFloat(pitchDeg, -30.0F, 30.0F) * h / 75.0F;
  const float halfLength = std::min(w, h) * 0.38F;
  const float dx = cosf(roll) * halfLength;
  const float dy = sinf(roll) * halfLength;
  frame_.drawLine(lroundf(cx - dx), lroundf(cy + pitchOffset - dy),
                  lroundf(cx + dx), lroundf(cy + pitchOffset + dy), cyan_);
  frame_.drawFastHLine(cx - 8, cy, 17, primary_);
  frame_.drawFastVLine(cx, cy - 3, 7, primary_);
}

void DisplayManager::drawLive(const TelemetrySample& sample,
                              const SystemStats& stats) {
  drawHeader("LIVE TELEMETRY", stats);
  drawArcGauge(94, 78, 53, sample.altitudeM);

  char text[32];
  snprintf(text, sizeof(text), "%.1f", sample.altitudeM);
  frame_.setTextDatum(MC_DATUM);
  frame_.setTextColor(green_, bg_);
  frame_.drawString(text, 94, 72, 4);
  frame_.setTextColor(secondary_, bg_);
  frame_.drawString("ALTITUDE m", 94, 96, 2);
  drawGraph(4, 127, 184, 109, altitude_, green_, "ALT / LAST 60 s");

  snprintf(text, sizeof(text), "%.1f C", sample.temperatureC);
  drawCard(194, 24, 122, 24, "TEMP", text, primary_);
  snprintf(text, sizeof(text), "%.0f %%", sample.humidityPct);
  drawCard(194, 51, 122, 24, "HUM", text, primary_);
  snprintf(text, sizeof(text), "%.0f", sample.pressureHpa);
  drawCard(194, 78, 122, 24, "hPa", text, primary_);
  formatDuration(stats.uptimeMs, text, sizeof(text));
  drawCard(194, 105, 122, 24, "TIME", text, primary_);
  snprintf(text, sizeof(text), "%.2f g", sample.accelMagnitudeG);
  drawCard(194, 132, 122, 24, "LOAD", text,
           sample.accelMagnitudeG > 2.0F ? red_ : green_);
  drawHorizon(194, 160, 122, 55, sample.rollDeg, sample.pitchDeg);

  frame_.setTextDatum(BL_DATUM);
  frame_.setTextColor(secondary_, bg_);
  snprintf(text, sizeof(text), "PKT %lu",
           static_cast<unsigned long>(sample.packetId));
  frame_.drawString(text, 196, 238, 1);
  frame_.setTextDatum(BR_DATUM);
  frame_.setTextColor(stats.sdLogging ? green_ : red_, bg_);
  frame_.drawString(stats.logFileName, 316, 238, 1);
}

void DisplayManager::drawMagnitudeBar(int16_t x, int16_t y, int16_t w,
                                      float magnitudeG, float peakG) {
  const float fraction = clampFloat(magnitudeG / 4.0F, 0.0F, 1.0F);
  const uint16_t color = magnitudeG > 2.0F ? red_ : green_;
  frame_.drawRect(x, y, w, 12, grid_);
  frame_.fillRect(x + 2, y + 2, static_cast<int16_t>((w - 4) * fraction), 8,
                  color);
  char text[40];
  snprintf(text, sizeof(text), "MAG %.2f g   PEAK %.2f g", magnitudeG,
           peakG);
  frame_.setTextDatum(ML_DATUM);
  frame_.setTextColor(primary_, bg_);
  frame_.drawString(text, x, y + 23, 2);
}

void DisplayManager::drawImu(const TelemetrySample& sample,
                             const SystemStats& stats) {
  drawHeader("IMU DETAIL", stats);
  constexpr int16_t plotW = 154;
  constexpr int16_t plotH = 54;
  drawGraph(4, 23, plotW, plotH, accelX_, red_, "ACC X  m/s2");
  drawGraph(162, 23, plotW, plotH, gyroX_, red_, "GYRO X  rad/s");
  drawGraph(4, 80, plotW, plotH, accelY_, green_, "ACC Y  m/s2");
  drawGraph(162, 80, plotW, plotH, gyroY_, green_, "GYRO Y  rad/s");
  drawGraph(4, 137, plotW, plotH, accelZ_, blue_, "ACC Z  m/s2");
  drawGraph(162, 137, plotW, plotH, gyroZ_, blue_, "GYRO Z  rad/s");
  drawMagnitudeBar(5, 196, 310, sample.accelMagnitudeG, stats.peakG);
}

void DisplayManager::drawSystem(const TelemetrySample& sample,
                                const SystemStats& stats) {
  drawHeader("SYSTEM STATUS", stats);
  char left[64];
  char right[64];
  int16_t y = 28;

  auto row = [&](const char* label, const char* value, uint16_t color) {
    frame_.setTextDatum(TL_DATUM);
    frame_.setTextColor(secondary_, bg_);
    frame_.drawString(label, 7, y, 2);
    frame_.setTextDatum(TR_DATUM);
    frame_.setTextColor(color, bg_);
    frame_.drawString(value, 313, y, 2);
    frame_.drawFastHLine(7, y + 18, 306, grid_);
    y += 21;
  };

  snprintf(right, sizeof(right), "AHT %.2f C / %.2f %%", sample.temperatureC,
           sample.humidityPct);
  row("ENVIRONMENT", right, primary_);
  snprintf(right, sizeof(right), "BMP %.2f C / %.2f hPa",
           sample.bmpTemperatureC, sample.pressureHpa);
  row("BAROMETER", right, primary_);
  snprintf(right, sizeof(right), "%.3f  %.3f  %.3f", sample.accelX,
           sample.accelY, sample.accelZ);
  row("ACCEL XYZ", right, sample.accelMagnitudeG > 2.0F ? red_ : primary_);
  snprintf(right, sizeof(right), "%.3f  %.3f  %.3f", sample.gyroX,
           sample.gyroY, sample.gyroZ);
  row("GYRO XYZ", right, primary_);
  snprintf(right, sizeof(right), "%.2f V", stats.batteryVoltage);
  row("BATTERY", right,
      stats.batteryVoltage < Config::BATTERY_EMPTY_V ? red_ : green_);
  snprintf(right, sizeof(right), "%.1f / %.1f MiB",
           stats.sdFreeBytes / 1048576.0, stats.sdTotalBytes / 1048576.0);
  row("SD FREE / TOTAL", right, stats.sdLogging ? green_ : red_);
  formatDuration(stats.uptimeMs, right, sizeof(right));
  row("UPTIME", right, primary_);
  const uint32_t totalSlots = sample.packetId + stats.droppedDeadlines;
  const float lossRate = totalSlots == 0
                             ? 0.0F
                             : 100.0F * stats.droppedDeadlines / totalSlots;
  snprintf(right, sizeof(right), "%.2f%% / %lu / %lu", lossRate,
           static_cast<unsigned long>(stats.checksumErrors),
           static_cast<unsigned long>(stats.logWriteErrors));
  row("LOSS / CRC / WRITE", right,
      (stats.droppedDeadlines || stats.checksumErrors || stats.logWriteErrors)
          ? amber_
          : green_);

  snprintf(left, sizeof(left), "ALT %.2f m", sample.altitudeM);
  frame_.setTextDatum(BL_DATUM);
  frame_.setTextColor(green_, bg_);
  frame_.drawString(left, 7, 238, 2);
  snprintf(right, sizeof(right), "ROLL %.1f  PITCH %.1f", sample.rollDeg,
           sample.pitchDeg);
  frame_.setTextDatum(BR_DATUM);
  frame_.setTextColor(primary_, bg_);
  frame_.drawString(right, 313, 238, 2);
}

