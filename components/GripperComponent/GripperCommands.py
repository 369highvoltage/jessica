from robot_map import RobotMap
from Command import InstantCommand, Command
from wpilib.timer import Timer


def move_left_right(speed: float) -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(speed, speed))


def suck() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(-1, -1))


def spit() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(1, 1))


def stop() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(0, 0))


class SuckFast(Command):
    def __init__(self):
        super().__init__()
        self.timer = Timer()

    def on_start(self):
        self.timer.start()

    def execute(self):
        RobotMap.gripper_component.set_motor_speeds(1, 1)
        if self.timer.hasPeriodPassed(0.4):
            RobotMap.gripper_component.set_motor_speeds(0, 0)
            self.finished()

    def on_end(self):
        pass


class SpitFast(Command):
    def __init__(self):
        super().__init__()
        self.timer = Timer()

    def on_start(self):
        self.timer.start()

    def execute(self):
        RobotMap.gripper_component.set_motor_speeds(-1, -1)
        if self.timer.hasPeriodPassed(0.4):
            RobotMap.gripper_component.set_motor_speeds(0, 0)
            self.finished()

    def on_end(self):
        pass


def spread() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_spread_state(True))


def close() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_spread_state(False))


def toggle_spread() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.toggle_spread_state())


