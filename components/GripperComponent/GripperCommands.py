from robot_map import RobotMap
from Command import InstantCommand, Command
from wpilib.timer import Timer
from .GripperComponent import GripperComponent


def move_left_right(speed: float) -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(speed, speed))


def suck() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(1, 1))


def spit() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_motor_speeds(-1, -1))


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
    def __init__(self, speed=1):
        super().__init__()
        self.timer = Timer()
        self._speed = -speed

    def on_start(self):
        self.timer.start()
        print("started spit")

    def execute(self):
        RobotMap.gripper_component.set_motor_speeds(self._speed, self._speed)
        if self.timer.hasPeriodPassed(1):
            RobotMap.gripper_component.set_motor_speeds(0, 0)
            self.finished()

    def on_end(self):
        self.timer.stop()
        self.timer.reset()
        print("ended spit")


def spread() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_spread_state(True))


def close() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.set_spread_state(False))


def toggle_spread() -> InstantCommand:
    return InstantCommand(lambda: RobotMap.gripper_component.toggle_spread_state())


class LiftTo(Command):
    running = None

    def __init__(self, pos: str):
        super().__init__()
        self._target_pos = GripperComponent.lift_positions[pos]
        self._speed = 0

    def on_start(self):
        if LiftTo.running is not None:
            LiftTo.running.finished()
        if Toggle.running is not None:
            Toggle.running.finished()
        LiftTo.running = self
        diff = RobotMap.gripper_component.pot.get() - self._target_pos
        if diff == 0:
            self._speed = 0
        else:
            self._speed = (diff / -diff) / 2

    def execute(self):
        if 0.2 < RobotMap.gripper_component.pot.get() - self._target_pos < 0.2:
            RobotMap.gripper_component.set_lift_motor(0)
            self.finished()
            return
        RobotMap.gripper_component.set_lift_motor(self._speed)

    def on_end(self):
        LiftTo.running = None


class Toggle(Command):
    running = None

    def __init__(self):
        super().__init__()
        current_pos = RobotMap.gripper_component.current_lift_state()
        if current_pos == "up":
            self._target_pos = GripperComponent.lift_positions["down"]
        else:
            self._target_pos = GripperComponent.lift_positions["up"]
        self._speed = 0

    def on_start(self):
        if LiftTo.running is not None:
            LiftTo.running.finished()
        if Toggle.running is not None:
            Toggle.running.finished()
        Toggle.running = self
        diff = RobotMap.gripper_component.pot.get() - self._target_pos
        if diff == 0:
            self._speed = 0
        else:
            self._speed = (diff / -diff) / 2

    def execute(self):
        if 0.2 < RobotMap.gripper_component.pot.get() - self._target_pos < 0.2:
            RobotMap.gripper_component.set_lift_motor(0)
            self.finished()
            return
        RobotMap.gripper_component.set_lift_motor(self._speed)

    def on_end(self):
        Toggle.running = None
