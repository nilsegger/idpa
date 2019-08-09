from tkinter import *
from sim_objects.simulation import Simulation
from sim_objects.object import Object, ObjectDimension
from sim_objects.tkinter_window import Window

from vision.vision import Vision
from vision.camera import SimulationCamera

Object.CANVAS_WIDTH = 1200
Object.CANVAS_HEIGHT = 720

root = Tk()
root.geometry(str(Object.CANVAS_WIDTH) + "x" + str(Object.CANVAS_HEIGHT))

center_x, center_y = Object.CANVAS_WIDTH / 2, Object.CANVAS_HEIGHT / 2

center_part = ObjectDimension(center_x, center_y, 50, 50)

motor_radius = 15
margin_delta = 30

motor_left = ObjectDimension(center_x - margin_delta - motor_radius / 2, center_y - motor_radius, motor_radius * 2,
                             motor_radius * 2)
motor_right = ObjectDimension(center_x + margin_delta - motor_radius, center_y - motor_radius, motor_radius * 2,
                              motor_radius * 2)

corner_radius = 15

corner_left = ObjectDimension(margin_delta, margin_delta, corner_radius * 2, corner_radius * 2)
corner_right = ObjectDimension(Object.CANVAS_WIDTH - margin_delta - corner_radius * 2, margin_delta, corner_radius * 2,
                               corner_radius * 2)

simulation = Simulation(motor_left, motor_right, corner_left, corner_right)
app = Window(root, simulation)

camera = SimulationCamera(app)
vision = Vision(camera)
vision.run_in_thread()


def on_destroy_callback():
    vision.quit()


app.set_on_destroy_callback(on_destroy_callback)

root.after(16, app.frame)
root.mainloop()

# Motor links, Motor Rechts, Spraydose
