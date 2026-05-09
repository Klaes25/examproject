#include <Arduino.h>

#include "MotorController.h"
#include "RobotArm.h"
#include "RadioReceiver.h"
#include "TemperatureSensor.h"
#include "UltrasonicSensor.h"

const byte address[6] = "ROV01";

RadioReceiver radio(A2, A1, address);

// Motor settings
const int MAX_SPEED = 255;
const int ACCEL_STEP = 32;

const int DEADZONE_ROVER = 80;
const int DEADZONE_ARM = 80;

// Lower speed for autonomous driving
const int AUTO_SPEED = 100;
const int TURN_SPEED = 90;

// Obstacle settings
const float OBSTACLE_DISTANCE_CM = 25.0;

// Autonomous timing
const unsigned long STOP_TIME = 250;
const unsigned long DRIVE_SHORT_TIME = 600;
const unsigned long CORRECT_LEFT_TIME = 350;

// Sensor intervals
const unsigned long DHT_INTERVAL = 2000;
const unsigned long ULTRASONIC_INTERVAL = 80;

// Safety
const unsigned long SIGNAL_TIMEOUT = 500;

unsigned long lastReceiveTime = 0;
unsigned long autoStateStartTime = 0;

bool autonomousMode = false;
bool lastRoverButtonState = false;

SensorPacket sensorData;

MotorController motors(
  5, 7, 4,
  6, 3, 2,
  MAX_SPEED,
  ACCEL_STEP
);

RobotArm arm(
  8,
  9,
  10,
  A0
);

TemperatureSensor temperatureSensor(
  A3,
  DHT22,
  DHT_INTERVAL
);

UltrasonicSensor ultrasonic(
  A4,
  A5,
  ULTRASONIC_INTERVAL
);

enum AutoState {
  AUTO_FORWARD,
  AUTO_STOP,
  AUTO_TURN_RIGHT_UNTIL_CLEAR,
  AUTO_DRIVE_SHORT,
  AUTO_CORRECT_LEFT
};

AutoState autoState = AUTO_FORWARD;

void setup() {
  Serial.begin(9600);

  motors.begin();
  arm.begin();
  radio.begin();
  temperatureSensor.begin();
  ultrasonic.begin();

  lastReceiveTime = millis();

  Serial.println("Rover ready");
}

void loop() {
  temperatureSensor.update();
  ultrasonic.update();

  sensorData.temperatureC = temperatureSensor.getTemperature();

  if (radio.available()) {
    radio.readData();
    lastReceiveTime = millis();

    // Drive joystick button toggles autonomous mode
    if (!lastRoverButtonState && radio.data.roverSW) {
      autonomousMode = !autonomousMode;

      motors.stop();
      autoState = AUTO_FORWARD;
      autoStateStartTime = millis();

      Serial.print("Autonomous mode: ");
      Serial.println(autonomousMode ? "ON" : "OFF");
    }

    lastRoverButtonState = radio.data.roverSW;

    if (autonomousMode) {
      runAutonomousMode();
    } else {
      motors.drive(
        radio.data.roverX,
        radio.data.roverY,
        DEADZONE_ROVER
      );
    }

    // Arm joystick button controls wrist toggle inside RobotArm class
    arm.control(
      radio.data.armX,
      radio.data.armY,
      radio.data.armSW,
      DEADZONE_ARM
    );

    radio.sendSensorData(sensorData);
  }

  if (millis() - lastReceiveTime > SIGNAL_TIMEOUT) {
    motors.stop();
  }

  delay(20);
}

void runAutonomousMode() {
  unsigned long now = millis();

  switch (autoState) {

    case AUTO_FORWARD:
      // Drive forward until obstacle is detected
      if (ultrasonic.isObstacleClose(OBSTACLE_DISTANCE_CM)) {
        motors.stop();
        autoState = AUTO_STOP;
        autoStateStartTime = now;
      } else {
        motors.forward(AUTO_SPEED);
      }
      break;

    case AUTO_STOP:
      // Short stop before avoiding obstacle
      motors.stop();

      if (now - autoStateStartTime >= STOP_TIME) {
        autoState = AUTO_TURN_RIGHT_UNTIL_CLEAR;
        autoStateStartTime = now;
      }
      break;

    case AUTO_TURN_RIGHT_UNTIL_CLEAR:
      // Turn right slowly until the path is clear
      if (ultrasonic.isObstacleClose(OBSTACLE_DISTANCE_CM)) {
        motors.turnRight(TURN_SPEED);
      } else {
        autoState = AUTO_DRIVE_SHORT;
        autoStateStartTime = now;
      }
      break;

    case AUTO_DRIVE_SHORT:
      // Drive a little forward after avoiding obstacle
      if (ultrasonic.isObstacleClose(OBSTACLE_DISTANCE_CM)) {
        motors.stop();
        autoState = AUTO_STOP;
        autoStateStartTime = now;
      } else {
        motors.forward(AUTO_SPEED);

        if (now - autoStateStartTime >= DRIVE_SHORT_TIME) {
          autoState = AUTO_CORRECT_LEFT;
          autoStateStartTime = now;
        }
      }
      break;

    case AUTO_CORRECT_LEFT:
      // Turn slightly left to return closer to original direction
      motors.turnLeft(TURN_SPEED);

      if (now - autoStateStartTime >= CORRECT_LEFT_TIME) {
        autoState = AUTO_FORWARD;
        autoStateStartTime = now;
      }
      break;
  }
}