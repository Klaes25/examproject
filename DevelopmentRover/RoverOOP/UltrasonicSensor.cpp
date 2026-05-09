#include "UltrasonicSensor.h"

UltrasonicSensor::UltrasonicSensor(int trigPin, int echoPin, unsigned long interval)
  : trigPin(trigPin), echoPin(echoPin), interval(interval) {}

void UltrasonicSensor::begin() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  digitalWrite(trigPin, LOW);
}

void UltrasonicSensor::update() {
  if (millis() - lastReadTime > interval) {
    lastReadTime = millis();

    // Send 10 microsecond trigger pulse
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);

    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);

    digitalWrite(trigPin, LOW);

    // Measure echo duration
    long duration = pulseIn(echoPin, HIGH, 30000);

    if (duration > 0) {
      // Convert time to distance in cm
      distanceCm = duration * 0.0343 / 2.0;
    }
  }
}

float UltrasonicSensor::getDistanceCm() {
  return distanceCm;
}

bool UltrasonicSensor::isObstacleClose(float thresholdCm) {
  return distanceCm > 0 && distanceCm < thresholdCm;
}