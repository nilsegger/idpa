from tkinter import *


class ObjectPositions:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def set_x(self, x: float):
        self.x = x

    def set_y(self, y: float):
        self.y = y

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @property
    def center_x(self):
        return self.x + self.w / 2

    @property
    def center_y(self):
        return self.y + self.h / 2


class Object:
    CANVAS_HEIGHT = 0
    CANVAS_WIDTH = 0

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):
        pass
