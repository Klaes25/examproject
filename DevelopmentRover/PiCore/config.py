import os

ROVER_TOKEN = os.getenv("ROVER_TOKEN")

if not ROVER_TOKEN:
    raise RuntimeError("ROVER_TOKEN is missing. PiCore.service must load /etc/rover.env")

SERVER_URL = f"ws://localhost:18765/rover/ws/rover?token={ROVER_TOKEN}"

ARDUINO_PORT = "/dev/ttyACM0"
ARDUINO_BAUD = 9600
SERIAL_RETRY_DELAY = 2
