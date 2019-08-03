from sim_objects.tkinter_window import Window


class Camera:

    def get_frame(self):
        pass


class SimulationCamera(Camera):

    def __init__(self, window: Window):
        self.window = window

    def get_frame(self):
        return self.window.get_frame()
