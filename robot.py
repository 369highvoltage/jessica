import magicbot
from wpilib import \
    SpeedControllerGroup, \
    DoubleSolenoid, \
    ADXRS450_Gyro, \
    Joystick, \
    run, \
    DigitalInput, \
    AnalogPotentiometer
from ctre import WPI_TalonSRX
from wpilib.drive import DifferentialDrive
from components.driver import Driver, GearMode
from components.lifter import Lifter
from utilities import truncate_float, normalize_range



class Jessica(magicbot.MagicRobot):
    driver: Driver
    lifter: Lifter

    # Create motors and stuff here
    def createObjects(self):
        # driver component setup
        left_front = WPI_TalonSRX(4)
        left_rear = WPI_TalonSRX(3)
        right_front = WPI_TalonSRX(2)
        right_rear = WPI_TalonSRX(1)
        left = SpeedControllerGroup(left_front, left_rear)
        right = SpeedControllerGroup(right_front, right_rear)

        # driver component dependencies
        self.drive_train = DifferentialDrive(left, right)
        self.left_encoder_motor = left_front
        self.right_encoder_motor = right_rear
        self.gear_solenoid = DoubleSolenoid(0, 1)
        self.driver_gyro = ADXRS450_Gyro()

        # lifter component dependencies
        self.elevator_motor = WPI_TalonSRX(5)
        self.elevator_bottom_switch = DigitalInput(0)

        self.lifter_motor = WPI_TalonSRX(6)
        self.lifter_bottom_switch = DigitalInput(1)
        self.lifter_pot = AnalogPotentiometer(0)

        # controllers
        self.controller = Joystick(0)
        self.el_mode = False
    
    # Init: Called when mode starts; optional 
    # Periodic: Called on each iteration of the control loop
    def autonomousInit(self):
        self.driver.set_gear(GearMode.LOW)
    
    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.driver.set_gear(GearMode.LOW)
        self.x_down = False
    
    def teleopPeriodic(self):
        if self.controller.getRawButtonPressed(1):
            self.driver.set_gear(GearMode.LOW)
        if self.controller.getRawButtonPressed(3):
            self.driver.set_gear(GearMode.HIGH)

        left_y = truncate_float(-self.controller.getRawAxis(1))
        right_x = truncate_float(self.controller.getRawAxis(2))
        right_y = truncate_float(-self.controller.getRawAxis(5))

        self.driver.set_curve(left_y, right_x)
        # self.driver.set_tank(left_y, right_y)

        # elevator controls
        l2 = normalize_range(self.controller.getRawAxis(3), -1, 1, 0, 1)
        r2 = normalize_range(self.controller.getRawAxis(4), -1, 1, 0, 1)
        b_speed = -l2 + r2

        if self.el_mode:
            self.lifter.move_elevator(b_speed)
            self.lifter.move_carriage(0)
        else:
            self.lifter.move_carriage(b_speed)
            self.lifter.move_elevator(0)

        if self.controller.getRawButtonPressed(2):
            self.x_down = True

        if self.controller.getRawButtonReleased(2) and self.x_down:
            self.el_mode = not self.el_mode
            self.x_down = False



if __name__ == '__main__':
    print("hello world")
    run(Jessica)
