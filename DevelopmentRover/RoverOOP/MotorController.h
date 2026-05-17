#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>
#include "Component.h"

class MotorController : public Component {
private:
  int ENA, IN1, IN2;
  int ENB, IN3, IN4;

  int currentLeftMotor = 0;
  int currentRightMotor = 0;

  int maxSpeed;
  int accelStep;

  int rampMotor(int currentSpeed, int targetSpeed);

  void setMotorA(int speedVal);
  void setMotorB(int speedVal);

public:
  MotorController(
    int ena, int in1, int in2,
    int enb, int in3, int in4,
    int maxSpeed,
    int accelStep
  );

  void begin() override;

  void drive(int xRaw, int yRaw, int deadzone);

  // Used by autonomous mode
  void forward(int speedVal);
  void turnRight(int speedVal);
  void turnLeft(int speedVal);
  void backward(int speedVal);
  void stop();
};

#endif