#ifndef PACKETS_H
#define PACKETS_H

struct SensorPacket {
  float temperatureC;
};

struct ControlPacket {
  int roverX;
  int roverY;
  bool roverSW;

  int armX;
  int armY;
  bool armSW;
};

#endif