from robot_map import RobotMap
from Command import Command, InstantCommand
from wpilib.timer import Timer


def curve_drive(linear: float, angular: float) -> InstantCommand:
    return InstantCommand(lambda: RobotMap.driver_component.set_curve(linear, angular))


class DriveByTime(Command):
    def __init__(self, seconds: float, speed: float):
        super().__init__()
        self._target_seconds = seconds
        self._speed = speed
        self.timer = Timer()

    def on_start(self):
        print("start driving forward by time")
        self.timer.start()

    def execute(self):
        RobotMap.driver_component.set_curve(self._speed, -RobotMap.driver_component.driver_gyro.getAngle()*0.2)
        if self.timer.hasPeriodPassed(self._target_seconds):
            RobotMap.driver_component.set_curve(0, 0)
            self.finished()

    def on_end(self):
        print("end driving forward by time")
        self.timer.stop()
        self.timer.reset()


class DriveByDistance(Command):
    def __init__(self, inches: float, speed: float):
        super().__init__()
        self._target_distance = inches
        self._speed = speed

    def on_start(self):
        RobotMap.driver_component.reset_drive_sensors()
        target_dist = "inches: " + str(self._target_distance)
        speed = "speed: " + str(self._speed)
        current_dist = "current: " + str(RobotMap.driver_component.current_distance)
        print("starting drive by distance, " + target_dist + " | " + speed + " | " + current_dist)

    def execute(self):
        RobotMap.driver_component.set_curve(self._speed, -RobotMap.driver_component.driver_gyro.getAngle()*0.2)
        if abs(RobotMap.driver_component.current_distance) >= abs(self._target_distance):
            RobotMap.driver_component.set_curve(0, 0)
            self.finished()

    def on_end(self):
        print("ending drive by distance, inches: " + str(self._target_distance) + " | speed: " + str(self._speed))


class Turn(Command):
    def __init__(self, degrees: float, speed: float):
        super().__init__()
        self._target_angle = degrees
        self._speed = speed

    def on_start(self):
        print("started turning")
        RobotMap.driver_component.reset_drive_sensors()

    def execute(self):
        RobotMap.driver_component.set_curve(0, self._speed)
        if abs(RobotMap.driver_component.driver_gyro.getAngle()) >= abs(self._target_angle):
            RobotMap.driver_component.set_curve(0, 0)
            self.finished()

    def on_end(self):
        print("ended turning")
