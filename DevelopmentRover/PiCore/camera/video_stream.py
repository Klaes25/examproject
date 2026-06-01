import io
import logging
import socketserver
import threading
from http import server
from threading import Condition

import simplejpeg

from camera.camera_manager import CameraManager


class _StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class _StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, output, *args, **kwargs):
        self.output = output
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                    frame = self.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('[VideoStream] Client %s disconnected: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


class _StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class VideoStream:

    def __init__(self, camera: CameraManager, port: int = 8000, quality: int = 85):
        self.camera = camera
        self.port = port
        self.quality = quality
        self._output = _StreamingOutput()
        self._stopped = False

    def start(self):
        threading.Thread(target=self._encode_loop, daemon=True).start()
        threading.Thread(target=self._serve, daemon=True).start()
        return self

    def _encode_loop(self):
        while not self._stopped:
            frame = self.camera.get_frame()
            if frame is None:
                continue
            jpeg = simplejpeg.encode_jpeg(frame, quality=self.quality, colorspace='BGR')
            self._output.write(jpeg)

    def _serve(self):
        output = self._output
        handler = lambda *args, **kwargs: _StreamingHandler(output, *args, **kwargs)
        httpd = _StreamingServer(('', self.port), handler)
        print(f"[VideoStream] Streaming at http://<pi-ip>:{self.port}/stream.mjpg")
        httpd.serve_forever()

    def stop(self):
        self._stopped = True
