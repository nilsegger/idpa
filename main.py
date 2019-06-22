import io
from time import sleep
from tkinter import *
from datetime import datetime

from PIL import Image

from objects.center_part import CenterPart
from objects.find_angle import AngleFinder
from objects.markers import Markers
from objects.object import Object, ObjectDimension

from os import system


class Window(Frame):

    def __init__(self, master, objects):
        Frame.__init__(self, master)
        self.destroyed = False
        self.master = master
        self.master.bind_all('<Key>', self.key_press)
        self.canvas = None
        self.objects = objects
        self.delta_time = 0
        self.last_frame_datetime = datetime.now()
        self.pause = False
        self.init_window()

    def init_window(self):
        self.master.title("Spray Testbed")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self)
        self.canvas.pack(fill=BOTH, expand=1)

    def key_press(self, event):
        if event.keysym == 'space':
            self.pause = not self.pause

    def frame(self):
        self.delta_time = datetime.now().timestamp() - self.last_frame_datetime.timestamp()
        self.last_frame_datetime = datetime.now()

        if not self.pause:
            self.canvas.delete("all")
            for obj in self.objects:
                obj.draw(self.canvas, delta_time=self.delta_time, window=self)

        self.master.after(16, self.frame)

    def save_frame(self):
        ps = self.canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img.save('test.jpg')

    def destroy(self):
        self.destroyed = True
        super().destroy()


root = Tk()
root.geometry("960x540")
Object.CANVAS_WIDTH = 960
Object.CANVAS_HEIGHT = 540

"""marker_radius = 10
border_margin = 5

center_part_width = 50
center_part_height = 50
center_part_marker_offset_x = 25
center_part_marker_offset_y = 25"""

center_part = ObjectDimension(200, 400, 50, 50)
motor_left = ObjectDimension(190, 390, 20, 20)
motor_right = ObjectDimension(240, 390, 20, 20)
corner_left = ObjectDimension(30, 30, 15, 15)
corner_right = ObjectDimension(Object.CANVAS_WIDTH - 45, 30, 15, 15)

app = Window(root, [
    AngleFinder(motor_left, motor_right, corner_left, corner_right),
    # CenterPart(border_margin + 100, 540 - center_part_height - border_margin, center_part_width, center_part_height,
    #           center_part_marker_offset_x, center_part_marker_offset_y, border_margin, marker_radius=marker_radius),
    # Markers(marker_radius, border_margin)
])

root.after(16, app.frame)
root.mainloop()
