import magicbot
from wpilib import SpeedControllerGroup, DoubleSolenoid, ADXRS450_Gyro, Joystick, run
from ctre import WPI_TalonSRX
from wpilib.drive import DifferentialDrive
from components.driver import Driver, GearMode

def truncate_float(num: float):
    return float('%.1f'%(num))


class Jessica(magicbot.MagicRobot):
    driver: Driver

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

        # controllers
        self.controller = Joystick(0)
    
    # Init: Called when mode starts; optional 
    # Periodic: Called on each iteration of the control loop
    def autonomousInit(self):
        self.driver.set_gear(GearMode.LOW)
    
    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.driver.set_gear(GearMode.LOW)
    
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
if __name__ == '__main__':
    print("hello world")
    run(Jessica)
