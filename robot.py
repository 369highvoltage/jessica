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

class Jessica(asyncRobot):
    driver: Driver
    lifter: Lifter
    gripper: Gripper

    def __init__(self):
        super().__init__()
        self._active_commands = []

    # Create motors and stuff here
    def robotInit(self, loop, event):
        pass

    def autonomousInit(self, loop, event):
        # Insert decision tree logic here.


        # Subclass CommandGroup and pass in the event objects
        self.auto_commands = ScaleCommandGroup(event)

        # Load in the first active command.
        self._active_commands.extend(self.auto_commands.next())

    def autonomousPeriodic(self):
        # Keep commands which have not finished and remove the rest.
        self._active_commands = list(filter(lambda com: not com.is_done(), self._active_commands))

        # If active_commands list is empty, load the next sequence in the CommandGroup.
        if len(self._active_commands) <= 0:
            try:
                self._active_commands.append(self.auto_commands.next())
            
            # Exception in the case all autonomous commands are done.
            except StopIteration:
                return
        
        # Schedule commands for execution via the event loop.
        for command in self._active_commands:
            loop.call_soon(command.execute)

    def teleopInit(self, loop, event):
        pass
    
    def teleopPeriodic(self):
        pass

if __name__ == '__main__':
    print("hello world")
    run(Jessica)
