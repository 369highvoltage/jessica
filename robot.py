from wpilib import run, Joystick
from components.driver import Driver, GearMode
from components.lifter import Lifter, MovementDir
from utilities import truncate_float, normalize_range
from components.gripper import Gripper, GripState, GripLiftState
from AsyncRobot import AsyncRobot
from CommandGroup import CommandGroup
from Command import Command, InstantCommand
import robot_map
from components.DriverComponent import DriverComponent
from components.DriverComponent.DriveCommands import DriveByTime, DriveByDistance, Turn, curve_drive
from components.LifterComponent.LifterCommands import move_lifter
from components.GripperComponent.GripperCommands import move_left_right, toggle_spread


# example
class ScaleCommandGroup(CommandGroup):
    def on_start(self):
        # Insert decision tree logic here.

        # create sequence
        self.add_sequential(InstantCommand(lambda: print("drive forward 220in")))
        self.add_sequential(InstantCommand(lambda: print("turn 90 degrees")))
        self.add_parallel([
            InstantCommand(lambda: print("drive back 12in")),
            InstantCommand(lambda: print("raise lifter to max_height"))
        ])
        self.add_sequential(InstantCommand(lambda: print("shoot")))


# or
def scale_command_group() -> CommandGroup:
    # Insert decision tree logic here.

    # create sequence
    sequence = CommandGroup()
    sequence.add_sequential(InstantCommand(lambda: print("drive forward 220in")))
    sequence.add_sequential(InstantCommand(lambda: print("turn 90 degrees")))
    sequence.add_parallel([
        InstantCommand(lambda: print("drive back 12in")),
        InstantCommand(lambda: print("raise lifter to max_height"))
    ])
    sequence.add_sequential(InstantCommand(lambda: print("shoot")))
    return sequence


class Jessica(AsyncRobot):

    def __init__(self):
        super().__init__()

    # Create motors and stuff here
    def robotInit(self):
        self.joystick = Joystick(1)

    def autonomousInit(self):
        # Insert decision tree logic here.

        # run command
        # self.run_command(ScaleCommandGroup())
        # or
        # self.run_command(scale_command_group())
        sequence = CommandGroup()
        sequence.add_sequential(DriveByDistance(324, 0.25))
        sequence.add_sequential(Turn(90, 0.5))
        sequence.add_sequential(DriveByDistance(-36, -0.25))
        sequence.add_sequential(DriveByDistance(48, 0.25))
        self.run_command(sequence)

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        pass
    
    def teleopPeriodic(self):
        # if self.joystick.getRawButtonPressed(1):
        left_y = -self.joystick.getRawAxis(1)
        right_x = self.joystick.getRawAxis(2)
        self.run_command(curve_drive(left_y, right_x))

        l2 = -normalize_range(self.joystick.getRawAxis(3), -1, 1, 0, 1)
        r2 = normalize_range(self.joystick.getRawAxis(4), -1, 1, 0, 1)
        speed = r2 + l2
        self.run_command(move_lifter(speed))

        l1 = 5
        r1 = 6
        g_speed = 0.0
        if self.joystick.getRawButton(l1):
            g_speed += 1.0
        if self.joystick.getRawButton(r1):
            g_speed -= 1.0

        self.run_command(move_left_right(g_speed))

        triangle = 4
        if self.joystick.getRawButtonPressed(triangle):
            self.run_command(toggle_spread())


if __name__ == '__main__':
    print("hello world")
    run(Jessica)
