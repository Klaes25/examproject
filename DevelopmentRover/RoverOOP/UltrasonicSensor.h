#ifndef ULTRASONIC_SENSOR_H
#define ULTRASONIC_SENSOR_H

#include <Arduino.h>
#include "Component.h"

class UltrasonicSensor : public Component {
private:
  int trigPin;
  int echoPin;

  unsigned long lastReadTime = 0;
  unsigned long interval;

  float distanceCm = 0;

public:
  UltrasonicSensor(int trigPin, int echoPin, unsigned long interval);

  void begin() override;

  // Reads distance at fixed intervals
  void update();

  // Returns latest distance in cm
  float getDistanceCm();

  // True if an object is closer than threshold
  bool isObstacleClose(float thresholdCm);
};

#endif