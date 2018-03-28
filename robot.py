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
    def robotInit(self, loop, events):
        # driver component setup
        # left_front = WPI_TalonSRX(2)
        left_front = Talon(3)
        left_rear = WPI_TalonSRX(1)
        right_front = WPI_TalonSRX(4)
        right_rear = WPI_TalonSRX(3)
        left = SpeedControllerGroup(left_front, left_rear)
        right = SpeedControllerGroup(right_front, right_rear)

        # driver component dependencies
        self.drive_train = DifferentialDrive(left, right)
        # self.left_encoder_motor = left_front
        # self.right_encoder_motor = right_rear
        self.left_encoder_motor = left_rear
        self.right_encoder_motor = right_front
        self.gear_solenoid = DoubleSolenoid(0, 1)
        self.driver_gyro = ADXRS450_Gyro()

        # lifter component dependencies
        self.elevator_motor = WPI_TalonSRX(5)
        self.elevator_bottom_switch = DigitalInput(9)

        # self.carriage_motor = WPI_TalonSRX(6)
        self.carriage_motor = WPI_TalonSRX(2)
        self.carriage_bottom_switch = DigitalInput(1) # was 2
        self.carriage_top_switch = DigitalInput(2) # was 1

        # gripper component dependencies
        self.claw_left_motor = Talon(0)
        self.claw_right_motor = Talon(1)
        self.claw_open_solenoid = DoubleSolenoid(2, 3)
        self.claw_up_limit = DigitalInput(0)
        self.claw_lift_motor = Victor(4)
        self.claw_pot = AnalogPotentiometer(0)

        # climber
        self.climber_motor = Talon(2)

        # controllers
        self.controller = Joystick(0)
        self.operator = Joystick(1)
        self.el_mode = False

        # self.compressor = Compressor(module=0)

    def autonomousInit(self, loop, events):
        # Insert decision tree logic here.

        # Subclass CommandGroup and pass in the event objects
        self.auto_commands = ScaleCommandGroup(events)
        # Load in the first active command.
        self._active_commands.append(self.auto_commands.next())

    def autonomousPeriodic(self):
        # Keep commands which have not finished and remove the rest.
        self._active_commands = list(filter(lambda com: not com.is_done(), self._active_commands))
        # If active_commands list is empty, load the next sequence in the CommandGroup.
        if len(self._active_commands) <= 0:
            try:
                self._active_commands.append(self.auto_commands.next())
                # Schedule the new commands for execution via the event loop.
                for command in self._active_commands:
                    loop.run_until_complete(command.execute)
            # Exception in the case all autonomous commands are done.
            except StopIteration:
                pass

    def teleopInit(self, loop, events):
        
    
    def teleopPeriodic(self):


if __name__ == '__main__':
    print("hello world")
    run(Jessica)
