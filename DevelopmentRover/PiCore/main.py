import time

import config
import sensor_db

from camera.camera_manager import CameraManager
from camera.video_stream import VideoStream

from communication.server_client import ServerClient
from communication.command_handler import CommandHandler
from communication.arduino_serial import ArduinoSerial

from vision.frame_processor import FrameProcessor


def main():
    sensor_db.init_db()

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

    # Initialize the object detection model
    processor = FrameProcessor(
        detect_colors=["red", "green", "blue", "yellow"],
        detect_objects=True
    )

    print("[INFO] running. press CTRL+C to stop.")

    try:
        # Continuously capture images from the camera and run inference
        while True:
            frame = camera.get_frame()

            if frame is None:
                continue

            annotated, results = processor.process(frame)
            camera.frame = annotated

            temperature = arduino.get_temperature()
            distance = arduino.get_distance_cm()

            if temperature is not None:
                try:
                    sensor_db.log_temperature(temperature)
                except Exception as e:
                    print(f"[WARNING] Failed to log temperature: {e}")

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
