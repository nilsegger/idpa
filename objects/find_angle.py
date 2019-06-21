import random
from os import system
from datetime import datetime
import math

from .object import *


class AngleFinder(Object):

    def __init__(self, motor_left: ObjectDimension, motor_right: ObjectDimension,
                 corner_left: ObjectDimension, corner_right: ObjectDimension):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.corner_left = corner_left
        self.corner_right = corner_right

        self.motor_to_motor_starting_distance = None
        self.distance_corner_to_corner = None
        self.motor_left_to_left_corner = None
        self.motor_right_to_right_corner = None
        self.motor_left_to_right_corner = None
        self.motor_right_to_left_corner = None

        self.motor_left_to_left_corner_vec = None
        self.motor_right_to_right_corner_vec = None

        self.calculate_starting_distances()

        self.right_rope_too_tense = False
        self.left_rope_too_tense = False

    def calculate_starting_distances(self):
        self.motor_to_motor_starting_distance = self.calculate_length(self.motor_left, self.motor_right)
        self.motor_left_to_left_corner = self.calculate_length(self.motor_left, self.corner_left)
        self.motor_right_to_right_corner = self.calculate_length(self.motor_right, self.corner_right)
        self.calculate_distances()
        self.calculate_vectors()

    def calculate_distances(self):
        self.distance_corner_to_corner = self.calculate_length(self.corner_left, self.corner_right)
        self.motor_left_to_right_corner = self.calculate_length(self.motor_left, self.corner_right)
        self.motor_right_to_left_corner = self.calculate_length(self.motor_right, self.corner_left)

    def calculate_vectors(self):
        self.motor_left_to_left_corner_vec = self.calculate_vec(self.corner_left, self.motor_left)
        self.motor_right_to_right_corner_vec = self.calculate_vec(self.corner_right, self.motor_right)

    def spin_left_motor(self, speed):
        self.motor_left_to_left_corner += speed

    def spin_right_motor(self, speed):
        self.motor_right_to_right_corner += speed

        if speed < 0:
            self.motor_right.pos.add(self.motor_right_to_right_corner_vec, speed)

            # versueche motor distanz wedr anezbecho numme mit seil dreihe
            temp_motor_pos = Vec2(copy=self.motor_left.pos)
            current_motor_distance = self.calculate_length(self.motor_left, self.motor_right)
            angle = self.angle_between_vectors(self.corner_left.center, self.motor_left.center)
            while angle > 0 and current_motor_distance > self.motor_to_motor_starting_distance and self.motor_left.center.y >= self.motor_right.center.y:
                vec = self.calculate_vec(self.corner_left, self.motor_left)
                vec.rotate(-0.1)
                new_left_motor_position = Vec2(copy=self.corner_left.pos)
                new_left_motor_position.add(vec, self.motor_left_to_left_corner)
                self.motor_left.pos = new_left_motor_position

                current_motor_distance = self.calculate_length(self.motor_left, self.motor_right)
                angle = self.angle_between_vectors(self.corner_left.center, self.motor_left.center)
                print(angle)

                """vec.rotate(-1)
                new_motor_pos = Vec2(copy=self.corner_left.pos)
                new_motor_pos.add(vec, self.motor_left_to_left_corner)
                self.motor_left.pos = new_motor_pos"""

            if math.floor(angle) == 0:
                self.motor_left.pos = temp_motor_pos
            # print(angle)
            print(current_motor_distance)

    def check_tension(self):
        if self.motor_left_to_left_corner + self.motor_to_motor_starting_distance + self.motor_right_to_right_corner < self.distance_corner_to_corner:
            self.right_rope_too_tense = True
            self.left_rope_too_tense = True
        else:
            self.right_rope_too_tense = True
            self.left_rope_too_tense = True

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):

        self.spin_right_motor(-10 * delta_time)
        self.calculate_vectors()
        self.calculate_distances()

        """vec = self.calculate_vec(self.corner_left, self.motor_left)
        print(vec.x, "/", vec.y)
        vec.rotate(10)
        print(vec.x, "/", vec.y)
        print(vec.length)
        new_motor_pos = Vec2(copy=self.corner_left.pos)
        new_motor_pos.add(vec, self.motor_left_to_left_corner)
        print(self.motor_left_to_left_corner)
        print(new_motor_pos.x, "/", new_motor_pos.y)
        self.motor_left.pos = new_motor_pos
        print("---")"""

        self.check_tension()

        self.draw_circle(canvas, self.corner_left, fill_color="red")
        self.draw_circle(canvas, self.corner_right, fill_color="red")

        self.draw_circle(canvas, self.motor_left, fill_color="blue")
        self.draw_circle(canvas, self.motor_right, fill_color="blue")

        self.draw_circle(canvas, ObjectDimension(self.corner_left.center.x - self.motor_left_to_left_corner,
                                                 self.corner_left.center.y - self.motor_left_to_left_corner,
                                                 self.motor_left_to_left_corner * 2,
                                                 self.motor_left_to_left_corner * 2))

        self.draw_circle(canvas, ObjectDimension(self.corner_right.center.x - self.motor_right_to_right_corner,
                                                 self.corner_right.center.y - self.motor_right_to_right_corner,
                                                 self.motor_right_to_right_corner * 2,
                                                 self.motor_right_to_right_corner * 2))

        self.draw_line(canvas, self.motor_left, self.corner_left,
                       fill_color=("black" if not self.left_rope_too_tense else "red"))
        self.draw_line(canvas, self.motor_right, self.corner_right,
                       fill_color=("black" if not self.right_rope_too_tense else "red"))

        self.draw_line(canvas, self.motor_left, self.motor_right, fill_color=(
            "black" if self.calculate_length(self.motor_left,
                                             self.motor_right) <= self.motor_to_motor_starting_distance + 5 else "red"))
