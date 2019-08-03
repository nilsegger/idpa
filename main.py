from tkinter import *
from sim_objects.simulation import Simulation
from sim_objects.object import Object, ObjectDimension
from sim_objects.tkinter_window import Window

from vision.vision import Vision
from vision.camera import SimulationCamera

root = Tk()
root.geometry("960x540")
Object.CANVAS_WIDTH = 960
Object.CANVAS_HEIGHT = 540

center_part = ObjectDimension(200, 400, 50, 50)
motor_left = ObjectDimension(190, 390, 20, 20)
motor_right = ObjectDimension(240, 390, 20, 20)
corner_left = ObjectDimension(30, 30, 15, 15)
corner_right = ObjectDimension(Object.CANVAS_WIDTH - 45, 30, 15, 15)

simulation = Simulation(motor_left, motor_right, corner_left, corner_right)
app = Window(root, simulation)

camera = SimulationCamera(app)
vision = Vision(camera)
vision.run_in_thread()

root.after(16, app.frame)
root.mainloop()



# Motor links, Motor Rechts, Spraydose
