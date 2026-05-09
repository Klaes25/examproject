#ifndef CONTROLLER_DISPLAY_H
#define CONTROLLER_DISPLAY_H

#include <Arduino.h>
#include <LiquidCrystal.h>

class ControllerDisplay {
private:
  LiquidCrystal lcd;
  unsigned long lastLCDUpdate;

public:
  ControllerDisplay();

  void begin();
  void showStartup();
  void showNRFError();
  void update(float temperature, bool hasTemperature, bool radioOK);
};

#endif