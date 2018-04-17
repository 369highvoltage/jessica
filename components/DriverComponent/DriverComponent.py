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
from ctre import WPI_TalonSRX, PigeonIMU, FeedbackDevice
from ctre.talonsrx import TalonSRX
from wpilib.drive import DifferentialDrive
from Command import InstantCommand, Command
from wpilib.pidcontroller import PIDController
from wpilib.timer import Timer
from enum import Enum, auto
import math

class RemoteSensorSource(object):
    Off = int(0)
    TalonSRX_SelectedSensor = int(1)
    Pigeon_Yaw = int(2)
    Pigeon_Pitch = int(3)
    Pigeon_Roll = int(4)
    CANifier_Quadrature = int(5)
    CANifier_PWMInput0 = int(6)
    CANifier_PWMInput1 = int(7)
    CANifier_PWMInput2 = int(8)
    CANifier_PWMInput3 = int(9)
    GadgeteerPigeon_Yaw = int(10)
    GadgeteerPigeon_Pitch = int(11)
    GadgeteerPigeon_Roll = int(12)

class GearMode:
    OFF = auto()
    LOW = auto()
    HIGH = auto()


class DriverComponent:
    CONV_FACTOR = 0.0524 * 0.846
    LINEAR_SAMPLE_RATE = 28
    ANGULAR_SAMPLE_RATE = 2
    PID_PRIMARY = 0
    REMOTE_0 = 0
    REMOTE_1 = 1
    PID_TURN = 1
    TimeOut_ms = 0

    def __init__(self):
        # left_front = Victor(3)
        left_front = WPI_TalonSRX(5)
        self.left_encoder_motor = left = left_rear = WPI_TalonSRX(1)
        self.right_encoder_motor = right = right_front = WPI_TalonSRX(4)
        # right_rear = Victor(6)
        self.pigeon_talon = right_rear = WPI_TalonSRX(6)
        self.pigeon = PigeonIMU(self.pigeon_talon)

        # left = SpeedControllerGroup(left_front, left_rear)
        # right = SpeedControllerGroup(right_front, right_rear)

        left_front.follow(left_rear)
        right_rear.follow(right_front)
        self.gear_solenoid = DoubleSolenoid(0, 1)
        # self.driver_gyro = ADXRS450_Gyro()

        self.drive_train = DifferentialDrive(left, right)
        self.drive_train.setDeadband(0.1)

        # setup encoders
        self.left_encoder_motor.setSensorPhase(True)
        self.right_encoder_motor.setSensorPhase(False)

        """
        # setup left encoder
        self.left_encoder_motor.configSelectedFeedbackSensor(
            FeedbackDevice.QuadEncoder,
            DriverComponent.PID_PRIMARY,
            DriverComponent.TimeOut_ms
        )

        # connect left encoder talon to right talon srx
        self.right_encoder_motor.configRemoteFeedbackFilter(
            self.left_encoder_motor.getDeviceID(),
            RemoteSensorSource.TalonSRX_SelectedSensor,
            DriverComponent.REMOTE_0,
            DriverComponent.TimeOut_ms
        )

        # connect piegon talon to right talon srx
        self.right_encoder_motor.configRemoteFeedbackFilter(
            self.pigeon_talon.getDeviceID(),
            RemoteSensorSource.GadgeteerPigeon_Yaw,
            DriverComponent.TimeOut_ms
        )
        """
        self.moving_linear = [0] * DriverComponent.LINEAR_SAMPLE_RATE
        self.moving_angular = [0] * DriverComponent.ANGULAR_SAMPLE_RATE

    def set_curve_raw(self, linear, angular):
        if -0.1 < linear < 0.1:
            self.drive_train.curvatureDrive(linear, angular, True)
        else:
            self.drive_train.curvatureDrive(linear, angular, False)

    def set_curve(self, linear, angular):
        self.moving_linear.append(linear)
        self.moving_angular.append(angular)
        if len(self.moving_linear) > DriverComponent.LINEAR_SAMPLE_RATE:
            self.moving_linear.pop(0)
        if len(self.moving_angular) > DriverComponent.ANGULAR_SAMPLE_RATE:
            self.moving_angular.pop(0)
        l_speed = sum([x / DriverComponent.LINEAR_SAMPLE_RATE for x in self.moving_linear])
        a_speed = sum([x / DriverComponent.ANGULAR_SAMPLE_RATE for x in self.moving_angular])
        # l_speed = math.sin(l_speed * math.pi/2)
        if -0.1 < l_speed < 0.1:
            self.drive_train.curvatureDrive(linear, a_speed, True)
        else:
            self.drive_train.curvatureDrive(linear, a_speed, False)

    def reset_drive_sensors(self):
        # self.driver_gyro.reset()
        self.left_encoder_motor.setSelectedSensorPosition(0, 0, 0)
        self.right_encoder_motor.setSelectedSensorPosition(0, 0, 0)

    @property
    def current_distance(self):
        return DriverComponent.CONV_FACTOR * self.left_encoder_motor.getSelectedSensorPosition(0)

    def current_gear(self):
        if self.gear_solenoid.get() is DoubleSolenoid.Value.kForward:
            return GearMode.HIGH
        if self.gear_solenoid.get() is DoubleSolenoid.Value.kReverse:
            return GearMode.LOW
        if self.gear_solenoid.get() is DoubleSolenoid.Value.kOff:
            return GearMode.OFF

    def toggle_gear(self):
        if self.current_gear() is GearMode.LOW:
            self.set_high_gear()
        if self.current_gear() is GearMode.HIGH:
            self.set_low_gear()

    def set_low_gear(self):
        print("shift low")
        self.gear_solenoid.set(DoubleSolenoid.Value.kReverse)

    def set_high_gear(self):
        print("shift high")
        self.gear_solenoid.set(DoubleSolenoid.Value.kForward)
