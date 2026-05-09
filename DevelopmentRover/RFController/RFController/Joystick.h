#ifndef JOYSTICK_H
#define JOYSTICK_H

#include <Arduino.h>

class Joystick {
private:
  int xPin;
  int yPin;
  int swPin;

public:
  Joystick(int xPin, int yPin, int swPin);

  void begin();

  int readX();
  int readY();
  bool isPressed();
};

#endif