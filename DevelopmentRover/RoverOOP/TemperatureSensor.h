#ifndef TEMPERATURE_SENSOR_H
#define TEMPERATURE_SENSOR_H

#include <Arduino.h>
#include <DHT.h>
#include "Component.h"

class TemperatureSensor : public Component {
private:
  DHT dht;

  unsigned long lastReadTime = 0;
  unsigned long interval;

  float temperatureC = 0;

public:
  TemperatureSensor(uint8_t pin, uint8_t type, unsigned long interval);

  void begin() override;

  void update();

  float getTemperature();
};

#endif