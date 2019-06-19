from .object import *


class Markers(Object):

    def __init__(self, radius, border_margin, fill_color="#FF653E"):
        self.radius = radius
        self.border_margin = border_margin
        self.fill_color = fill_color
        d = self.radius * 2
        self.markers = [
            [
                self.border_margin,
                self.border_margin,
                self.border_margin + d,
                self.border_margin + d
            ],
            [
                self.CANVAS_WIDTH - self.border_margin - d,
                self.border_margin,
                self.CANVAS_WIDTH - self.border_margin,
                self.border_margin + d
            ],
            [
                self.border_margin,
                self.CANVAS_HEIGHT - self.border_margin - d,
                self.border_margin + d,
                self.CANVAS_HEIGHT - self.border_margin
            ],
            [
                self.CANVAS_WIDTH - self.border_margin - d,
                self.CANVAS_HEIGHT - self.border_margin - d,
                self.CANVAS_WIDTH - self.border_margin,
                self.CANVAS_HEIGHT - self.border_margin
            ]
        ]

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):
        for marker in self.markers:
            canvas.create_oval(marker[0], marker[1], marker[2], marker[3], fill=self.fill_color)
