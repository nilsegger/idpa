import random
from os import system
from datetime import datetime
import math

from .object import *


class AngleFinder(Object):

    def __init__(self, center_part: ObjectPositions, motor_left: ObjectPositions, motor_right: ObjectPositions,
                 corner_left: ObjectPositions, corner_right: ObjectPositions):
        self.center_part = center_part
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.corner_left = corner_left
        self.corner_right = corner_right

        self.motor_left_to_corner = None
        self.motor_right_to_corner = None
        self.calculate_starting_distances()

    @staticmethod
    def calculate_length(p1: ObjectPositions, p2: ObjectPositions) -> float:
        a = p2.center_x - p1.center_x
        b = p2.center_y - p1.center_y
        return math.sqrt(a * a + b * b)

    def calculate_starting_distances(self):
        self.motor_left_to_corner = self.calculate_length(self.motor_left, self.corner_left)
        self.motor_right_to_corner = self.calculate_length(self.motor_right, self.corner_right)

    def spin_left_motor(self, speed):
        self.motor_left += speed

    def spin_right_motor(self, speed):
        self.motor_right += speed

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):
        canvas.create_oval(self.corner_left.x, self.corner_left.y, self.corner_left.x2, self.corner_left.y2)
        canvas.create_oval(self.corner_right.x, self.corner_right.y, self.corner_right.x2, self.corner_right.y2)


