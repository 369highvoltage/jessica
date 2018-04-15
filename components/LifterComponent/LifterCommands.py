from robot_map import RobotMap
from Command import InstantCommand, Command
from components.LifterComponent import LifterComponent


def lock_carriage_move_elevator(speed: float) -> InstantCommand:
    def move():
        RobotMap.lifter_component.set_carriage_speed(-1)
        RobotMap.lifter_component.set_elevator_speed(speed)
    return InstantCommand(move)


def move_lifter(speed: float) -> InstantCommand:
    def move_lifter_sync():
        RobotMap.lifter_component.set_elevator_speed(speed)
        RobotMap.lifter_component.set_carriage_speed(speed)
    return InstantCommand(move_lifter_sync)


class MoveToPosition(Command):
    def __init__(self, position: str):
        super().__init__()
        self._position = position
        self._target_position = LifterComponent.positions[position]

    def on_start(self):
        # start moving towards the target
        RobotMap.lifter_component.lift_to_distance(self._target_position)
        # check if another command is trying to move the lifter
        RobotMap.lifter_component.add_listener(LifterComponent.EVENTS.on_control_move, self.interrupt)
        RobotMap.lifter_component.add_listener(LifterComponent.EVENTS.on_manual_move, self.interrupt)
        print("start move to position command "+ self._position)

    def execute(self):
        if RobotMap.lifter_component.is_at_distance(self._target_position):
            self.finished()

    def on_end(self):
        if not self._interupted:
            RobotMap.lifter_component.stop_lift()
        RobotMap.lifter_component.remove_listener(LifterComponent.EVENTS.on_control_move, self.interrupt)
        RobotMap.lifter_component.remove_listener(LifterComponent.EVENTS.on_manual_move, self.interrupt)
        print("end move to position command")


def move_to_position_instant(position: str) -> InstantCommand:
    return InstantCommand(lambda: RobotMap.lifter_component.lift_to_distance(LifterComponent.positions[position]))


def move_up_instant() -> InstantCommand:
    target_position = LifterComponent.positions[RobotMap.lifter_component.next_position()]
    return InstantCommand(lambda: RobotMap.lifter_component.lift_to_distance(target_position))


def move_down_instant() -> InstantCommand:
    target_position = LifterComponent.positions[RobotMap.lifter_component.prev_position()]
    return InstantCommand(lambda: RobotMap.lifter_component.lift_to_distance(target_position))


class Reset(Command):
    def on_start(self):
        print("start reset command")

    def execute(self):
        speed = -0.25
        RobotMap.lifter_component.set_elevator_speed(speed)
        RobotMap.lifter_component.set_carriage_speed(speed)
        if RobotMap.lifter_component.elevator_bottom_switch.get() \
                and RobotMap.lifter_component.carriage_bottom_switch.get():
            RobotMap.lifter_component.reset_sensors()
            self.finished()

    def on_end(self):
        print("end reset command")


class MoveUp(Command):
    def __init__(self):
        super().__init__()
        self._target_position = None

    def on_start(self):
        self._target_position = LifterComponent.positions[RobotMap.lifter_component.next_position()]

    def execute(self):
        RobotMap.lifter_component.lift_to_distance(self._target_position)
        if RobotMap.lifter_component.is_at_distance(self._target_position):
            self.finished()


class MoveDown(Command):
    def __init__(self):
        super().__init__()
        self._target_position = None

    def on_start(self):
        self._target_position = LifterComponent.positions[RobotMap.lifter_component.prev_position()]

    def execute(self):
        RobotMap.lifter_component.lift_to_distance(self._target_position)
        if RobotMap.lifter_component.is_at_distance(self._target_position):
            self.finished()
