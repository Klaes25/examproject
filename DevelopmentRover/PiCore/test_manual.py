import time
import config

from rover_control.manual_control import ManualControl
from communication.command_handler import CommandHandler
from communication.arduino_serial import ArduinoSerial


arduino = ArduinoSerial(config)

if not arduino.connect():
    print("Could not connect to Arduino.")
    exit(1)

manual = ManualControl()
handler = CommandHandler(arduino)

print("Testing manual rover control in 3 seconds...")
time.sleep(3)

tests = [
    ("forward", manual.create_drive_command("forward", 700)),
    ("stop", manual.stop()),
    ("backward", manual.create_drive_command("backward")),
    ("stop", manual.stop()),
    ("left", manual.create_drive_command("left")),
    ("stop", manual.stop()),
    ("right", manual.create_drive_command("right")),
    ("stop", manual.stop()),
]

for name, cmd in tests:
    print(f"\nSending: {name}")
    handler.handle_command(cmd)
    time.sleep(1.5)

print("\nDone. Stopping rover.")
handler.handle_command(manual.stop())
time.sleep(0.5)
arduino.disconnect()
