# Public IP address or domain name of your server
SERVER_IP = "YOUR_SERVER_IP"

# Port exposed by docker-compose
SERVER_PORT = 18765

# WebSocket endpoint implemented in FastAPI
SERVER_WS_PATH = "/ws/control"

# Full WebSocket URL used by server_client.py
SERVER_URL = f"ws://{SERVER_IP}:{SERVER_PORT}{SERVER_WS_PATH}"

# Serial port to the Arduino Uno
SERIAL_PORT = "/dev/ttyACM0"

# Serial baud rate (must match Serial.begin)
SERIAL_BAUDRATE = 9600

# Delay between reconnect attempts (seconds)
RECONNECT_DELAY = 3