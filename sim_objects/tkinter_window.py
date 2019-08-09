import io
from tkinter import *
from datetime import datetime
import numpy
from PIL import Image

from sim_objects.object import Object
from sim_objects.simulation import Simulation


class Window(Frame):

    def __init__(self, master, simulation: Simulation):
        Frame.__init__(self, master)
        self.destroyed = False
        self.master = master
        self.master.bind_all('<KeyPress>', self.key_press)
        self.master.bind_all('<KeyRelease>', self.key_release)
        self.keys = {}
        self.canvas = None
        self.simulation = simulation
        self.delta_time = 0
        self.last_frame_datetime = datetime.now()
        self.pause = False
        self.ps_frame = None
        self.on_destroy = None
        self.init_window()

    def init_window(self):
        self.master.title("Spray Testbed")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self)
        self.canvas.pack(fill=BOTH, expand=1)

    def key_press(self, event):
        if event.keysym == 'space':
            pass
        else:
            self.keys[event.keysym] = True

    def key_release(self, event):
        if event.keysym == 'space':
            self.pause = not self.pause
        else:
            self.keys[event.keysym] = False

    def frame(self):
        self.delta_time = datetime.now().timestamp() - self.last_frame_datetime.timestamp()
        self.last_frame_datetime = datetime.now()

        if not self.pause:

            speed = 50

            if 'w' in self.keys and self.keys['w']:
                self.simulation.spin_left_motor(-speed * self.delta_time)
            if 's' in self.keys and self.keys['s']:
                self.simulation.spin_left_motor(speed * self.delta_time)

            if 'Up' in self.keys and self.keys['Up']:
                self.simulation.spin_right_motor(-speed * self.delta_time)
            if 'Down' in self.keys and self.keys['Down']:
                self.simulation.spin_right_motor(speed * self.delta_time)

            if 'q' in self.keys and self.keys['q']:
                self.simulation.spray()

            self.canvas.delete("all")
            self.simulation.draw(self.canvas, delta_time=self.delta_time, window=self)

        self.ps_frame = self.canvas.postscript(colormode='color', pagewidth=Object.CANVAS_WIDTH-1, pageheight=Object.CANVAS_HEIGHT-1)
        self.master.after(16, self.frame)

    def get_frame(self):
        return numpy.array(Image.open(io.BytesIO(self.ps_frame.encode('utf-8')))) if self.ps_frame is not None else None

    def set_on_destroy_callback(self, callback):
        self.on_destroy = callback

    def destroy(self):
        self.destroyed = True

        if self.on_destroy is not None:
            self.on_destroy()

        super().destroy()
