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

    def __init__(self, pos: str):
        super().__init__()
        self._target_pos = GripperComponent.lift_positions[pos]
        self._speed = 0

    def on_start(self):
        RobotMap.gripper_component.trigger_event(GripperComponent.EVENTS.gripper_started_moving, data=self)
        RobotMap.gripper_component.add_listener(GripperComponent.EVENTS.gripper_started_moving, self.check_if_in_use)

    def check_if_in_use(self, data: GripperComponent.EVENTS.gripper_started_moving_data):
        if self != data:
            self.interrupt()

    def on_interrupted(self):
        print("interupted LiftTo")

    def execute(self):
        if -0.02 < RobotMap.gripper_component.pot.get() - self._target_pos < 0.02:
            RobotMap.gripper_component.set_lift_motor(0)
            self.finished()
            return
        diff = RobotMap.gripper_component.pot.get() - self._target_pos
        if diff == 0:
            self._speed = 0
        else:
            self._speed = (abs(diff) / diff) * 0.50
        RobotMap.gripper_component.set_lift_motor(self._speed)

    def on_end(self):
        RobotMap.gripper_component.remove_listener(GripperComponent.EVENTS.gripper_started_moving, self.check_if_in_use)

class Toggle(Command):

    def __init__(self):
        super().__init__()
        self._target_pos = None
        self._speed = 0

    def on_start(self):
        RobotMap.gripper_component.trigger_event(GripperComponent.EVENTS.gripper_started_moving, data=self)
        RobotMap.gripper_component.add_listener(GripperComponent.EVENTS.gripper_started_moving, self.check_if_in_use)
        current_pos = RobotMap.gripper_component.current_lift_state()
        if current_pos == "up":
            self._target_pos = GripperComponent.lift_positions["down"]
        else:
            self._target_pos = GripperComponent.lift_positions["up"]
        self._speed = 0


        current_pos_s = "current: " + current_pos + str(RobotMap.gripper_component.pot.get())
        target_s = "target: " + str(self._target_pos)
        speed_s = "speed: " + str(self._speed)
        print("start toggle " + current_pos_s + " | " + target_s + " | " + speed_s)

    def check_if_in_use(self, data: GripperComponent.EVENTS.gripper_started_moving_data):
        if self != data:
            print("self: {} | data: {}".format(self, data))
            self.interrupt()

    def on_interrupted(self):
        print("interupted toggle")

    def execute(self):
        print("grip execute | current: " + str(RobotMap.gripper_component.pot.get()) + " | target: " + str(self._target_pos))
        if -0.01 < RobotMap.gripper_component.pot.get() - self._target_pos < 0.01:
            RobotMap.gripper_component.set_lift_motor(0)
            self.finished()
            return
        diff = RobotMap.gripper_component.pot.get() - self._target_pos
        if diff == 0:
            self._speed = 0
        else:
            self._speed = (abs(diff) / diff) * 0.50
        RobotMap.gripper_component.set_lift_motor(self._speed)

    def on_end(self):
        RobotMap.gripper_component.remove_listener(GripperComponent.EVENTS.gripper_started_moving, self.check_if_in_use)
        print("toggle end")
