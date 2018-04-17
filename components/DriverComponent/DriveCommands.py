from robot_map import RobotMap
from Command import Command, InstantCommand
from wpilib.timer import Timer
from control_system import ControlSystem
from wpilib.pidcontroller import PIDController
from wpilib import DoubleSolenoid
from pid_output import PIDOutput


def set_low_gear() -> InstantCommand:
    return InstantCommand(RobotMap.driver_component.set_low_gear)


def set_high_gear() -> InstantCommand:
    return InstantCommand(RobotMap.driver_component.set_high_gear)


def toggle_gear() -> InstantCommand:
    return InstantCommand(RobotMap.driver_component.toggle_gear)


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


# kP, kI, kD, kF
linear_gains = (0.02, 0.0, 0.0, 0.0)


angular_tolerance = 2


class DriveByDistance(Command):
    def __init__(self, inches: float, speed: float):
        super().__init__()
        angular_gains = (0.02, 0.0001, 0.02, 0.0)
        self._target_distance = inches
        self._speed = speed
        self._linear = 0
        self._angular = 0

        # setup angular pid controller
        self.angular_controller = PIDController(
            *angular_gains,
            RobotMap.driver_component.pigeon,
            output=PIDOutput(self._update_angular)
        )
        self.angular_controller.setInputRange(-360, 360)
        self.angular_controller.setOutputRange(-1, 1)
        self.angular_controller.setAbsoluteTolerance(0.5)

        self.angular_controller.setSetpoint(0)

        # setup linear pid controller
        self.linear_controll = PIDController(
            *linear_gains,
            RobotMap.driver_component.
        )

    def _update_angular_pid(self):
        # return RobotMap.driver_component.pigeon.getYawPitchRoll
    def _update_angular(self, output):
        self._angular = output

    def on_start(self):
        RobotMap.driver_component.reset_drive_sensors()

        self.angular_controller.enable()

    def execute(self):
        if abs(RobotMap.driver_component.current_distance) >= abs(self._target_distance):
            RobotMap.driver_component.drive_train.curvatureDrive(0, 0, False)
            self.finished()
            return

        RobotMap.driver_component.drive_train.curvatureDrive(self._speed, self._angular, False)

    def on_end(self):
        self.angular_controller.disable()


class Turn(Command):
    def __init__(self, degrees: float, speed: float):
        super().__init__()
        angular_gains = (0.0125, 0.00005, 0.01, 0.0)
        self._target_angle = degrees
        self._speed = speed
        self._angular = 0

        self.angular_controller = PIDController(*angular_gains, RobotMap.driver_component.driver_gyro, output=self)
        self.angular_controller.setInputRange(-360, 360)
        self.angular_controller.setOutputRange(-1, 1)
        self.angular_controller.setAbsoluteTolerance(1)

        self.angular_controller.setSetpoint(degrees)

    def pidWrite(self, output):
        self._angular = output

    def on_start(self):
        RobotMap.driver_component.reset_drive_sensors()
        self.angular_controller.enable()

    def execute(self):
        if self.angular_controller.onTarget():
            RobotMap.driver_component.drive_train.curvatureDrive(0, 0, False)
            self.finished()
            return
        RobotMap.driver_component.drive_train.curvatureDrive(0, self._angular, True)

    def on_end(self):
        self.angular_controller.disable()
        print("done turning")
