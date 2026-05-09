#include "RobotArm.h"

RobotArm::RobotArm(int basePin, int shoulderPin, int elbowPin, int wristPin)
  : basePin(basePin), shoulderPin(shoulderPin), elbowPin(elbowPin), wristPin(wristPin) {}

void RobotArm::begin() {
  baseServo.attach(basePin);
  shoulderServo.attach(shoulderPin);
  elbowServo.attach(elbowPin);
  wristServo.attach(wristPin);

  baseServo.write(basePos);
  updateArmFromExtension();
  wristServo.write(45);
}

void RobotArm::control(int xValue, int yValue, bool buttonState, int deadzone) {
  int x = yValue - CENTER;
  int y = -(xValue - CENTER);

  if (abs(x) > deadzone) {
    int stepSize = map(abs(x), deadzone, 511, 1, 3);

    if (x > 0) basePos += stepSize;
    else basePos -= stepSize;
  }

  basePos = constrain(basePos, 0, 180);
  baseServo.write(basePos);

  if (abs(y) > deadzone) {
    int stepSize = map(abs(y), deadzone, 511, 1, 2);

    if (y < 0) extension += stepSize;
    else extension -= stepSize;
  }

  extension = constrain(extension, 0, 180);
  updateArmFromExtension();

  if (!lastButtonState && buttonState) {
    wristClosed = !wristClosed;

    if (wristClosed) wristServo.write(0);
    else wristServo.write(45);
  }

  lastButtonState = buttonState;
}

void RobotArm::updateArmFromExtension() {
  int shoulderPos = map(extension, 0, 180, 140, 60);
  int elbowPos = map(extension, 0, 180, 60, 140);

  shoulderPos = constrain(shoulderPos, 20, 160);
  elbowPos = constrain(elbowPos, 20, 160);

  shoulderServo.write(shoulderPos);
  elbowServo.write(elbowPos);
}