from .camera import Camera
import cv2
import numpy as np
import threading


class Vision:

    def __init__(self, camera: Camera, image_to_print, margin_to_markers_horizontal=25, margin_to_markers_vertical=200):
        self.camera = camera
        self.thread = None
        self.quit_loop = False
        self.image_to_print = image_to_print

        #self.image_path = np.where(image_to_print)

        self.margin_to_markers_horizontal = margin_to_markers_horizontal
        self.margin_to_markers_vertical = margin_to_markers_vertical

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def quit(self):
        self.quit_loop = True

    def run(self):

        u = 0
        while not self.quit_loop:
            frame = self.camera.get_frame()

            if frame is not None:

                target = frame.copy()

                markers = self.camera.get_markers()
                if markers is not None:
                    i = 0
                    for marker in markers:
                        if i == 2: break
                        i += 1
                        x, y, r = marker
                        cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

                # Bild verkleinern?
                # height, width, channels = frame.shape
                # frame = cv2.resize(frame, (int(width/2), int(height/2)))

                border = self.get_canvas_restrictions(markers)
                if border is not None:
                    target[border[0][1]:border[1][1], border[0][0]:border[1][0]] = self.image_to_print
                    cv2.rectangle(target, border[0], border[1], (0, 255, 0), 3)

                    # Kopiert von https://gist.github.com/IAmSuyogJadhav/305bfd9a0605a4c096383408bee7fd5c
                    alpha = 0.3
                    frame = cv2.addWeighted(target, alpha, frame, 1 - alpha, 0)

                cv2.imshow('image', frame)
                print("Image!", u)
            else:
                print("None!", u)
            u += 1
            cv2.waitKey(1)

    def get_canvas_restrictions(self, markers):

        if markers is None or len(markers) != 4:
            return None

        markers_offset = markers[1][0] - markers[0][0]  # Rechter Wand Marker X - Linker Wand Marker X

        height, width, channels = self.image_to_print.shape

        if width > markers_offset - self.margin_to_markers_horizontal * 2:
            print("Image to big!")  # TODO was sötti da passiere.
            return None

        # TODO was wenn sbild höcher isch als es chönti si??

        p1 = (int(markers[0][0] + markers_offset / 2 - width / 2), markers[0][1] + self.margin_to_markers_vertical)
        p2 = (p1[0] + width,
              p1[1] + height)

        return p1, p2
