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
from Command import InstantCommand, Command
from wpilib.timer import Timer


class DriverComponent:
    CONV_FACTOR = 0.0524

    def __init__(self):
        left_front = Talon(3)
        left_rear = WPI_TalonSRX(1)
        right_front = WPI_TalonSRX(4)
        right_rear = WPI_TalonSRX(3)

        left = SpeedControllerGroup(left_front, left_rear)
        right = SpeedControllerGroup(right_front, right_rear)

        self.left_encoder_motor = left_rear
        self.right_encoder_motor = right_front
        self.gear_solenoid = DoubleSolenoid(0, 1)
        self.driver_gyro = ADXRS450_Gyro()

        self.drive_train = DifferentialDrive(
            left,
            right)

        # setup encoders
        self.left_encoder_motor.setSensorPhase(True)

    def set_curve(self, linear, angular):
        if -0.1 < linear < 0.1:
            self.drive_train.curvatureDrive(linear, angular, True)
        else:
            self.drive_train.curvatureDrive(linear, angular, False)

    def reset_drive_sensors(self):
        self.driver_gyro.reset()
        self.left_encoder_motor.setSelectedSensorPosition(0, 0, 0)
        self.right_encoder_motor.setSelectedSensorPosition(0, 0, 0)

    @property
    def current_distance(self):
        return DriverComponent.CONV_FACTOR * self.left_encoder_motor.getSelectedSensorPosition(0)
