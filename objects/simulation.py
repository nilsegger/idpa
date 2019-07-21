import random
from os import system
from datetime import datetime
import math

from .object import *


class Simulation(Object):

    def __init__(self, motor_left: ObjectDimension, motor_right: ObjectDimension,
                 corner_left: ObjectDimension, corner_right: ObjectDimension):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.corner_left = corner_left
        self.corner_right = corner_right

        self.motor_to_motor_starting_distance = None
        self.corner_to_corner_distance = None
        self.left_rope_distance = None
        self.right_rope_distance = None

        self.points_sprayed = []

        self.calculate_starting_distances()

        self.ropes_too_tense = False

        self.slow_forward = 0.05
        self.medium_forward = 0.1
        self.fast_forward = 1
        self.faster_than_fast_forward = 1.25

    def calculate_starting_distances(self):
        self.motor_to_motor_starting_distance = self.calculate_length(self.motor_left.center, self.motor_right.center)
        self.left_rope_distance = self.calculate_length(self.motor_left.center, self.corner_left.center)
        self.right_rope_distance = self.calculate_length(self.motor_right.center, self.corner_right.center)
        self.corner_to_corner_distance = self.calculate_length(self.corner_left.center, self.corner_right.center)

    def spin_left_motor(self, speed):

        if speed < 0 and self.has_rope_tension():
            return

        self.left_rope_distance += speed
        self.motor_left.pos.add(self.motor_left_to_left_corner_vec, speed)

        if speed < 0:
            if self.ropes_intercept:
                while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance and self.motor_right.center.y >= self.motor_left.center.y:
                    self.move_right_motor(1, self.slow_forward)
                    if self.motor_right.center.y < self.motor_left.center.y:
                        self.move_right_motor(-1, self.slow_forward)
                        break

                last_motor_distance = self.current_motor_to_motor_distance
                while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance and last_motor_distance >= self.current_motor_to_motor_distance:
                    last_motor_distance = self.current_motor_to_motor_distance
                    self.move_left_motor(-1, self.slow_forward)
                if last_motor_distance < self.current_motor_to_motor_distance:
                    self.move_left_motor(1, self.slow_forward)

            else:
                while self.motor_right.center.y > self.motor_left.center.y:
                    self.move_right_motor(1, self.slow_forward)
                while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance and not self.has_rope_tension():
                    self.move_right_motor(1, self.medium_forward)
                    while self.motor_right.center.y < self.motor_left.center.y:
                        self.move_left_motor(-1, self.medium_forward)
        else:
            while self.current_motor_to_motor_distance < self.motor_to_motor_starting_distance:
                self.move_left_motor(1, self.slow_forward)
                while self.motor_right.center.y < self.motor_left.center.y <= self.corner_right.center.y + self.right_rope_distance:
                    self.move_right_motor(-1, self.fast_forward)

            left_motor_to_right_corner_vec = self.calculate_vec(self.corner_right.center, self.motor_left.center)
            right_motor_to_right_corner_vec = self.calculate_vec(self.corner_right.center, self.motor_right.center)

            while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance \
                    and not left_motor_to_right_corner_vec.compare(right_motor_to_right_corner_vec, 2):
                self.move_right_motor(1, self.faster_than_fast_forward)

                left_motor_to_right_corner_vec = self.calculate_vec(self.corner_right.center, self.motor_left.center)
                right_motor_to_right_corner_vec = self.calculate_vec(self.corner_right.center, self.motor_right.center)

            if self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance:
                motor_to_motor_forward = self.calculate_vec(self.motor_right.center, self.motor_left.center)
                new_pos = Vec2(copy=self.motor_right.pos)
                new_pos.add(motor_to_motor_forward, self.motor_to_motor_starting_distance - 0.1)
                self.motor_left.pos = new_pos
                self.left_rope_distance = self.calculate_length(self.motor_left.center, self.corner_left.center)

    def spin_right_motor(self, speed):

        if speed < 0 and self.has_rope_tension():
            return

        self.right_rope_distance += speed
        self.motor_right.pos.add(self.motor_right_to_right_corner_vec, speed)

        if speed < 0:
            if self.ropes_intercept:
                while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance and self.motor_left.center.y >= self.motor_right.center.y:
                    self.move_left_motor(-1, self.slow_forward)
                    if self.motor_left.center.y < self.motor_right.center.y:
                        self.move_left_motor(1, self.slow_forward)
                        break

                last_motor_distance = self.current_motor_to_motor_distance
                while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance and last_motor_distance >= self.current_motor_to_motor_distance:
                    last_motor_distance = self.current_motor_to_motor_distance
                    self.move_right_motor(1, self.slow_forward)
                if last_motor_distance < self.current_motor_to_motor_distance:
                    self.move_right_motor(-1, self.slow_forward)

            else:
                while self.motor_left.center.y > self.motor_right.center.y:
                    self.move_left_motor(-1, self.slow_forward)
                while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance and not self.has_rope_tension():
                    self.move_left_motor(-1, self.medium_forward)
                    while self.motor_left.center.y < self.motor_right.center.y:
                        self.move_right_motor(1, self.medium_forward)
        else:
            while self.current_motor_to_motor_distance < self.motor_to_motor_starting_distance:
                self.move_right_motor(-1, self.slow_forward)
                while self.motor_left.center.y < self.motor_right.center.y <= self.corner_left.center.y + self.left_rope_distance:
                    self.move_left_motor(1, self.fast_forward)

            left_motor_to_left_corner_vec = self.calculate_vec(self.corner_left.center, self.motor_left.center)
            right_motor_to_left_corner_vec = self.calculate_vec(self.corner_left.center, self.motor_right.center)

            while self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance \
                    and not left_motor_to_left_corner_vec.compare(right_motor_to_left_corner_vec, 2):
                self.move_left_motor(-1, self.faster_than_fast_forward)

                left_motor_to_left_corner_vec = self.calculate_vec(self.corner_left.center, self.motor_left.center)
                right_motor_to_left_corner_vec = self.calculate_vec(self.corner_left.center, self.motor_right.center)

            if self.current_motor_to_motor_distance > self.motor_to_motor_starting_distance:
                motor_to_motor_forward = self.calculate_vec(self.motor_left.center, self.motor_right.center)
                new_pos = Vec2(copy=self.motor_left.pos)
                new_pos.add(motor_to_motor_forward, self.motor_to_motor_starting_distance - 0.1)
                self.motor_right.pos = new_pos
                self.right_rope_distance = self.calculate_length(self.motor_right.center, self.corner_right.center)

    @property
    def motor_right_to_right_corner_vec(self):
        return self.calculate_vec(self.corner_right.center, self.motor_right.center)

    @property
    def motor_left_to_left_corner_vec(self):
        return self.calculate_vec(self.corner_left.center, self.motor_left.center)

    @property
    def ropes_intercept(self) -> bool:
        return self.right_rope_distance + self.left_rope_distance >= self.corner_to_corner_distance

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

    def has_rope_tension(self):
        tension = False
        if self.calculate_length(self.corner_left.center,
                                 self.motor_left.center) + self.motor_to_motor_starting_distance + self.calculate_length(
            self.motor_right.center, self.corner_right.center) < self.corner_to_corner_distance:
            self.ropes_too_tense = True
            tension = True
        else:
            self.ropes_too_tense = False
        return tension

    @property
    def spray_point(self) -> Vec2:
        motor_vec = self.calculate_vec(self.motor_left.center, self.motor_right.center)
        motor_center_point = Vec2(copy=self.motor_left.center)
        motor_center_point.add(motor_vec, self.current_motor_to_motor_distance / 2)
        motor_vec.rotate(90)
        motor_center_point.add(motor_vec, 25)
        return motor_center_point

    def spray(self):
        self.points_sprayed.append(self.spray_point)

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):
        self.has_rope_tension()

        for sprayed_point in self.points_sprayed:
            self.draw_point(canvas, sprayed_point, 3, "yellow", "")

        self.draw_circle(canvas, self.corner_left, fill_color="red")
        self.draw_circle(canvas, self.corner_right, fill_color="red")

        self.draw_circle(canvas, self.motor_left, fill_color="blue")
        self.draw_circle(canvas, self.motor_right, fill_color="blue")

        self.draw_circle(canvas, ObjectDimension(self.corner_left.center.x - self.left_rope_distance,
                                                 self.corner_left.center.y - self.left_rope_distance,
                                                 self.left_rope_distance * 2,
                                                 self.left_rope_distance * 2))

        self.draw_circle(canvas, ObjectDimension(self.corner_right.center.x - self.right_rope_distance,
                                                 self.corner_right.center.y - self.right_rope_distance,
                                                 self.right_rope_distance * 2,
                                                 self.right_rope_distance * 2))

        self.draw_line(canvas, self.motor_left, self.corner_left,
                       fill_color=("black" if not self.ropes_too_tense else "red"))
        self.draw_line(canvas, self.motor_right, self.corner_right,
                       fill_color=("black" if not self.ropes_too_tense else "red"))

        self.draw_line(canvas, self.motor_left, self.motor_right, fill_color=(
            "black" if self.calculate_length(self.motor_left.center,
                                             self.motor_right.center) <= self.motor_to_motor_starting_distance else "red"))

        self.draw_point(canvas, self.spray_point, 3, "green")
