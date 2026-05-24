#ifndef RADIO_RECEIVER_H
#define RADIO_RECEIVER_H

#include <RF24.h>
#include <nRF24L01.h>
#include <SPI.h>
#include "Component.h"

struct ControlPacket {
  int roverX;
  int roverY;
  bool roverSW;

  int armX;
  int armY;
  bool armSW;
};

struct SensorPacket {
  float temperatureC;
  float humidity;
};

class RadioReceiver : public Component {
private:
  RF24 radio;
  byte address[6];

public:
  ControlPacket data;

  RadioReceiver(uint8_t cePin, uint8_t csnPin, const byte* addr);

  void begin() override;

  bool available();

  void readData();

  void sendSensorData(SensorPacket& sensorData);
};

#endif