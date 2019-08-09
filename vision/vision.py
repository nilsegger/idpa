from .camera import Camera
import cv2
import numpy as np
import threading


class Vision:

    def __init__(self, camera: Camera, image_to_print=None, margin_to_markers=25):
        self.camera = camera
        self.thread = None
        self.quit_loop = False
        self.image_to_print = image_to_print
        self.margin_to_markers = margin_to_markers

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
                markers = self.camera.get_markers()
                if markers is not None:
                    for marker in markers:
                        x, y, r = marker
                        cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

                frame = cv2.resize(frame, (int(width/2), int(height/2)))

                canvas_border_p1, canvas_border_p2 = self.get_canvas_restrictions(markers)

                cv2.imshow('image', frame)  # np.hstack([frame, img, cimg]))
            cv2.waitKey(16)

    def get_canvas_restrictions(self, markers):

        """
        Image height wird no gebrucht
        :param markers:
        :return:
        """


