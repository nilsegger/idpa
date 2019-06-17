from os import system

from .object import *


class CenterPart(Object):

    def __init__(self, x, y, width, height, marker_center_offset_x, marker_center_offset_y, fill_color="#828DFF",
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

        self.last_x = None
        self.last_y = None

        self.print_info()

    def draw(self, canvas: Canvas, delta_time: float, window: Frame):
        canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.fill_color,
                                outline="#000", width=1)

        center_x = self.x + (self.width / 2)
        center_y = self.y + (self.height / 2)

        markers = [
            [
                center_x - self.marker_center_offset_x - self.marker_radius,
                center_y - self.marker_center_offset_y - self.marker_radius,
                center_x - self.marker_center_offset_x + self.marker_radius,
                center_y - self.marker_center_offset_y + self.marker_radius,
            ],
            [
                center_x + self.marker_center_offset_x - self.marker_radius,
                center_y - self.marker_center_offset_y - self.marker_radius,
                center_x + self.marker_center_offset_x + self.marker_radius,
                center_y - self.marker_center_offset_y + self.marker_radius,
            ]
        ]

        for marker in markers:
            canvas.create_oval(marker[0], marker[1], marker[2], marker[3], fill=self.marker_fill_color)

        canvas.create_oval(center_x - self.marker_radius, center_y - self.marker_radius, center_x + self.marker_radius,
                           center_y + self.marker_radius, fill="#6EFF40")

        self.print_info()

    def print_info(self):

        if self.x != self.last_x or self.y != self.last_y:
            system("cls")
            print("Position: ", self.x, "/", self.y)
            self.last_x = self.x
            self.last_y = self.y
