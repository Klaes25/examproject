#include <Arduino.h>

#include "MotorController.h"
#include "RobotArm.h"
#include "RadioReceiver.h"
#include "TemperatureSensor.h"
#include "UltrasonicSensor.h"

// NRF24 address
const byte address[6] = "ROV01";

// Radio receiver object
RadioReceiver radio(A2, A1, address);

// Rover settings
const int MAX_SPEED = 255;
const int ACCEL_STEP = 32;

const int DEADZONE_ROVER = 80;
const int DEADZONE_ARM = 80;

// Safety settings
const unsigned long SIGNAL_TIMEOUT = 500;
const float OBSTACLE_DISTANCE_CM = 20.0;

// Sensor update intervals
const unsigned long DHT_INTERVAL = 2000;
const unsigned long ULTRASONIC_INTERVAL = 100;

// Timing
unsigned long lastReceiveTime = 0;

// Sensor packet sent back to controller
SensorPacket sensorData;

// Motor controller
MotorController motors(
  5, 7, 4,
  6, 3, 2,
  MAX_SPEED,
  ACCEL_STEP
);

// Robot arm
RobotArm arm(
  8,
  9,
  10,
  A0
);

// DHT22 sensor
TemperatureSensor temperatureSensor(
  A3,
  DHT22,
  DHT_INTERVAL
);

// Ultrasonic sensor
UltrasonicSensor ultrasonic(
  A4,
  A5,
  ULTRASONIC_INTERVAL
);

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

  // Update sensors
  temperatureSensor.update();
  ultrasonic.update();

  // Save temperature into packet
  sensorData.temperatureC =
    temperatureSensor.getTemperature();

  // Check for incoming controller data
  if (radio.available()) {

    radio.readData();

    lastReceiveTime = millis();

    // Stop rover if obstacle is too close
    if (
      ultrasonic.isObstacleClose(
        OBSTACLE_DISTANCE_CM
      )
    ) {

      motors.stop();

    } else {

      // Drive rover
      motors.drive(
        radio.data.roverX,
        radio.data.roverY,
        DEADZONE_ROVER
      );
    }

    // Control robot arm
    arm.control(
      radio.data.armX,
      radio.data.armY,
      radio.data.armSW,
      DEADZONE_ARM
    );

    // Send sensor data back
    radio.sendSensorData(sensorData);
  }

  // Stop motors if signal lost
  if (
    millis() - lastReceiveTime >
    SIGNAL_TIMEOUT
  ) {

    motors.stop();
  }

  delay(20);
}