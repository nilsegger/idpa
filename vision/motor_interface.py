from sim_objects.simulation import Simulation

class MotorInterface:

    def __init__(self, min_speed, max_speed):
        self.min = min_speed
        self.max = max_speed

    def spin_left_motor(self, speed):
        pass

    def spin_right_motor(self, speed):
        pass

    def check_speed(self, speed):
        if speed < 0:
            if speed > -self.min:
                speed = -self.min
            if speed < -self.max:
                speed = -self.max
        elif speed > 0:
            if speed < self.min:
                speed = self.min
            elif speed > self.max:
                speed = self.max
        return speed

    def spray(self):
        pass


class SimulationMotorInterface(MotorInterface):

    def __init__(self, simulation : Simulation, min_speed, max_speed):
        self.simulation = simulation
        super().__init__(min_speed, max_speed)

    def spin_left_motor(self, speed):
        if speed == 0:
            return
        speed = self.check_speed(speed)
        self.simulation.spin_left_motor(speed)

    def spin_right_motor(self, speed):
        if speed == 0:
            return
        speed = self.check_speed(speed)
        self.simulation.spin_right_motor(speed)

    def spray(self):
        self.simulation.spray()
