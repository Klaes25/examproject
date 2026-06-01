from picamera2 import Picamera2
from threading import Thread


class CameraManager:

    def __init__(self, resolution=(320, 240), framerate=32):
        self.camera = Picamera2()
        config = self.camera.create_video_configuration(
            main={"size": resolution, "format": "BGR888"},
            controls={"FrameRate": framerate}
        )
        self.camera.configure(config)
        self.frame = None
        self.stopped = False

    def start(self):
        self.camera.start()
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            self.frame = self.camera.capture_array()
        self.camera.stop()
        self.camera.close()

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stopped = True
