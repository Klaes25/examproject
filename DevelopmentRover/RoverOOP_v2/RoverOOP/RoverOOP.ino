#include <Arduino.h>

#include "MotorController.h"
#include "RadioReceiver.h"
#include "TemperatureSensor.h"
#include "UltrasonicSensor.h"
#include "InfraredSensor.h"

const byte address[6] = "ROV01";

RadioReceiver radio(A2, A1, address);

// Motor settings
const int MAX_SPEED = 255;
const int ACCEL_STEP = 20;

const int DEADZONE_ROVER = 80;

// Lower speed for autonomous driving
const int AUTO_SPEED = 100;
const int TURN_SPEED = 90;

// Line follow speed
const int LINE_SPEED = 80;
const int LINE_CORRECTION = 30;

// Obstacle settings
const float OBSTACLE_DISTANCE_CM = 35.0;

// Autonomous timing
const unsigned long STOP_TIME = 250;
const unsigned long DRIVE_SHORT_TIME = 600;
const unsigned long CORRECT_LEFT_TIME = 350;

// Sensor intervals
const unsigned long DHT_INTERVAL = 2000;
const unsigned long ULTRASONIC_INTERVAL = 80;

// Safety
const unsigned long SIGNAL_TIMEOUT = 500;

// 90-degree turn timing (kalibreres)
const unsigned long TURN_90_TIME = 600;

unsigned long lastReceiveTime = 0;
unsigned long autoStateStartTime = 0;

enum DriveMode {
  MANUAL_MODE,
  OBSTACLE_AUTO_MODE,
  LINE_FOLLOW_MODE
};

DriveMode driveMode = MANUAL_MODE;

bool lastRoverButtonState = false;
bool lastArmButtonState = false;
bool lastSerialRoverButtonState = false;

SensorPacket sensorData;

// ENA, IN1, IN2
// ENB, IN3, IN4
MotorController motors(
  5, 7, 4,
  6, 3, 2,
  MAX_SPEED,
  ACCEL_STEP
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

// KY-033 OUT connected to D8
// Change HIGH to LOW if detection is reversed
const int LINE_STATE = LOW;

InfraredSensor leftInfrared(
  9,
  LINE_STATE
);

InfraredSensor rightInfrared(
  8,
  LINE_STATE
);

enum AutoState {
  AUTO_FORWARD,
  AUTO_STOP,
  AUTO_TURN_RIGHT_UNTIL_CLEAR,
  AUTO_DRIVE_SHORT,
  AUTO_CORRECT_LEFT
};

AutoState autoState = AUTO_FORWARD;

// 90-degree turn state machine
enum TurnState {
  TURN_IDLE,
  TURN_RIGHT_90,
  TURN_LEFT_90
};

TurnState turnState = TURN_IDLE;
unsigned long turnStateStartTime = 0;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(20);

  motors.begin();
  radio.begin();
  temperatureSensor.begin();
  ultrasonic.begin();
  leftInfrared.begin();
  rightInfrared.begin();

  lastReceiveTime = millis();

  Serial.println("Rover ready");
}

void loop() {
  readSerialControl();

  temperatureSensor.update();
  ultrasonic.update();

  sensorData.temperatureC = temperatureSensor.getTemperature();
  sensorData.humidity = temperatureSensor.getHumidity();

  static unsigned long lastPrint = 0;

  if (millis() - lastPrint > 2000) {
    lastPrint = millis();

    Serial.print("SENSOR:TEMP:");
    Serial.println(sensorData.temperatureC);

    Serial.print("SENSOR:HUM:");
    Serial.println(sensorData.humidity);

    Serial.print("SENSOR:DIST:");
    Serial.println(ultrasonic.getDistanceCm());
   
    Serial.print("SENSOR:IR LEFT RAW:");
    Serial.println(leftInfrared.getRawValue());

    Serial.print("SENSOR:IR RIGHT RAW:");
    Serial.println(rightInfrared.getRawValue());
  }


  if (radio.available()) {
    radio.readData();
    lastReceiveTime = millis();

// Rover joystick button toggles obstacle autonomous mode
    if (!lastRoverButtonState && radio.data.roverSW) {

      if (driveMode == OBSTACLE_AUTO_MODE) {
        driveMode = MANUAL_MODE;
      } else {
        driveMode = OBSTACLE_AUTO_MODE;
      }

      motors.stop();

      autoState = AUTO_FORWARD;
      autoStateStartTime = millis();

      Serial.print("Obstacle auto mode: ");
      Serial.println(
        driveMode == OBSTACLE_AUTO_MODE ? "ON" : "OFF"
      );
    }

    lastRoverButtonState = radio.data.roverSW;

// Other joystick button toggles line-follow mode
    if (!lastArmButtonState && radio.data.armSW) {

      if (driveMode == LINE_FOLLOW_MODE) {
        driveMode = MANUAL_MODE;
      } else {
        driveMode = LINE_FOLLOW_MODE;
      }

      motors.stop();

      Serial.print("Line follow mode: ");
      Serial.println(
        driveMode == LINE_FOLLOW_MODE ? "ON" : "OFF"
      );
    }

    lastArmButtonState = radio.data.armSW;

// Joystick drives only in manual mode
    if (driveMode == MANUAL_MODE && !isTurning()) {
      motors.drive(
        radio.data.roverX,
        radio.data.roverY,
        DEADZONE_ROVER
      );
    }

    radio.sendSensorData(sensorData);
  }

  updateTurn90();

  if (driveMode == OBSTACLE_AUTO_MODE) {
    runAutonomousMode();
  }
  else if (driveMode == LINE_FOLLOW_MODE) {
    runLineFollowMode();
  }

  if (millis() - lastReceiveTime > SIGNAL_TIMEOUT) {
    motors.stop();
  }

  delay(20);
}

