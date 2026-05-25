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
    
    last_detection_times = {}
    DETECTION_COOLDOWN = 10

    try:
        # Continuously capture images from the camera and run inference
        while True:
            frame = camera.get_frame()

            if frame is None:
                continue

            annotated, results = processor.process(frame)
            
            print(results)
            
            camera.frame = annotated
            
            temperature = arduino.get_temperature()
            humidity = arduino.get_humidity()
            distance = arduino.get_distance_cm()

            if temperature is not None:
                try:
                    sensor_db.log_temperature(temperature)
                except Exception as e:
                    print(f"[WARNING] Failed to log temperature: {e}")

            server.send_sensor_data(
                temperature=temperature,
                humidity=humidity,
                distance=distance
            )

            detected_objects = results.get("objects", [])
            detected_colors = results.get("colors", [])

            if detected_objects:
                first_object = detected_objects[0]
                first_color = detected_colors[0]["color"] if detected_colors else None

                detected_object = first_object.get("label")
                confidence = first_object.get("score")

                current_time = time.time()

                if detected_object is not None:
                    last_time = last_detection_times.get(detected_object, 0)
 
                    is_new_detection = (
                        current_time - last_time > DETECTION_COOLDOWN
                    )

                    if is_new_detection:
                        server.send_detection(
                            detected_object=detected_object,
                            color=first_color,
                            confidence=confidence
                        )

                        last_detection = detected_object
                        last_detection_time = current_time
        
                time.sleep(2)

    except KeyboardInterrupt:
        print("[INFO] stopping...")

    stream.stop()
    camera.stop()
    server.disconnect()
    arduino.disconnect()

if __name__ == "__main__":
    main()
