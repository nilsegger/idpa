from .camera import Camera
import cv2
import numpy as np
import threading


class Vision:

    def __init__(self, camera: Camera, image_to_print, spray_point_offset, wall_markers_distance_in_cm,
                 margin_to_markers_horizontal=25, margin_to_markers_vertical=200, show_process=True):
        self.camera = camera
        self.thread = None
        self.quit_loop = False
        self.image_to_print = image_to_print
        self.print_path = self.find_path(image_to_print)
        self.margin_to_markers_horizontal = margin_to_markers_horizontal
        self.margin_to_markers_vertical = margin_to_markers_vertical
        self.spray_point_offset = spray_point_offset
        self.wall_markers_distance_in_cm = wall_markers_distance_in_cm
        self.show_process = show_process

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def quit(self):
        self.quit_loop = True

    def run(self):
        while not self.quit_loop:
            frame = self.camera.get_frame()

            if frame is not None:

                # Bild verkleinern
                # height, width, channels = frame.shape
                # frame = cv2.resize(frame, (int(width/2), int(height/2)))

                overlay = frame.copy()

                markers = self.camera.get_markers(frame)
                if markers is not None:

                    border = self.get_canvas_restrictions(markers)
                    if border is not None:

                        if self.show_process:
                            overlay[border[0][1]:border[1][1], border[0][0]:border[1][0]] = self.image_to_print
                            cv2.rectangle(overlay, border[0], border[1], (0, 255, 0), 3)
                        self.follow_path(markers, border, overlay)

                    for marker in markers:
                        x, y, r = marker

                        if self.show_process:
                            cv2.circle(overlay, (x, y), r, (0, 255, 0), 2)

                    if self.show_process and len(markers) == 4:
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(overlay, 'Linke Wand', (markers[0][0], markers[0][1]), font, 0.5, (0, 255, 0), 2,
                                    cv2.LINE_AA)
                        cv2.putText(overlay, 'Rechte Wand', (markers[1][0], markers[1][1]), font, 0.5, (0, 255, 0), 2,
                                    cv2.LINE_AA)
                        cv2.putText(overlay, 'Linker Motor', (markers[2][0], markers[2][1]), font, 0.5, (0, 255, 0), 2,
                                    cv2.LINE_AA)
                        cv2.putText(overlay, 'Rechter Motor', (markers[3][0], markers[3][1]), font, 0.5, (0, 255, 0), 2,
                                    cv2.LINE_AA)

                # Kopiert von https://gist.github.com/IAmSuyogJadhav/305bfd9a0605a4c096383408bee7fd5c
                alpha = 0.4
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                if self.show_process:
                    cv2.imshow('image', frame)

            if self.show_process:
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

    def find_path(self, image_to_print):
        height, width, _ = image_to_print.shape
        path = []
        for y in range(height):
            for x in range(width):
                if image_to_print[y][x][0] == image_to_print[y][x][1] == image_to_print[y][x][2] == 255:
                    path.append((x, y))
        return path

    def follow_path(self, markers, border_offset, overlay):

        if len(self.print_path) == 0:
            print("No path found?!")
            return

        # TODO, funktionierts vertical und horizontal??
        cm_to_pixel = self.wall_markers_distance_in_cm / (markers[1][0] - markers[0][0])

        spray_point_x_offset, spray_point_y_offset = self.spray_point_offset

        spray_point_x_offset = int(spray_point_x_offset / cm_to_pixel)
        spray_point_y_offset = int(spray_point_y_offset / cm_to_pixel)

        spray_point = (markers[2][0] + spray_point_x_offset, markers[2][1] + spray_point_y_offset)

        if self.show_process:
            cv2.circle(overlay, (self.print_path[0][0] + border_offset[0][0], self.print_path[0][1] + border_offset[0][1]),
                       2, (0, 0, 255), 2)

            cv2.circle(overlay,
                       spray_point,
                       2, (0, 0, 255), 2)
