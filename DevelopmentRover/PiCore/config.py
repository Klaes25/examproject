import os

# Server address used by the Raspberry Pi.
# For local/server testing this should point to the nginx entrypoint, not the backend container port.
SERVER_IP = os.getenv("SERVER_IP", "100.116.69.43")
SERVER_PORT = int(os.getenv("SERVER_PORT", "50325"))

# Rover-specific WebSocket endpoint through nginx.
SERVER_WS_PATH = os.getenv("SERVER_WS_PATH", "/rover/ws/rover")

# Rover token must be set on the Raspberry Pi environment.
# Do not hardcode the real token in Git.
ROVER_TOKEN = os.getenv("ROVER_TOKEN", "change-me")

# Full WebSocket URL used by server_client.py
SERVER_URL = f"ws://{SERVER_IP}:{SERVER_PORT}{SERVER_WS_PATH}?token={ROVER_TOKEN}"

# Serial port to the Arduino Uno
ARDUINO_PORT = "/dev/ttyACM0"

# Serial baud rate (must match Serial.begin)
ARDUINO_BAUD = 9600

# Delay between reconnect attempts (seconds)
SERIAL_RETRY_DELAY = 3
