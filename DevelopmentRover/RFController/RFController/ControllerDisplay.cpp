#include "ControllerDisplay.h"

ControllerDisplay::ControllerDisplay()
  : lcd(A4, 4, 5, 6, 7, 10), lastLCDUpdate(0) {
}

void ControllerDisplay::begin() {
  lcd.begin(16, 2);
}

void ControllerDisplay::showStartup() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Controller ready");
  lcd.setCursor(0, 1);
  lcd.print("Waiting temp...");
}

void ControllerDisplay::showNRFError() {
  lcd.clear();
  lcd.print("NRF error");
}

void ControllerDisplay::update(float temperature, bool hasTemperature, bool radioOK) {
  if (millis() - lastLCDUpdate < 300) {
    return;
  }

  lastLCDUpdate = millis();

  lcd.setCursor(0, 0);
  lcd.print("Temp: ");

  if (hasTemperature) {
    lcd.print(temperature, 1);
    lcd.print((char)223);
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