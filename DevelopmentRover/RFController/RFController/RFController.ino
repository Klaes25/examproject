#include "Joystick.h"
#include "ControllerDisplay.h"
#include "RFCommunication.h"
#include "Packets.h"

// Rover joystick
Joystick roverJoystick(A2, A3, 3);

// Arm joystick
Joystick armJoystick(A0, A1, 2);

// LCD
ControllerDisplay display;

// RF
RFCommunication rf;

ControlPacket controlData;
SensorPacket sensorData;

float lastTemperature = 0.0;
bool hasTemperature = false;

void setup() {
  Serial.begin(9600);

  roverJoystick.begin();
  armJoystick.begin();

  display.begin();
  display.showStartup();

  if (!rf.begin()) {
    Serial.println("NRF not responding on controller");
    display.showNRFError();
    while (1);
  }

  Serial.println("Controller ready");

  delay(1000);
}

void loop() {
  readJoysticks();

  bool radioOK = rf.sendControlData(controlData);

  if (rf.readSensorData(sensorData)) {
    lastTemperature = sensorData.temperatureC;
    hasTemperature = true;

    Serial.print("Temp: ");
    Serial.print(lastTemperature);
    Serial.println(" C");
  }

  display.update(lastTemperature, hasTemperature, radioOK);

  delay(20);
}

void readJoysticks() {
  controlData.roverX = roverJoystick.readX();
  controlData.roverY = roverJoystick.readY();
  controlData.roverSW = roverJoystick.isPressed();

  controlData.armX = armJoystick.readX();
  controlData.armY = armJoystick.readY();
  controlData.armSW = armJoystick.isPressed();
}