from CommandGroup import CommandGroup
from components.DriverComponent.DriveCommands import DriveByDistance, Turn
from components.LifterComponent.LifterCommands import MoveToPosition, Reset
from components.GripperComponent.GripperCommands import SpitFast


def switch_scale(scale_location: str, switch_location: str, start_location: str) -> CommandGroup:
    angle = 0
    auto = CommandGroup()

    auto.add_sequential(Reset())

    if start_location == "L":
        angle = 90
    if start_location == "R":
        angle = -90

    if start_location == scale_location:
        # go to scale
        auto.add_parallel([
            MoveToPosition("floor"),
            DriveByDistance(324, 0.75)
        ])
        auto.add_sequential(Turn(angle, 0.25))
        auto.add_sequential(DriveByDistance(-30, -0.25))
        auto.add_sequential(MoveToPosition("scale_high"))
        auto.add_sequential(SpitFast())
        auto.add_sequential(MoveToPosition("floor"))
    elif start_location == switch_location:
        # go to switch
        auto.add_parallel([
            MoveToPosition("floor"),
            DriveByDistance(152, 0.5)
        ])
        auto.add_sequential(Turn(angle, 0.25))
        auto.add_sequential(MoveToPosition("portal"))
        auto.add_sequential(DriveByDistance(12, 0.25))
        auto.add_sequential(SpitFast(speed=0.5))
    elif start_location == "L" or start_location == "R":
        auto.add_sequential(DriveByDistance(168, 0.25))
    elif start_location == "M":
        # switch from middle
        if switch_location == "L":
            angle = -90
        if switch_location == "R":
            angle = 90
        auto.add_sequential(DriveByDistance(24, 0.5))
        auto.add_sequential(Turn(angle / 2, 0.25))
        auto.add_sequential(DriveByDistance(48, 0.5))
        auto.add_sequential(Turn(-(angle / 2), 0.25))
        auto.add_sequential(MoveToPosition("portal"))
        auto.add_sequential(DriveByDistance(24, 0.5))
        auto.add_sequential(SpitFast(speed=0.5))
        auto.add_sequential(DriveByDistance(-24, -0.5))
        auto.add_sequential(MoveToPosition("floor"))


    return auto
