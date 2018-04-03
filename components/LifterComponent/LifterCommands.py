from robot_map import RobotMap
from Command import InstantCommand, Command
from components.LifterComponent import LifterComponent


def move_lifter(speed: float) -> InstantCommand:
    def move_lifter_sync():
        RobotMap.lifter_component.set_elevator_speed(speed)
        RobotMap.lifter_component.set_carriage_speed(speed)
    return InstantCommand(move_lifter_sync)


class MoveToPosition(Command):
    def __init__(self, position: str):
        super().__init__()
        self._target_position = LifterComponent.positions[position]

    def on_start(self):
        pass

    def execute(self):
        RobotMap.lifter_component.lift_to_distance(self._target_position)
        if RobotMap.lifter_component.is_at_distance(self._target_position):
            self.finished()

    def on_end(self):
        pass


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
