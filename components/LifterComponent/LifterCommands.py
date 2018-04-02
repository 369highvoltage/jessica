from robot_map import RobotMap
from Command import InstantCommand, Command
from components.LifterComponent import LifterComponent


def move_lifter(speed: float) -> InstantCommand:
    def move_lifter_sync():
        RobotMap.lifter_component.set_elevator_speed(speed)
        RobotMap.lifter_component.set_carriage_speed(speed)
    return InstantCommand(move_lifter_sync)


class MoveToPosition(Command):
    positions = {
        "floor": 2.0,
        "portal": 34.0,
        "scale_low": 48.0,
        "scale_mid": 60.0,
        "scale_high": 72.0,
        "max_height": 84.0
    }

    def __init__(self, position: str):
        super().__init__()
        self._target_position = position
        self._target_distance = None
        self._carriage = None
        self._elevator = None

    def on_start(self):
        self._target_distance = MoveToPosition.positions[self._target_position]

        # Carriage cannot go farther than 30 inches. Restrict carriage travel.
        carriage = min(self._target_distance * LifterComponent.CARRIAGE_MULTIPLIER, LifterComponent.CARRIAGE_MAX_HEIGHT)
        # Elevator moves the remainder of distance.
        elevator = self._target_distance - carriage

        self._carriage = carriage / LifterComponent.CARRIAGE_CONV_FACTOR
        self._elevator = elevator / LifterComponent.ELEVATOR_CONV_FACTOR

    def execute(self):
        RobotMap.lifter_component.elevator_to_target_position(self._carriage)
        RobotMap.lifter_component.carriage_to_target_position(self._elevator)
        if RobotMap.lifter_component.is_at_position(self._target_distance):
            self.finished()

    def on_end(self):
        pass
