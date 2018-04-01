from wpilib import \
    SpeedControllerGroup, \
    DoubleSolenoid, \
    ADXRS450_Gyro, \
    Joystick, \
    run, \
    DigitalInput, \
    AnalogPotentiometer, \
    Talon, \
    SmartDashboard, \
    Victor, \
    Compressor, \
    AnalogInput
from ctre import WPI_TalonSRX
from wpilib.drive import DifferentialDrive
from components.driver import Driver, GearMode
from components.lifter import Lifter, MovementDir
from utilities import truncate_float, normalize_range
from components.gripper import Gripper, GripState, GripLiftState
from AsyncRobot import AsyncRobot
from CommandGroup import CommandGroup
from Command import Command, InstantCommand


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
    driver: Driver
    lifter: Lifter
    gripper: Gripper

    def __init__(self):
        super().__init__()
    # Create motors and stuff here
    def robotInit(self):
        pass

    def autonomousInit(self):
        # Insert decision tree logic here.

        # run command
        self.run_command(ScaleCommandGroup())
        # or
        self.run_command(scale_command_group())

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        pass
    
    def teleopPeriodic(self):
        pass

if __name__ == '__main__':
    print("hello world")
    run(Jessica)
