import io
from time import sleep
from tkinter import *
from datetime import datetime

from PIL import Image

from objects.center_part import CenterPart
from objects.markers import Markers
from objects.object import Object

from os import system


class Window(Frame):

    def __init__(self, master, objects):
        Frame.__init__(self, master)
        self.destroyed = False
        self.master = master
        self.canvas = None
        self.objects = objects
        self.delta_time = 0
        self.x = 0
        self.last_frame_datetime = datetime.now()
        self.init_window()

    def init_window(self):
        self.master.title("Spray Testbed")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self)
        self.canvas.pack(fill=BOTH, expand=1)

    def frame(self):
        self.delta_time = datetime.now().timestamp() - self.last_frame_datetime.timestamp()
        self.last_frame_datetime = datetime.now()
        self.canvas.delete("all")

        for obj in self.objects:
            obj.draw(self.canvas, delta_time=self.delta_time, window=self)

        # self.x += 100 * self.delta_time
        """self.canvas.create_oval(self.x, 0, self.x + 50, 50, outline="#f11",
                                fill="#1f1", width=2)"""

        # self.canvas.create_text(50, 10, fill="darkblue", font="Consolas 20 italic bold",
        #                        text=str((1000 / (self.delta_time * 1000)).__round__()) + " FPS")

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

marker_radius = 10
border_margin = 5

center_part_width = 50
center_part_height = 50
center_part_marker_offset_x = 25
center_part_marker_offset_y = 25

app = Window(root, [
    CenterPart(border_margin + 100, 540 - center_part_height - border_margin, center_part_width, center_part_height,
               center_part_marker_offset_x, center_part_marker_offset_y, border_margin, marker_radius=marker_radius),
    Markers(marker_radius, border_margin)])

root.after(16, app.frame)
root.mainloop()
