from robot_map import RobotMap
from Command import InstantCommand


def climb() -> InstantCommand:
    return InstantCommand(RobotMap.climb_component.climb())


def stop() -> InstantCommand:
    return InstantCommand(RobotMap.climb_component.stop())