void runLineFollowMode() {
  bool leftLine = leftInfrared.isLineDetected();
  bool rightLine = rightInfrared.isLineDetected();

  if (!leftLine && !rightLine) {
    // Neither sensor sees black -> continue forward
    motors.backward(LINE_SPEED);
  }
  else if (leftLine && !rightLine) {
    // Left sensor sees black -> gently correct left
    motors.curveLeft(LINE_SPEED, LINE_CORRECTION);
  }
  else if (!leftLine && rightLine) {
    // Right sensor sees black -> gently correct right
    motors.curveRight(LINE_SPEED, LINE_CORRECTION);
  }
  else {
    // Both sensors see black -> stop for safety
    motors.stop();
  }
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
        motors.backward(AUTO_SPEED); // actually forward, motors are reversed
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
        motors.backward(AUTO_SPEED); // actually forward, motors are reversed

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

// ---- 90-degree turn state machine ----

void startTurn90Right() {
  turnState = TURN_RIGHT_90;
  turnStateStartTime = millis();
}

void startTurn90Left() {
  turnState = TURN_LEFT_90;
  turnStateStartTime = millis();
}

bool isTurning() {
  return turnState != TURN_IDLE;
}

void updateTurn90() {
  unsigned long now = millis();

  switch (turnState) {

    case TURN_IDLE:
      break;

    case TURN_RIGHT_90:
      motors.turnRight(TURN_SPEED);

      if (now - turnStateStartTime >= TURN_90_TIME) {
        motors.stop();
        turnState = TURN_IDLE;
      }
      break;

    case TURN_LEFT_90:
      motors.turnLeft(TURN_SPEED);

      if (now - turnStateStartTime >= TURN_90_TIME) {
        motors.stop();
        turnState = TURN_IDLE;
      }
      break;
  }
}

void readSerialControl() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    if (line.startsWith("CONTROL:")) {
      line.remove(0, 8);

      int values[6];
      int index = 0;

      while (line.length() > 0 && index < 6) {
        int commaIndex = line.indexOf(',');

        if (commaIndex == -1) {
          values[index++] = line.toInt();
          break;
        }

        values[index++] = line.substring(0, commaIndex).toInt();
        line.remove(0, commaIndex + 1);
      }

      if (index == 6) {
        bool serialRoverSW = values[2];

        // Toggle obstacle autonomous mode
        if (!lastSerialRoverButtonState && serialRoverSW) {

          if (driveMode == OBSTACLE_AUTO_MODE) {
            driveMode = MANUAL_MODE;
          } else {
            driveMode = OBSTACLE_AUTO_MODE;
          }

          motors.stop();

          autoState = AUTO_FORWARD;
          autoStateStartTime = millis();

          Serial.print("Obstacle auto mode: ");
          Serial.println(
            driveMode == OBSTACLE_AUTO_MODE ? "ON" : "OFF"
          );
        }

        lastSerialRoverButtonState = serialRoverSW;

        // Manual driving only in manual mode
        if (driveMode == MANUAL_MODE && !isTurning()) {
          motors.drive(
            values[0],
            values[1],
            DEADZONE_ROVER
          );
        }

        // Prevent signal timeout from stopping the rover
        lastReceiveTime = millis();
      }
    }
  }
}