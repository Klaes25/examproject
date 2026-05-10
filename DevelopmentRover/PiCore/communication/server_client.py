# server_client.py

# Handles communication between the Raspberry Pi and the server.

# Features:
# - Connects to the server using WebSocket
# - Automatically reconnects if the connection is lost
# - Sends sensor data, AI detections and status messages
# - Receives commands from the server

import json
import time
import threading
from typing import Callable, Optional, Dict, Any

import websocket


# Manages the WebSocket connection to the server
class ServerClient:

    def __init__(
        self,
        server_url: str,
        on_command: Optional[Callable[[Dict[str, Any]], None]] = None,
        reconnect_delay: int = 3
    ):
        # Server WebSocket URL
        self.server_url = server_url

        # Callback function for received commands
        self.on_command = on_command

        # Delay before trying to reconnect
        self.reconnect_delay = reconnect_delay

        # WebSocket object
        self.ws = None

        # True when connected to the server
        self.connected = False

        # True while the background thread should keep running
        self.running = False

        # Background thread for connection handling
        self.thread = None

    # Starts the connection in a background thread
    def connect(self):
        self.running = True

        self.thread = threading.Thread(
            target=self._connection_loop,
            daemon=True
        )

        self.thread.start()

    # Keeps trying to connect if the connection is lost
    def _connection_loop(self):
        while self.running:
            try:
                # Create WebSocket client
                self.ws = websocket.WebSocketApp(
                    self.server_url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )

                # Run until disconnected
                self.ws.run_forever()

            except Exception as error:
                print(f"[ServerClient] Connection error: {error}")

            # Mark as disconnected
            self.connected = False

            # Wait and reconnect
            if self.running:
                print("[ServerClient] Reconnecting...")
                time.sleep(self.reconnect_delay)

    # Called when the connection is established
    def _on_open(self, ws):
        self.connected = True

        print("[ServerClient] Connected to server")

        # Send initial online status
        self.send_status({
            "status": "online",
            "device": "raspberry_pi_rover"
        })

    # Called when the server sends a message
    def _on_message(self, ws, message):
        try:
            # Convert JSON string to Python dictionary
            data = json.loads(message)

            # Call the command handler if one was provided
            if self.on_command:
                self.on_command(data)

        except json.JSONDecodeError:
            print(f"[ServerClient] Invalid JSON received: {message}")

    # Called when an error occurs
    def _on_error(self, ws, error):
        print(f"[ServerClient] WebSocket error: {error}")

    # Called when the connection closes
    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        print("[ServerClient] Disconnected from server")

    # Sends a Python dictionary as JSON
    def send(self, data: Dict[str, Any]):
        # Do nothing if not connected
        if not self.connected or not self.ws:
            return False

        try:
            # Convert dictionary to JSON string
            json_string = json.dumps(data)

            # Send the message
            self.ws.send(json_string)

            return True

        except Exception as error:
            print(f"[ServerClient] Send failed: {error}")

            self.connected = False
            return False

    # Sends sensor data to the server
    def send_sensor_data(
        self,
        temperature=None,
        humidity=None,
        distance=None
    ):
        return self.send({
            "type": "sensor_data",
            "temperature": temperature,
            "humidity": humidity,
            "distance": distance,
            "timestamp": time.time()
        })

    # Sends AI or color detection results
    def send_detection(
        self,
        detected_object=None,
        color=None,
        confidence=None
    ):
        return self.send({
            "type": "detection",
            "object": detected_object,
            "color": color,
            "confidence": confidence,
            "timestamp": time.time()
        })

    # Sends general rover status
    def send_status(self, status: Dict[str, Any]):
        return self.send({
            "type": "status",
            **status,
            "timestamp": time.time()
        })

    # Stops the connection cleanly
    def disconnect(self):
        self.running = False

        if self.ws:
            self.ws.close()

        self.connected = False

    # Returns True if connected
    def is_connected(self):
        return self.connected