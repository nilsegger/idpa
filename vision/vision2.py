import time

import math

from .camera import Camera
import cv2
import numpy as np
import threading
from .motor_interface import MotorInterface

import threading


class Vision:

    def __init__(self, motors: MotorInterface, max_height_in_cm, precision_in_cm, camera: Camera, image_to_print,
                 spray_point_offset,
                 wall_markers_distance_in_cm,
                 margin_to_markers_horizontal_cm=150, margin_to_markers_vertical_cm=200):
        self.camera = camera
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
        self.scale_action_timeout_original = 1
        self.scale_action_timeout = 1
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

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def quit(self):
        self.quit_loop = True
        self.thread.join(1)

    def run(self):

        while not self.quit_loop:
            frame = self.camera.get_frame()
            if frame is not None:

                overlay = frame.copy()
                
                
                markers = self.camera.get_markers(frame)
                if markers is not None:
                    self.show_markers(overlay, markers)

                    if self.calculate_values(markers, overlay):

                        if self.image_scaled:
                            try:
                                overlay[self.image_p1[1]:self.image_p2[1], self.image_p1[0]:self.image_p2[0]] = self.image_to_print

                                if not self.start_printing:
                                    self.display_message(overlay, "Ready, press enter to begin printing process.")
                                else:
                                    self.print(markers, overlay)
                                    self.display_message(overlay,
                                                         "Printing progress: " + str(int(math.floor(math.fabs(100 / self.printing_path_begin_length *
                                                                                                              len(self.print_path) - 100)))) + "%")

                            except ValueError:
                                self.display_message(overlay, "Failed to overlay image.")
                        else:
                            self.manage_image_scale(markers, overlay)

                # Kopiert von https://gist.github.com/IAmSuyogJadhav/305bfd9a0605a4c096383408bee7fd5c
                alpha = 0.5
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
                cv2.imshow('Vision', frame)
                k = cv2.waitKey(1)
                if k == 13 and self.image_scaled and not self.start_printing:
                    self.start_printing = True
                    self.printing_path_begin_length = len(self.print_path)
            else:
                print("Frame is None.")

    def calculate_values(self, markers, overlay):

        if len(markers) != 4:
            self.display_message(overlay, "Markers not found.")
            return False

        self.wall_markers_offset = markers[1][0] - markers[0][0]
        self.cm_to_pixel = self.wall_markers_offset / self.wall_markers_distance_in_cm

        self.canvas_p1 = (int(markers[0][0] + self.margin_to_markers_horizontal_cm * self.cm_to_pixel),
                          int(markers[0][1] + self.margin_to_markers_vertical_cm * self.cm_to_pixel))
        self.canvas_p2 = (int(markers[1][0] - self.margin_to_markers_horizontal_cm * self.cm_to_pixel),
                          int(markers[1][1] + self.max_height_in_cm * self.cm_to_pixel))

        self.left_motor_corner_distance, a, b = self.distance(markers[0], markers[2])
        self.write_text(overlay, str(int(round(self.left_motor_corner_distance / self.cm_to_pixel))) + "cm",
                        (markers[0][0] + int(a / 2), markers[0][1] + int(b / 2)))

        self.right_motor_corner_distance, a, b = self.distance(markers[1], markers[3])
        self.write_text(overlay, str(int(round(self.right_motor_corner_distance / self.cm_to_pixel))) + "cm",
                        (markers[1][0] - int(a / 2), markers[1][1] + int(b / 2)))

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

        self.last_marker_positions = markers
        self.image_scale_last = time.time()
        return False

    def scale_image(self, markers, overlay):

        if self.image_scale_start == None:
            self.image_scale_start = int(round(time.time()))
            t = threading.Thread(target=self.scale_image_thread, args=(markers,))
            t.start()
        else:
            Vision.display_message(overlay, "Scaling image and calculating path. " + str(
                int(round(time.time())) - self.image_scale_start) + "s, progress: " + str(round(self.path_progress)) + "%")

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

        self.image_p1 = (int(self.canvas_p1[0] + max_width / 2 - width / 2), int(self.canvas_p1[1] + max_height / 2 - height / 2))
        self.image_p2 = (int(self.image_p1[0] + width), int(self.image_p1[1] + height))

        self.find_path()

    def find_path(self):
        height, width, _ = self.image_to_print.shape
        path = []
        for y in range(height):
            for x in range(width):
                if (self.image_to_print[y][x][0] != 0) or (self.image_to_print[y][x][1] != 0) or (self.image_to_print[y][x][2] != 0):
                    path.append((x, y))

        if len(path) == 0:
            print("There were no white pixels.")

        path_length = len(path)
        optimized_path = [path[0]]
        del path[0]

        while len(optimized_path) != path_length:

            self.path_progress = (100 / path_length * len(optimized_path))

            index = 0
            index_distance = self.distance_squared(optimized_path[len(optimized_path) - 1], path[0])

            for i in range(1, len(path)):
                d = self.distance_squared(optimized_path[len(optimized_path) - 1], path[i])
                if d < index_distance:
                    index_distance = d
                    index = i

            optimized_path.append(path[index])
            del path[index]

        self.print_path = optimized_path
        self.image_scaled = True
        print("Path found.")

    def print(self, markers, overlay):

        if len(self.print_path) == 0:
            return

        target_point = (self.print_path[0][0] + self.image_p1[0], self.print_path[0][1] + self.image_p1[1])

        _, left_offset, _ = self.distance(self.spray_point, markers[2])

        target_left = (int(
            target_point[0] - self.spray_point_offset[0] * self.cm_to_pixel - left_offset),
                       int(target_point[1] - self.spray_point_offset[1] * self.cm_to_pixel))

        _, right_offset, _ = self.distance(self.spray_point, markers[3])
        target_right = (int(
            target_point[0] + self.spray_point_offset[0] * self.cm_to_pixel + right_offset),
                        int(target_point[1] - self.spray_point_offset[1] * self.cm_to_pixel))

        left_target_distance, _, _ = self.distance(markers[2], target_left)
        right_target_distance, _, _ = self.distance(markers[3], target_right)

        self.draw_line(overlay, target_left, markers[0])
        self.draw_line(overlay, target_right, markers[1])

        left_target_corner_distance, a, b = self.distance(target_left, markers[0])
        self.write_text(overlay, str(int(round(left_target_corner_distance / self.cm_to_pixel))) + "cm",
                        (int(markers[0][0] + a / 2), int(markers[0][1] + b / 2)), color=(0, 0, 255))

        right_target_corner_distance, a, b = self.distance(target_right, markers[1])
        self.write_text(overlay, str(int(round(right_target_corner_distance / self.cm_to_pixel))) + "cm",
                        (int(markers[1][0] - a / 2), int(markers[1][1] + b / 2)), color=(0, 0, 255))

        left_motor_in_position = left_target_distance <= self.precision_in_cm * self.cm_to_pixel
        right_motor_in_position = right_target_distance <= self.precision_in_cm * self.cm_to_pixel

        if left_target_distance > right_target_distance and not left_motor_in_position:
            if target_left[1] < markers[2][1]:
                self.motors.spin_left_motor(-left_target_distance)
            else:
                self.motors.spin_left_motor(left_target_distance)
        elif not right_motor_in_position:
            if target_right[1] < markers[3][1]:
                self.motors.spin_right_motor(-right_target_distance)
            else:
                self.motors.spin_right_motor(right_target_distance)

        self.draw_circle(overlay, target_left, (0, 0, 255) if not left_motor_in_position else (0, 255, 0),
                         r=markers[2][2])
        self.draw_circle(overlay, target_right, (0, 0, 255) if not right_motor_in_position else (0, 255, 0),
                         r=markers[3][2])
        self.draw_circle(overlay, target_point, (0, 0, 255))

        if left_motor_in_position and right_motor_in_position:
            self.motors.spray()
            del self.print_path[0]

    @staticmethod
    def position_equals(pos1, pos2, precision=0):
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
