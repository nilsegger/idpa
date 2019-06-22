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
        self.motor_to_motor_starting_distance = self.calculate_length(self.motor_left.center, self.motor_right.center)
        self.motor_left_to_left_corner = self.calculate_length(self.motor_left.center, self.corner_left.center)
        self.motor_right_to_right_corner = self.calculate_length(self.motor_right.center, self.corner_right.center)
        self.calculate_distances()
        self.calculate_vectors()

    def calculate_distances(self):
        self.distance_corner_to_corner = self.calculate_length(self.corner_left.center, self.corner_right.center)
        self.motor_left_to_right_corner = self.calculate_length(self.motor_left.center, self.corner_right.center)
        self.motor_right_to_left_corner = self.calculate_length(self.motor_right.center, self.corner_left.center)

    def calculate_vectors(self):
        self.motor_left_to_left_corner_vec = self.calculate_vec(self.corner_left.center, self.motor_left.center)
        self.motor_right_to_right_corner_vec = self.calculate_vec(self.corner_right.center, self.motor_right.center)

    def spin_left_motor(self, speed):
        self.motor_left_to_left_corner += speed

    def spin_right_motor(self, speed):
        self.motor_right_to_right_corner += speed

        if speed < 0:
            self.motor_right.pos.add(self.motor_right_to_right_corner_vec, speed)

            temp_left_motor_corner_distance = self.calculate_length(self.motor_left.center, self.corner_left.center)
            current_motor_distance = self.calculate_length(self.motor_left.center, self.motor_right.center)

            while current_motor_distance > self.motor_to_motor_starting_distance and self.motor_left.center.y > self.motor_right.center.y:
                rotation_vec = self.calculate_vec(self.corner_left.center, self.motor_left.center)
                rotation_vec.rotate(-1)
                rotated_new_point = Vec2(copy=self.corner_left.center)
                rotated_new_point.add(rotation_vec, temp_left_motor_corner_distance)
                target_vec = self.calculate_vec(self.motor_left.center, rotated_new_point)
                self.motor_left.pos.add(target_vec, 0.01)

                # Korrektur, da mir ned direkt mitem roation vec schaffed wird de kreis immer kliner, mit dem dümmers wedr uf de rand use setze
                self.motor_left.pos.add(rotation_vec,
                                        temp_left_motor_corner_distance - self.calculate_length(self.corner_left.center, self.motor_left.center))

                current_motor_distance = self.calculate_length(self.motor_left.center, self.motor_right.center)

            angle = 180
            temp_pos = self.motor_right.pos
            temp_right_motor_corner_distance = self.calculate_length(self.motor_right.center, self.corner_right.center)
            while angle >= 90 and current_motor_distance > self.motor_to_motor_starting_distance:
                rotation_vec = self.calculate_vec(self.corner_right.center, self.motor_right.center)
                rotation_vec.rotate(1)
                rotated_point = Vec2(copy=self.corner_right.center)
                rotated_point.add(rotation_vec, temp_right_motor_corner_distance)
                forward_vec = self.calculate_vec(self.motor_right.center, rotated_point)
                self.motor_right.pos.add(forward_vec, 0.01)
                self.motor_right.pos.add(rotation_vec,
                                         temp_right_motor_corner_distance - self.calculate_length(self.motor_right.center, self.corner_right.center))
                current_motor_distance = self.calculate_length(self.motor_left.center, self.motor_right.center)

                angle = self.angle_between_vectors(self.motor_right.center, self.corner_right.center)
                print(angle)

            if angle <= 90:
                self.motor_right.pos = temp_pos

    @property
    def current_motor_to_motor_distance(self) -> float:
        return self.calculate_length(self.motor_left.center, self.motor_right.center)

    def move_left_motor(self, degree: float, forward: float):
        distance_to_corner = self.current_left_motor_to_corner_distance
        rotation_vec = self.calculate_vec(self.corner_left.center, self.motor_left.center)
        rotation_vec.rotate(degree)
        rotated_point = Vec2(copy=self.corner_left.center)
        rotated_point.add(rotation_vec, distance_to_corner)
        forward_vec = self.calculate_vec(self.motor_left.center, rotated_point)
        self.motor_left.pos.add(forward_vec, forward)
        self.motor_left.pos.add(rotation_vec, distance_to_corner - self.current_left_motor_to_corner_distance)

    @property
    def current_left_motor_to_corner_distance(self) -> float:
        return self.calculate_length(self.motor_left.center, self.corner_left.center)

    def move_right_motor(self, degree: float, forward: float):
        distance_to_corner = self.current_right_motor_to_corner_distance
        rotation_vec = self.calculate_vec(self.corner_right.center, self.motor_right.center)
        rotation_vec.rotate(degree)
        rotated_point = Vec2(copy=self.corner_right.center)
        rotated_point.add(rotation_vec, distance_to_corner)
        forward_vec = self.calculate_vec(self.motor_right.center, rotated_point)
        self.motor_right.pos.add(forward_vec, forward)
        self.motor_right.pos.add(rotation_vec, distance_to_corner - self.current_right_motor_to_corner_distance)

    @property
    def current_right_motor_to_corner_distance(self) -> float:
        return self.calculate_length(self.motor_right.center, self.corner_right.center)

    def check_tension(self):
        tension = False
        if self.calculate_length(self.corner_left.center, self.motor_left.center) + self.motor_to_motor_starting_distance + self.calculate_length(
                self.motor_right.center, self.corner_right.center) < self.distance_corner_to_corner:
            self.right_rope_too_tense = True
            self.left_rope_too_tense = True
            tension = True
        else:
            self.right_rope_too_tense = False
            self.left_rope_too_tense = False
        return tension

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):

        self.spin_right_motor(-50 * delta_time)
        self.calculate_vectors()
        self.calculate_distances()

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
            "black" if self.calculate_length(self.motor_left.center,
                                             self.motor_right.center) <= self.motor_to_motor_starting_distance else "red"))
