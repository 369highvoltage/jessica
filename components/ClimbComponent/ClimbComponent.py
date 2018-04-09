from wpilib import Victor


class ClimberComponent:
    def __init__(self):
        self.climb_motor_1 = Victor(2)
        self.climb_motor_2 = Victor(5)

    def climb(self):
        self.climb_motor_1.set(-1)
        self.climb_motor_2.set(-1)

    def stop(self):
        self.climb_motor_1.set(0)
        self.climb_motor_2.set(0)

    def release(self):
        self.climb_motor_1.set(0.5)
        self.climb_motor_2.set(0.5)
