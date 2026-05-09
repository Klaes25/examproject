#ifndef ROBOT_ARM_H
#define ROBOT_ARM_H

#include <Arduino.h>
#include <Servo.h>
#include "Component.h"

class RobotArm : public Component {
private:
  Servo baseServo;
  Servo shoulderServo;
  Servo elbowServo;
  Servo wristServo;

  int basePin, shoulderPin, elbowPin, wristPin;

  int basePos = 90;
  int extension = 90;

  bool wristClosed = false;
  bool lastButtonState = false;

  const int CENTER = 512;

  void updateArmFromExtension();

public:
  RobotArm(int basePin, int shoulderPin, int elbowPin, int wristPin);

  void begin() override;
  void control(int xValue, int yValue, bool buttonState, int deadzone);
};

#endif