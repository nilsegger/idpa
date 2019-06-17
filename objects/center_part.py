import random
from os import system
from datetime import datetime
import math

from .object import *


class CenterPart(Object):

    def __init__(self, x, y, width, height, marker_center_offset_x, marker_center_offset_y, border_margin,
                 fill_color="#828DFF",
                 marker_radius=5, marker_fill_color="#FF653E"):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.fill_color = fill_color
        self.marker_radius = marker_radius
        self.marker_fill_color = marker_fill_color
        self.marker_center_offset_x = marker_center_offset_x
        self.marker_center_offset_y = marker_center_offset_y

        self.border_margin = border_margin

        self.motor_positions = []

        self.last_x = None
        self.last_y = None
        self.last_print = datetime.now()

        self.motor_positions_printed = False

        self.target_x = None
        self.target_y = 0

        self.points_sprayed = []

        self.print_info()

    def set_target(self, pos_x, pos_y):
        self.target_x = pos_x
        self.target_y = pos_y

    def spin_right_motor(self, speed):
        pass

    def spin_left_motor(self, speed):
        pass

    POPPED = 0

    def spray(self):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        if len(self.points_sprayed) >= 3:
            p1x, p1y = self.points_sprayed[-2]
            p2x, p2y = self.points_sprayed[-1]
            y = center_y - p1y
            x = center_x - p1x
            if x == 0 and p1y == p2y:
                # Vertikali linie
                self.points_sprayed.pop(len(self.points_sprayed) - 1)
                self.POPPED += 1
            else:
                m = y / x
                #  ey - p1y = m(x - p1x) -> ey = mx - mp1x + p1y
                if p2y == (m * p2x - m * p1x + p1y):
                    self.points_sprayed.pop(len(self.points_sprayed) - 1)
                    self.POPPED += 1

        self.points_sprayed.append((center_x, center_y))

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):

        for i in range(len(self.points_sprayed) - 1):
            p1x, p1y = self.points_sprayed[i]
            p2x, p2y = self.points_sprayed[i + 1]
            canvas.create_line(p1x, p1y, p2x, p2y, fill="#000")

        self.x += random.randint(1, 50) * delta_time
        self.y -= random.randint(1, 50) * delta_time

        canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.fill_color,
                                outline="#000", width=1)

        center_x = self.x + (self.width / 2)
        center_y = self.y + (self.height / 2)

        self.motor_positions = [
            [
                center_x - self.marker_center_offset_x - self.marker_radius,
                center_y - self.marker_center_offset_y - self.marker_radius,
                center_x - self.marker_center_offset_x + self.marker_radius,
                center_y - self.marker_center_offset_y + self.marker_radius,
                center_x - self.marker_center_offset_x,
                center_y - self.marker_center_offset_y
            ],
            [
                center_x + self.marker_center_offset_x - self.marker_radius,
                center_y - self.marker_center_offset_y - self.marker_radius,
                center_x + self.marker_center_offset_x + self.marker_radius,
                center_y - self.marker_center_offset_y + self.marker_radius,
                center_x + self.marker_center_offset_x,
                center_y - self.marker_center_offset_y
            ]
        ]

        for motor in self.motor_positions:
            canvas.create_oval(motor[0], motor[1], motor[2], motor[3], fill=self.marker_fill_color)

        a = self.motor_positions[0][4] - self.border_margin
        b = self.motor_positions[0][5] - self.border_margin
        distance_motor_left_to_left_corner = math.sqrt(a * a + b * b)

        canvas.create_oval(self.border_margin - distance_motor_left_to_left_corner,
                           self.border_margin - distance_motor_left_to_left_corner,
                           self.border_margin + distance_motor_left_to_left_corner,
                           self.border_margin + distance_motor_left_to_left_corner)

        a = self.motor_positions[1][4] - (self.CANVAS_WIDTH - self.border_margin)
        b = self.motor_positions[1][5] - self.border_margin
        distance_motor_right_to_right_corner = math.sqrt(a * a + b * b)
        canvas.create_oval((self.CANVAS_WIDTH - self.border_margin) - distance_motor_right_to_right_corner,
                           self.border_margin - distance_motor_right_to_right_corner,
                           (self.CANVAS_WIDTH - self.border_margin) + distance_motor_right_to_right_corner,
                           self.border_margin + distance_motor_right_to_right_corner)

        canvas.create_oval(center_x - self.marker_radius, center_y - self.marker_radius, center_x + self.marker_radius,
                           center_y + self.marker_radius, fill="#6EFF40")

        self.spray()

        self.print_info()

    def print_info(self):

        if not (self.last_print is not None and datetime.now().timestamp() - self.last_print.timestamp() > 0.5):
            return

        if self.x != self.last_x or self.y != self.last_y or (len(self.motor_positions) > 0
                                                              and not self.motor_positions_printed):
            system("cls")
            print("Spray Position: ", self.x + self.width / 2, "/", self.y + self.height / 2)

            if self.target_x is not None:
                a = self.target_x - self.x + self.width / 2
                b = self.target_y - self.y + self.height / 2
                print("Target: ", self.target_x, "/", self.target_y, " Distance to spray point: ",
                      math.sqrt(a * a + b * b))

            print("---")

            if len(self.motor_positions) > 0:
                print("Motor Left Position: ", self.motor_positions[0][4], "/", self.motor_positions[0][5])
                a = self.motor_positions[0][4] - self.border_margin
                b = self.motor_positions[0][5] - self.border_margin
                print("Distance to left corner : ", math.sqrt(a * a + b * b))

                print("---")

                print("Motor Right Position: ", self.motor_positions[1][4], "/", self.motor_positions[1][5])
                a = self.motor_positions[1][4] - (self.CANVAS_WIDTH - self.border_margin)
                b = self.motor_positions[1][5] - self.border_margin
                print("Distance to right corner : ", math.sqrt(a * a + b * b))
                self.motor_positions_printed = True

            print("---")

            print(len(self.points_sprayed), " points sprayed.")
            print("Popped: ", self.POPPED)
            self.last_x = self.x
            self.last_y = self.y

            self.last_print = datetime.now()
