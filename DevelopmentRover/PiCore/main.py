# We add code to main.py after we finish modules

import time
from camera.camera_manager import CameraManager
from camera.video_stream import VideoStream


def main():
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

    except KeyboardInterrupt:
        print("[INFO] stopping...")

    stream.stop()
    camera.stop()


if __name__ == "__main__":
    main()
