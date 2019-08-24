import time

import math
import cv2
import numpy as np
import threading
from picamera.array import PiRGBArray
from picamera import PiCamera
import threading

from motor_interface import MotorInterface


class Vision:

    def __init__(self, motors: MotorInterface, max_height_in_cm, precision_in_cm,
                 wall_markers_distance_in_cm, spray_point_offset=(0, 0), image_to_print=None,
                 margin_to_markers_horizontal_cm=15, margin_to_markers_vertical_cm=20):
        self.thread = None
        self.quit_loop = False
        self.image_to_print = image_to_print
        self.margin_to_markers_horizontal_cm = margin_to_markers_horizontal_cm
        self.margin_to_markers_vertical_cm = margin_to_markers_vertical_cm
        self.spray_point_offset = spray_point_offset
        self.wall_markers_distance_in_cm = wall_markers_distance_in_cm
        self.motors = motors
        self.precision_in_cm = precision_in_cm
        self.max_height_in_cm = max_height_in_cm

        self.image_scale_last = None

        self.image_scaled = False
        self.scale_action_timeout_original = 5
        self.scale_action_timeout = 5
        self.last_marker_positions = None

        self.image_scaled = False
        self.image_scale_start = None

        self.wall_markers_offset = None
        self.cm_to_pixel = None
        self.canvas_p1 = None
        self.canvas_p2 = None
        self.left_motor_corner_distance = None
        self.right_motor_corner_distance = None
        self.image_p1 = None
        self.image_p2 = None

        self.path_progress = 0
        self.print_path = None

        self.start_printing = False
        self.printing_path_begin_length = None
        self.spray_point = None

        self.spray_timeout = 0
        self.spray_timeout_last = None

        self.moved_since_last_spray = True

        self.overlay_image = None

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def quit(self):
        self.quit_loop = True
        self.thread.join(1)

    def run(self):

        resolution = (1024, 768)
        camera = PiCamera()
        camera.resolution = resolution
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=resolution)

        time.sleep(1)

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            img = frame.array

            img = cv2.flip(img, 0)
            img = cv2.flip(img, 1)
            overlay = img.copy()

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            lower_range = np.array([0, 0, 0])
            upper_range = np.array([255, 255, 254])
            mask = cv2.inRange(hsv, lower_range, upper_range)
            circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 20, param1=7, param2=6, minRadius=2,
                                       maxRadius=10)

            markers = []
            if circles is not None:
                circles = np.uint16(np.around(circles))

                if len(circles[0, :]) > 10:
                    self.display_message(overlay, "Too many markers found.")
                else:
                    for circle in circles[0, :]:
                        markers.append((circle[0], circle[1], circle[2]))

            if markers is not None and len(markers) > 0:

                if len(markers) != 4:
                    self.motors.stop()
                    self.display_message(overlay, "Markers not found.")
                else:

                    i = 0
                    while i < len(markers) - 1:

                        changed = False
                        for q in range(i + 1, len(markers)):
                            if markers[q][1] < markers[i][1]:
                                temp = markers[q]
                                del markers[q]
                                markers.insert(i, temp)
                                changed = True
                                break

                        if not changed:
                            i += 1

                    x, y, r = markers[0]
                    sx, sy, sr = markers[1]
                    if sx < x:
                        markers[0] = (sx, sy, sr)
                        markers[1] = (x, y, r)

                    x, y, r = markers[2]
                    sx, sy, sr = markers[3]
                    if sx < x:
                        markers[2] = (sx, sy, sr)
                        markers[3] = (x, y, r)

                    self.show_markers(overlay, markers)

                if self.calculate_values(markers, overlay):

                    if self.image_scaled:
                        try:
                            overlay[self.image_p1[1]:self.image_p2[1],
                            self.image_p1[0]:self.image_p2[0]] = self.overlay_image

                            if not self.start_printing:
                                self.motors.stop()
                                self.display_message(overlay, "Ready, press enter to begin printing process.")
                            else:
                                self.follow_print_path(markers, overlay)
                                self.display_message(overlay,
                                                     "Printing progress: " + str(int(
                                                         math.floor(math.fabs(100 / self.printing_path_begin_length *
                                                                              len(self.print_path) - 100)))) + "%")

                        except ValueError:
                            self.display_message(overlay, "Failed to overlay image.")
                    else:
                        self.manage_image_scale(markers, overlay)
                        self.motors.stop()

            # Kopiert von https://gist.github.com/IAmSuyogJadhav/305bfd9a0605a4c096383408bee7fd5c
            alpha = 0.8
            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
            cv2.imshow('Vision', img)
            k = cv2.waitKey(1)
            if k == 13 and self.image_scaled and not self.start_printing:
                self.start_printing = True
                self.printing_path_begin_length = len(self.print_path)

            # clear the stream in preparation for the next frame
            rawCapture.truncate(0)

            # if the `q` key was pressed, break from the loop
            if k == ord("q"):
                self.motors.quit_loop()
                break
        else:
            print("Frame is None.")

    def calculate_values(self, markers, overlay):

        if len(markers) != 4:
            self.display_message(overlay, "Markers not found.")
            return False

        self.wall_markers_offset = markers[1][0] - markers[0][0]
        self.cm_to_pixel = self.wall_markers_offset / self.wall_markers_distance_in_cm

        if self.cm_to_pixel == 0:
            self.display_message(overlay, "Wrong markers found.")
            return False

        self.canvas_p1 = (int(markers[0][0] + self.margin_to_markers_horizontal_cm * self.cm_to_pixel),
                          int(markers[0][1] + self.margin_to_markers_vertical_cm * self.cm_to_pixel))
        self.canvas_p2 = (int(markers[1][0] - self.margin_to_markers_horizontal_cm * self.cm_to_pixel),
                          int(markers[1][1] + self.max_height_in_cm * self.cm_to_pixel))

        self.left_motor_corner_distance, a, b = self.distance(markers[0], markers[2])

        try:
            self.write_text(overlay, str(int(round(self.left_motor_corner_distance / self.cm_to_pixel))) + "cm",
                            (markers[0][0] + int(a / 2), markers[0][1] + int(b / 2)))
        except OverflowError:
            pass

        self.right_motor_corner_distance, a, b = self.distance(markers[1], markers[3])

        try:
            self.write_text(overlay, str(int(round(self.right_motor_corner_distance / self.cm_to_pixel))) + "cm",
                            (markers[1][0] - int(a / 2), markers[1][1] + int(b / 2)))
        except OverflowError:
            pass

        self.draw_rect(overlay, self.canvas_p1, self.canvas_p2)

        d, a, b = self.distance(markers[3], markers[2])
        motors_center = (markers[2][0] + a / 2, markers[2][1] + b / 2)
        self.spray_point = (
            int(motors_center[0] + self.spray_point_offset[0] * self.cm_to_pixel),
            int(motors_center[1] + self.spray_point_offset[1] * self.cm_to_pixel))
        self.draw_circle(overlay, self.spray_point, (0, 0, 255))

        return True

    def manage_image_scale(self, markers, overlay):

        if self.last_marker_positions is None:
            self.image_scale_last = time.time()
            self.last_marker_positions = markers
            return False

        if Vision.position_equals(self.last_marker_positions[0], markers[0]) and Vision.position_equals(
                self.last_marker_positions[1], markers[1]) and Vision.position_equals(self.last_marker_positions[2],
                                                                                      markers[
                                                                                          2]) and Vision.position_equals(
            self.last_marker_positions[3], markers[3]):
            delta = time.time() - self.image_scale_last
            self.scale_action_timeout -= delta

            if self.scale_action_timeout <= 0:
                self.scale_image(markers, overlay)
                return True
            else:
                self.display_message(overlay, str(round(self.scale_action_timeout)) + "s")

        else:
            self.display_message(overlay, "Markers are still changing...")
            self.scale_action_timeout = self.scale_action_timeout_original

        self.image_scale_last = time.time()
        self.last_marker_positions = markers
        return False

    def scale_image(self, markers, overlay):

        if self.image_scale_start == None:
            self.image_scale_start = int(round(time.time()))
            t = threading.Thread(target=self.scale_image_thread, args=(markers,))
            t.start()
        else:
            Vision.display_message(overlay, "Scaling image and calculating path. " + str(
                int(round(time.time())) - self.image_scale_start) + "s, progress: " + str(
                round(self.path_progress)) + "%")

    def scale_image_thread(self, markers):

        max_width = self.canvas_p2[0] - self.canvas_p1[0]

        height, width, channels = self.image_to_print.shape

        if width > max_width:
            scale = width / max_width
            self.image_to_print = cv2.resize(self.image_to_print, (int(max_width), int(height / scale)))

        height, width, channels = self.image_to_print.shape
        max_height = self.canvas_p2[1] - self.canvas_p1[1]

        if height > max_height:
            scale = height / max_height
            self.image_to_print = cv2.resize(self.image_to_print, (int(max_width / scale), int(max_height)))

        height, width, channels = self.image_to_print.shape

        print("Hello")

        if height > width and height < max_height:
            scale = max_height / height
            self.image_to_print = cv2.resize(self.image_to_print, (int(width * scale), int(height * scale)))
        elif width > height and width < max_width:
            scale = max_width / width
            self.image_to_print = cv2.resize(self.image_to_print, (int(width * scale), int(height * scale)))

        height, width, channels = self.image_to_print.shape

        self.image_p1 = (
            int(self.canvas_p1[0] + max_width / 2 - width / 2), int(self.canvas_p1[1] + max_height / 2 - height / 2))
        self.image_p2 = (int(self.image_p1[0] + width), int(self.image_p1[1] + height))

        print(self.image_to_print.shape)

        self.find_path()

    def find_path(self):
        height, width, _ = self.image_to_print.shape
        path = []

        step = self.precision_in_cm * self.cm_to_pixel

        for y in range(height - 1, 0, -step):
            for x in range(width - 1, 0, -step):
                if (self.image_to_print[y][x][0] != 0) or (self.image_to_print[y][x][1] != 0) or (
                        self.image_to_print[y][x][2] != 0):
                    path.append((x, y))

        if len(path) == 0:
            print("There were no white pixels.")
            exit(-1)

        for p in path:
            self.overlay_image[p[1]][p[0]] = (0, 255, 0)

        self.print_path = path
        self.image_scaled = True
        self.overlay_image = np.zeros(self.image_to_print.shape, np.uint8)

    def follow_print_path(self, markers, overlay):

        if len(self.print_path) == 0:
            print("Path is empty!")
            return

        """
            lm = left motor, rm = right_motor, sp = spray point, tlm = target lm, trm = target right motor, abs_tsp = absolute target spray position
        """

        if self.spray_timeout > 0:
            delta = time.time() - self.spray_timeout_last if self.spray_timeout_last is not None else 0
            self.spray_timeout -= delta
            self.spray_timeout_last = time.time()
            return

        lm_to_lw, lm_to_lw_a, lm_to_lw_b = self.distance(markers[0], markers[2])
        rm_to_rw, rm_to_rw_a, rm_to_rw_b = self.distance(markers[1], markers[3])

        _, lm_to_sp_a, lm_to_sp_b = self.distance(markers[2], self.spray_point)
        _, rm_to_sp_a, rm_to_sp_b = self.distance(markers[3], self.spray_point)

        abs_tsp = (self.print_path[0][0] + self.image_p1[0], self.print_path[0][1] + self.image_p1[1])

        self.draw_circle(overlay, abs_tsp, (0, 0, 255))

        ltm_pos = (abs_tsp[0] - lm_to_sp_a,
                   abs_tsp[1] + lm_to_sp_b if markers[2][1] > self.spray_point[1] else abs_tsp[1] - lm_to_sp_b)
        rtm_pos = (abs_tsp[0] + rm_to_sp_a,
                   abs_tsp[1] + rm_to_sp_b if markers[3][1] > self.spray_point[1] else abs_tsp[1] - rm_to_sp_b)

        self.draw_circle(overlay, ltm_pos, (0, 0, 255), r=markers[2][2])
        self.draw_circle(overlay, rtm_pos, (0, 0, 255), r=markers[3][2])

        ltm_to_lw, ltm_to_lw_a, ltm_to_lw_b = self.distance(markers[0], ltm_pos)

        self.write_text(overlay, str(int(round(ltm_to_lw / self.cm_to_pixel))) + "cm",
                        (markers[0][0] + int(ltm_to_lw_a / 2), markers[0][1] + int(ltm_to_lw_b / 2)), color=(0, 0, 255))

        rtm_to_rw, rtm_to_rw_a, rtm_to_rw_b = self.distance(markers[1], rtm_pos)
        self.write_text(overlay, str(int(round(rtm_to_rw / self.cm_to_pixel))) + "cm",
                        (markers[1][0] - int(rtm_to_rw_a / 2), markers[1][1] + int(rtm_to_rw_b / 2)), color=(0, 0, 255))

        lm_to_ltm = self.distance_squared(markers[2], ltm_pos)
        rm_to_rtm = self.distance_squared(markers[3], rtm_pos)

        precision = math.pow(self.precision_in_cm * self.cm_to_pixel, 2)

        lm_positioned = False
        rm_positioned = False

        if lm_to_ltm <= precision / 2:
            lm_positioned = True
            self.motors.spin_Motor_left(0)
        elif lm_to_lw < ltm_to_lw:
            self.motors.spin_Motor_left(-1)
            self.moved_since_last_spray = True
        else:
            self.motors.spin_Motor_left(1)
            self.moved_since_last_spray = True

        if rm_to_rtm <= precision / 2:
            rm_positioned = True
            self.motors.spin_Motor_right(0)
        elif rm_to_rw < rtm_to_rw:
            self.motors.spin_Motor_right(-1)
            self.moved_since_last_spray = True
        else:
            self.motors.spin_Motor_right(1)
            self.moved_since_last_spray = True

        if rm_positioned and lm_positioned:
            if self.moved_since_last_spray:
                self.spray_timeout = self.motors.spray()
            del self.print_path[0]
            self.moved_since_last_spray = False

        self.spray_timeout_last = time.time()

    @staticmethod
    def position_equals(pos1, pos2, precision=15):
        a = pos1[0] - pos2[0] if pos1[0] > pos2[0] else pos2[0] - pos1[0]
        b = pos1[1] - pos2[1] if pos1[1] > pos2[1] else pos2[1] - pos1[1]
        dsq = math.pow(a, 2) + math.pow(b, 2)
        return dsq <= math.pow(precision, 2)

    @staticmethod
    def show_markers(overlay, markers):
        for marker in markers:
            x, y, r = marker
            Vision.draw_circle(overlay, (x, y), r=r)

        if len(markers) == 4:
            Vision.write_text(overlay, "Linke Wand", markers[0])
            Vision.write_text(overlay, "Rechte Wand", markers[1])
            Vision.write_text(overlay, "Linker Motor", markers[2])
            Vision.write_text(overlay, "Rechter Motor", markers[3])

    @staticmethod
    def display_message(overlay, text):
        Vision.write_text(overlay, text, (0, 10), (0, 0, 0))

    @staticmethod
    def write_text(overlay, text, position, color=(0, 255, 0)):
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(overlay, text, (position[0], position[1]), font, 0.5, color, 2, cv2.LINE_AA)

    @staticmethod
    def draw_circle(overlay, position, color=(0, 255, 0), r=2):
        cv2.circle(overlay, position, r, color, 2)

    @staticmethod
    def draw_line(overlay, p1, p2, color=(0, 255, 0), thickness=2):
        cv2.line(overlay, (p1[0], p1[1]), (p2[0], p2[1]), color, thickness)

    @staticmethod
    def draw_rect(overlay, p1, p2, color=(0, 255, 0), thickness=3):
        cv2.rectangle(overlay, p1, p2, color, thickness)

    @staticmethod
    def distance(p1, p2):
        a = p2[0] - p1[0] if p2[0] > p1[0] else p1[0] - p2[0]
        b = p2[1] - p1[1] if p2[1] > p1[1] else p1[1] - p2[1]
        return math.sqrt(math.pow(a, 2) + math.pow(b, 2)), a, b

    @staticmethod
    def distance_squared(p1, p2):
        a = p2[0] - p1[0] if p2[0] > p1[0] else p1[0] - p2[0]
        b = p2[1] - p1[1] if p2[1] > p1[1] else p1[1] - p2[1]
        return math.pow(a, 2) + math.pow(b, 2)
