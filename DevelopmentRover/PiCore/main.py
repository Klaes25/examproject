import time

import config

from camera.camera_manager import CameraManager
from camera.video_stream import VideoStream

from communication.server_client import ServerClient
from communication.command_handler import CommandHandler
from communication.arduino_serial import ArduinoSerial


def main():
    print("[INFO] connecting to Arduino...")
    arduino = ArduinoSerial(config)

    if not arduino.connect():
        print("[WARNING] Arduino not connected. Commands will not reach rover.")

    command_handler = CommandHandler(arduino=arduino)

    print("[INFO] connecting to server...")
    server = ServerClient(
        server_url=config.SERVER_URL,
        on_command=command_handler.handle_command
    )
    server.connect()
    
    print("[INFO] starting camera...")
    camera = CameraManager(resolution=(320, 240), framerate=32).start()

    time.sleep(2.0)

    print("[INFO] starting video stream...")
    stream = VideoStream(camera, port=8000).start()

    print("[INFO] running. press CTRL+C to stop.")

    try:
        while True:
            frame = camera.get_frame()

            if frame is None:
                continue

            # vision modules go here later
            
            temperature = arduino.get_temperature()
            distance = arduino.get_distance_cm()

            server.send_sensor_data(
                temperature=temperature,
                humidity=None,
                distance=distance
            )

            time.sleep(2)

    except KeyboardInterrupt:
        print("[INFO] stopping...")

    stream.stop()
    camera.stop()
    server.disconnect()
    arduino.disconnect()

if __name__ == "__main__":
    main()
