#include "Joystick.h"

Joystick::Joystick(int xPin, int yPin, int swPin) {
  this->xPin = xPin;
  this->yPin = yPin;
  this->swPin = swPin;
}

void Joystick::begin() {
  pinMode(swPin, INPUT_PULLUP);
}

int Joystick::readX() {
  return analogRead(xPin);
}

int Joystick::readY() {
  return analogRead(yPin);
}

bool Joystick::isPressed() {
  return digitalRead(swPin) == LOW;
}