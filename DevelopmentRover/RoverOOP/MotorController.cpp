#include "MotorController.h"

MotorController::MotorController(int ena, int in1, int in2, int enb, int in3, int in4, int maxSpeed, int accelStep)
  : ENA(ena), IN1(in1), IN2(in2), ENB(enb), IN3(in3), IN4(in4),
    maxSpeed(maxSpeed), accelStep(accelStep) {}

void MotorController::begin() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stop();
}

void MotorController::drive(int xRaw, int yRaw, int deadzone) {
  int x = map(xRaw, 0, 1023, -maxSpeed, maxSpeed);
  int y = map(yRaw, 0, 1023, -maxSpeed, maxSpeed);

  if (abs(x) < deadzone) x = 0;
  if (abs(y) < deadzone) y = 0;

  int targetLeft = constrain(y + x, -maxSpeed, maxSpeed);
  int targetRight = constrain(y - x, -maxSpeed, maxSpeed);

  currentLeftMotor = rampMotor(currentLeftMotor, targetLeft);
  currentRightMotor = rampMotor(currentRightMotor, targetRight);

  setMotorA(currentLeftMotor);
  setMotorB(currentRightMotor);
}

int MotorController::rampMotor(int currentSpeed, int targetSpeed) {
  if (currentSpeed < targetSpeed) {
    currentSpeed += accelStep;
    if (currentSpeed > targetSpeed) currentSpeed = targetSpeed;
  } else if (currentSpeed > targetSpeed) {
    currentSpeed -= accelStep;
    if (currentSpeed < targetSpeed) currentSpeed = targetSpeed;
  }

  return currentSpeed;
}

void MotorController::setMotorA(int speedVal) {
  if (speedVal > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, speedVal);
  } else if (speedVal < 0) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, -speedVal);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
  }
}

void MotorController::setMotorB(int speedVal) {
  if (speedVal > 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, speedVal);
  } else if (speedVal < 0) {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, -speedVal);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 0);
  }
}

void MotorController::stop() {
  currentLeftMotor = 0;
  currentRightMotor = 0;

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}