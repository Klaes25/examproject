#include "RFCommunication.h"

RFCommunication::RFCommunication()
  : radio(9, 8) {
}

bool RFCommunication::begin() {
  if (!radio.begin()) {
    return false;
  }

  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.enableAckPayload();
  radio.enableDynamicPayloads();
  radio.openWritingPipe(address);
  radio.stopListening();

  return true;
}

bool RFCommunication::sendControlData(ControlPacket &data) {
  return radio.write(&data, sizeof(data));
}

bool RFCommunication::readSensorData(SensorPacket &sensorData) {
  if (radio.isAckPayloadAvailable()) {
    radio.read(&sensorData, sizeof(sensorData));
    return true;
  }

  return false;
}