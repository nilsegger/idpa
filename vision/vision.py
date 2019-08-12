from .camera import Camera
import cv2
import numpy as np
import threading


class Vision:

    def __init__(self, camera: Camera, image_to_print, margin_to_markers_horizontal=25, margin_to_markers_vertical=50):
        self.camera = camera
        self.thread = None
        self.quit_loop = False
        self.image_to_print = image_to_print
        self.margin_to_markers_horizontal = margin_to_markers_horizontal
        self.margin_to_markers_vertical = margin_to_markers_vertical

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
                    i = 0
                    for marker in markers:
                        if i == 2: break
                        i += 1
                        x, y, r = marker
                        cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

                #frame = cv2.resize(frame, (int(width/2), int(height/2)))

                border = self.get_canvas_restrictions(markers)
                if border is not None:
                    canvas_border_p1, canvas_border_p2 = border
                    print(canvas_border_p1, "x", canvas_border_p2)

                cv2.imshow('image', frame)  # np.hstack([frame, img, cimg]))
            cv2.waitKey(1)

    def get_canvas_restrictions(self, markers):

        return None

        if markers is None or len(markers) != 4:
            return None

        markers_offset = markers[1][0] - markers[0][0] # Rechter Wand Marker X - Linker Wand Marker X

        height, width, channels = self.image_to_print.shape

        if width > markers_offset - self.margin_to_markers_horizontal*2:
            print("Image to big!") # TODO was sötti da passiere.
            return None

        # TODO was wenn sbild höcher isch als es chönti si??

        p1 = (markers[0][0] + self.margin_to_markers_horizontal, markers[0][1] + self.margin_to_markers_vertical)
        p2 = (markers[0][0] + self.margin_to_markers_horizontal + width, markers[0][1] + self.margin_to_markers_vertical + height)

        return p1, p2
