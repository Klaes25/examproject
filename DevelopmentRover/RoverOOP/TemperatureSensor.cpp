#include "TemperatureSensor.h"

TemperatureSensor::TemperatureSensor(uint8_t pin, uint8_t type, unsigned long interval)
  : dht(pin, type), interval(interval) {}

void TemperatureSensor::begin() {
  dht.begin();
}

void TemperatureSensor::update() {

  if (millis() - lastReadTime > interval) {

    lastReadTime = millis();

    float t = dht.readTemperature();

    if (!isnan(t)) {
      temperatureC = t;
    }
  }
}

float TemperatureSensor::getTemperature() {
  return temperatureC;
}