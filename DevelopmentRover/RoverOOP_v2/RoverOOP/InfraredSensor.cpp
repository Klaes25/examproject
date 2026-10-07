#include "InfraredSensor.h"

InfraredSensor::InfraredSensor(int sensorPin, int lineState)
  : sensorPin(sensorPin),
    lineState(lineState) {
}

void InfraredSensor::begin() {
  pinMode(sensorPin, INPUT_PULLUP);
}

bool InfraredSensor::isLineDetected() {
  return digitalRead(sensorPin) == lineState;
}

int InfraredSensor::getRawValue() {
  return digitalRead(sensorPin);
}