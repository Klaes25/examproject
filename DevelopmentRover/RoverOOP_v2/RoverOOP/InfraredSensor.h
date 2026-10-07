#ifndef INFRARED_SENSOR_H
#define INFRARED_SENSOR_H

#include <Arduino.h>
#include "Component.h"

class InfraredSensor : public Component {
private:
  int sensorPin;
  int lineState;

public:
  InfraredSensor(int sensorPin, int lineState = HIGH);

  void begin() override;

  bool isLineDetected();
  int getRawValue();
};

#endif