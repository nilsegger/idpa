from tkinter import *

import math


class Vec2:

    def __init__(self, x=0, y=0, copy=None):
        self.x = x
        self.y = y

        if copy is not None:
            self.x = copy.x
            self.y = copy.y

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    """@propery
    def angle(self):"""

    def rotate(self, degrees):
        radians = math.radians(degrees)
        cos_radian = math.cos(radians)
        sin_radian = math.sin(radians)
        x = self.x
        y = self.y
        self.x = cos_radian*x-sin_radian*y
        self.y = sin_radian*x+cos_radian*y

    def set_length(self, new_length=1):
        current_length = self.length
        self.x = self.x / (current_length / new_length)
        self.y = self.y / (current_length / new_length)

    def add(self, vec, distance):
        self.x += vec.x * distance
        self.y += vec.y * distance


class ObjectDimension:

    def __init__(self, x, y, w, h):
        self.pos = Vec2(x, y)
        self.size = Vec2(w, h)

    @property
    def pos2(self):
        return Vec2(self.pos.x + self.size.x, self.pos.y + self.size.y)

    @property
    def center(self):
        return Vec2(self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2)


class Object:
    CANVAS_HEIGHT = 0
    CANVAS_WIDTH = 0

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):
        pass

    @staticmethod
    def calculate_length(p1: Vec2, p2: Vec2) -> float:
        a = p2.x - p1.x
        b = p2.y - p1.y
        return math.sqrt(a * a + b * b)

    @staticmethod
    def calculate_vec(p1: Vec2, p2: Vec2, length=1) -> Vec2:
        vec = Vec2(p2.x - p1.x, p2.y - p1.y)
        vec.set_length(length)
        return vec

    @staticmethod
    def angle_between_vectors(v1: Vec2, v2: Vec2) -> float:
        #return math.atan2(v2.x-v1.x, v2.y-v1.y) * 180 / math.pi

        alpha = (v1.x * v2.x + v1.y * v2.y) / (v1.length * v2.length)
        return math.acos(alpha) * 180 / math.pi

    @staticmethod
    def draw_line(canvas: Canvas, p1: ObjectDimension, p2: ObjectDimension, fill_color=None):
        canvas.create_line(p1.center.x, p1.center.y, p2.center.x, p2.center.y, fill=fill_color)

    @staticmethod
    def draw_circle(canvas: Canvas, object_position: ObjectDimension, fill_color=None):
        canvas.create_oval(object_position.pos.x, object_position.pos.y, object_position.pos2.x, object_position.pos2.y,
                           fill=fill_color)
