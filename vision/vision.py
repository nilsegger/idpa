from .camera import Camera
import cv2
import numpy as np
import threading


class Vision:

    def __init__(self, camera: Camera):
        self.camera = camera
        self.thread = None
        self.quit_loop = False

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def quit(self):
        self.quit_loop = True

    def run(self):
        while not self.quit_loop:
            frame = self.camera.get_frame()

            if frame is not None:

                height, width, channels = frame.shape
                print(width, "x", height)

                markers = self.camera.get_markers()

                if markers is not None:
                    for marker in markers:
                        x, y, r = marker
                        cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

                cv2.imshow('image', frame)  # np.hstack([frame, img, cimg]))
            cv2.waitKey(16)
