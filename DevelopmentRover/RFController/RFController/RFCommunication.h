#ifndef RF_COMMUNICATION_H
#define RF_COMMUNICATION_H

#include <Arduino.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "Packets.h"

class RFCommunication {
private:
  RF24 radio;
  const byte address[6] = "ROV01";

public:
  RFCommunication();

  bool begin();
  bool sendControlData(ControlPacket &data);
  bool readSensorData(SensorPacket &sensorData);
};

#endif