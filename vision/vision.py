from .camera import Camera
import cv2

import threading


class Vision:

    def __init__(self, camera: Camera):
        self.camera = camera
        self.thread = None

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while True:
            frame = self.camera.get_frame()
            if frame is not None:
                cv2.imshow('image', frame)
            cv2.waitKey(16)
