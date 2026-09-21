#include "RadioReceiver.h"

RadioReceiver::RadioReceiver(uint8_t cePin, uint8_t csnPin, const byte* addr)
  : radio(cePin, csnPin) {

  memcpy(address, addr, 6);
}

void RadioReceiver::begin() {
  radio.begin();

  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);

  radio.enableAckPayload();
  radio.enableDynamicPayloads();

  radio.openReadingPipe(0, address);

  radio.startListening();
}

bool RadioReceiver::available() {
  return radio.available();
}

void RadioReceiver::readData() {
  radio.read(&data, sizeof(data));
}

void RadioReceiver::sendSensorData(SensorPacket& sensorData) {
  radio.writeAckPayload(0, &sensorData, sizeof(sensorData));
}