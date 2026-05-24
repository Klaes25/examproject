#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <LiquidCrystal.h>

RF24 radio(9, 8);   // CE, CSN
const byte address[6] = "ROV01";

// LCD pins: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(A4, 4, 5, 6, 7, 10);

struct SensorPacket {
  float temperatureC;
  float humidity;
};

SensorPacket sensorData;

// Rover joystick
const int roverJoyX  = A2;
const int roverJoyY  = A3;
const int roverJoySW = 3;

// Arm joystick
const int armJoyX  = A0;
const int armJoyY  = A1;
const int armJoySW = 2;

struct ControlPacket {
  int roverX;
  int roverY;
  bool roverSW;

  int armX;
  int armY;
  bool armSW;
};

ControlPacket data;

float lastTemperature = 0.0;
bool hasTemperature = false;

void setup() {
  pinMode(roverJoySW, INPUT_PULLUP);
  pinMode(armJoySW, INPUT_PULLUP);

  Serial.begin(9600);

  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("Controller ready");
  lcd.setCursor(0, 1);
  lcd.print("Waiting temp...");

  if (!radio.begin()) {
    Serial.println("NRF not responding on controller");
    lcd.clear();
    lcd.print("NRF error");
    while (1);
  }

  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.enableAckPayload();
  radio.enableDynamicPayloads();
  radio.openWritingPipe(address);
  radio.stopListening();

  Serial.println("Controller ready");
  delay(1000);
  lcd.clear();
}

void loop() {
  data.roverX = analogRead(roverJoyX);
  data.roverY = analogRead(roverJoyY);
  data.roverSW = (digitalRead(roverJoySW) == LOW);

  data.armX = analogRead(armJoyX);
  data.armY = analogRead(armJoyY);
  data.armSW = (digitalRead(armJoySW) == LOW);

   bool ok = radio.write(&data, sizeof(data));

  if (radio.isAckPayloadAvailable()) {
    radio.read(&sensorData, sizeof(sensorData));
    lastTemperature = sensorData.temperatureC;
    hasTemperature = true;

    Serial.print("Temp: ");
    Serial.print(lastTemperature);
    Serial.println(" C");
  }

  updateLCD(ok);

  delay(20);
}

  void updateLCD(bool radioOK) {
  static unsigned long lastLCDUpdate = 0;

  if (millis() - lastLCDUpdate < 300) {
    return;
  }

  lastLCDUpdate = millis();

  lcd.setCursor(0, 0);
  lcd.print("Temp: ");

if (hasTemperature) {
  lcd.print(lastTemperature, 1);
  lcd.print((char)223); // degree symbol
  lcd.print("C   ");
} else {
  lcd.print("--.-");
  lcd.print((char)223);
  lcd.print("C   ");
}

lcd.setCursor(0, 1);
lcd.print("Radio: ");
if (radioOK) {
  lcd.print("OK     ");
} else {
  lcd.print("NO     ");
}
}