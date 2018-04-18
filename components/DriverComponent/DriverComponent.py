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
    AnalogInput, \
    Ultrasonic
from ctre import WPI_TalonSRX, FeedbackDevice, RemoteSensorSource
from wpilib.drive import DifferentialDrive
from Command import InstantCommand, Command
from wpilib.timer import Timer
from enum import Enum, auto
import math
from Events import Events


class GearMode:
    OFF = auto()
    LOW = auto()
    HIGH = auto()


class DriverComponent(Events):
    CONV_FACTOR = 0.0524 * 0.846
    LINEAR_DECELERATION_THRESHOLD = 0.3
    ANGULAR_DECELERATION_THRESHOLD = 0.6

    PID_PRIMARY = 0
    REMOTE_0 = 0
    REMOTE_1 = 1
    PID_TURN = 1
    TimeOut_ms = 0

    class EVENTS(object):
        driving = "driving"

    def __init__(self):
        Events.__init__(self)
        # left_front = Victor(3)
        left_front = WPI_TalonSRX(6)
        self.left_encoder_motor = left = left_rear = WPI_TalonSRX(1)
        self.right_encoder_motor = right = right_front = WPI_TalonSRX(4)
        # right_rear = Victor(6)
        right_rear = WPI_TalonSRX(7)

        left_front.follow(left_rear)
        right_rear.follow(right_front)
        
        self.gear_solenoid = DoubleSolenoid(0, 1)
        self.driver_gyro = ADXRS450_Gyro()

        self.drive_train = DifferentialDrive(left, right)

        # setup encoders
        self.left_encoder_motor.setSensorPhase(True)
        self.drive_train.setDeadband(0.1)

        self.last_linear_input = 0.0
        self.last_angular_input = 0.0

        self.back_distance_sensor = Ultrasonic(7, 8)
        self.back_distance_sensor.setAutomaticMode(True)
        self.back_distance_sensor.setEnabled(True)

        self._create_event(DriverComponent.EVENTS.driving)

    def setup_talons(self):
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
        # self.right_encoder_motor.configRemoteFeedbackFilter(
        #     self.pigeon_talon.getDeviceID(),
        #     RemoteSensorSource.GadgeteerPigeon_Yaw,
        #     DriverComponent.REMOTE_1,
        #     DriverComponent.TimeOut_ms
        # )
    
    def clamp_deceleration(self, current_input, last_input, threshold):
        # Check for deceleration (current input should be closer to 0.0 than last input)
        if abs(current_input) < abs(last_input):
            last_input -= min(
                threshold,
                max(
                    -threshold,
                    current_input - last_input
                )
            )
        else:
            last_input = current_input
        
        return last_input

    def set_curve_raw(self, linear, angular):
        if -0.1 < linear < 0.1:
            self.drive_train.curvatureDrive(linear, angular, True)
        else:
            self.drive_train.curvatureDrive(linear, angular, False)
        self.trigger_event(DriverComponent.EVENTS.driving)

    def set_curve(self, linear, angular):
        self.last_linear_input = self.clamp_deceleration(linear, self.last_linear_input, DriverComponent.LINEAR_DECELERATION_THRESHOLD)
        self.last_angular_input = self.clamp_deceleration(angular, self.last_angular_input, DriverComponent.ANGULAR_DECELERATION_THRESHOLD)
        self.set_curve_raw(self.last_linear_input, self.last_angular_input)

    def reset_drive_sensors(self):
        self.driver_gyro.reset()
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
