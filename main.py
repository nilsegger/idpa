from tkinter import *
from simulation.simulation import Simulation
from simulation.object import Object, ObjectDimension
from simulation.tkinter_window import Window

from vision.vision2 import Vision
from vision.camera import SimulationCamera
from vision.image_preparation import prepare_image
from vision.motor_interface import SimulationMotorInterface

import sys
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

if len(sys.argv) == 1:
    print("Kein Bild mitgegeben. Test Bild wird verwendet.")
    image_to_draw = prepare_image("vision/test_bild.jpg")
else:
    image_to_draw = prepare_image(sys.argv[1])

print("Image prepared.")

if image_to_draw is None:
    print("Image can not be null to continue.")
    exit(-1)

motor_interface = SimulationMotorInterface(simulation, 0.001, 5)

vision = Vision(motor_interface, 500, 1.5, camera, image_to_draw, (0, 25), corner_right.center.x - corner_left.center.x)
vision.run_in_thread()


def on_destroy_callback():
    vision.quit()


app.set_on_destroy_callback(on_destroy_callback)

root.after(16, app.frame)
root.mainloop()
