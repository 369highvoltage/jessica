from wpilib.drive import DifferentialDrive
from wpilib import DoubleSolenoid, ADXRS450_Gyro, SmartDashboard, PIDController
from wpilib.interfaces import PIDOutput
from networktables import NetworkTables
from ctre import WPI_TalonSRX
from enum import Enum, auto
from magicbot import tunable


class GearMode(Enum):
    LOW = auto()
    HIGH = auto()


class DriveModes(Enum):
    TANK = auto()
    CURVE = auto()
    AUTO_POSITION = auto()


class Driver:
    # dependencies
    left_encoder_motor: WPI_TalonSRX
    right_encoder_motor: WPI_TalonSRX
    drive_train: DifferentialDrive
    gear_solenoid: DoubleSolenoid
    driver_gyro: ADXRS450_Gyro

    # constants
    LOW_GEAR_RATIO = 0.01543
    HIGH_GEAR_RATIO = 0.03516
    MAX_SPEED = 1
    MIN_SPEED = -1
    dist_kP = tunable(0.04, doc="driver distance P pid value")
    dist_kI = tunable(0.0, doc="driver distance I pid value")
    dist_kD = tunable(0.0, doc="driver distance D pid value")
    dist_kF = tunable(0.0, doc="driver distance F pid value")

    distance_reached_cbs: list

    def __init__(self):
        self.enabled = False
        self.left_val = 0.0
        self.right_val = 0.0
        self.drive_mode = None
        self.gear_mode = None
        self.target_distance_inches = None
        self.distance_reached_cbs = []

    def setup(self):
        self.distance_pid_out = DistancePIOutput()
        self.distance_pid = PIDController(
            Kp=self.dist_kP,
            Ki=self.dist_kI,
            Kd=self.dist_kD,
            Kf=self.dist_kF,
            source=lambda : self.current_distance,
            output=self.distance_pid_out,
        )
        self.distance_pid.setInputRange(-648.0, 648.0)
        self.distance_pid.setOutputRange(Driver.MIN_SPEED, Driver.MAX_SPEED)
        self.distance_pid.setContinuous()

    def set_gear(self, gear: GearMode):
        if gear is GearMode.HIGH:
            self.gear_solenoid.set(DoubleSolenoid.Value.kForward)
            self.gear_mode = GearMode.HIGH
        if gear is GearMode.LOW:
            self.gear_solenoid.set(DoubleSolenoid.Value.kReverse)
            self.gear_mode = GearMode.LOW

    def toggle_gear(self):
        if self.gear_mode is GearMode.HIGH:
            self.set_gear(GearMode.LOW)
        if self.gear_mode is GearMode.LOW:
            self.set_gear(GearMode.HIGH)

    """
    sensors
    """
    # gyro
    def reset_gyro(self):
        self.driver_gyro.reset()

    @property
    def current_angle(self):
        return self.driver_gyro.getAngle()

    # encoder
    def reset_drive_sensors(self):
        self.left_encoder_motor.setQuadraturePosition(0)
        self.right_encoder_motor.setQuadraturePosition(0)

    @property
    def current_distance(self):
        average_position = (self.left_encoder_motor.getQuadraturePosition() + self.right_encoder_motor.getQuadraturePosition()) / 2
        actual_position = 0
        if self.gear_mode is GearMode.LOW and average_position != 0:
            actual_position = Driver.LOW_GEAR_RATIO / average_position
        if self.gear_mode is GearMode.HIGH and average_position != 0:
            actual_position = Driver.HIGH_GEAR_RATIO / average_position
        return actual_position

    # calculations based on velocity
    @property
    def linear_displacement(self):
        return (self.right_encoder_motor.getSelectedSensorVelocity(0) + self.left_encoder_motor.getSelectedSensorVelocity(0)) / 2

    @property
    def angular_displacement(self):
        return self.right_encoder_motor.getSelectedSensorVelocity(0) - self.left_encoder_motor.getSelectedSensorVelocity(0)

    # set drive speeds
    def set_tank(self, left_speed: float, right_speed: float):
        self.drive_mode= DriveModes.TANK
        self.left_val = left_speed
        self.right_val = right_speed

    def set_curve(self, linear: float, angular: float):
        self.drive_mode = DriveModes.CURVE
        self.left_val = linear
        self.right_val = angular

    def drive_to_position(self, inches: float, cb):
        self.target_distance_inches = inches
        if cb:
            self.distance_reached_cbs += cb

    def is_at_target_distance(self):
        if not self.distance_pid.isEnabled():
            return False
        return self.distance_pid.onTarget()

    def _drive_to_target(self):
        if not self.distance_pid.isEnabled():
            self.reset_drive_sensors()
            self.distance_pid.setSetpoint(self.target_distance_inches)
            self.distance_pid.enable()
        else:
            self.set_curve(self.distance_pid_out.output, 0.0)
            if self.distance_pid.onTarget():
                self.distance_pid.disable()
                self.set_curve(0.0, 0.0)
                self.target_distance_inches = None
                for cb in self.distance_reached_cbs:
                    cb()

    """
    runtime functions
    """
    def on_enable(self):
        self.enabled = True
        # self.reset_drive_sensors()
        # self.reset_gyro()

    def execute(self):
        if self.target_distance_inches:
            self._drive_to_target()

        if self.drive_mode is DriveModes.TANK:
            self.drive_train.tankDrive(self.left_val, self.right_val)
        if self.drive_mode is DriveModes.CURVE:
            # if -0.1 < self.left_val < 0.1:
            #     self.drive_train.curvatureDrive(self.left_val, self.right_val, True)
            # else:
            self.drive_train.curvatureDrive(self.left_val, self.right_val, False)



        # debug values
        SmartDashboard.putBoolean('driver/DriveMode', self.drive_mode)
        if self.gear_mode is GearMode.HIGH:
            SmartDashboard.putBoolean('driver/GearMode', 'HIGH')
        if self.gear_mode is GearMode.LOW:
            SmartDashboard.putBoolean('driver/GearMode', 'LOW')

        left_label = None
        right_label = None
        if self.drive_mode is DriveModes.TANK:
            left_label = 'driver/left_speed'
            right_label = 'driver/right_speed'
        if self.drive_mode is DriveModes.CURVE:
            left_label = 'driver/linear'
            right_label = 'driver/angular'
        SmartDashboard.putNumber(left_label, self.left_val)
        SmartDashboard.putNumber(right_label, self.right_val)
        SmartDashboard.putNumber('driver/linear_displacement', self.linear_displacement)
        SmartDashboard.putNumber('driver/angular_displacement', self.angular_displacement)
        SmartDashboard.putNumber('driver/current_distance', self.current_distance)
        SmartDashboard.putNumber('driver/current_angle', self.current_angle)
        if self.target_distance_inches:
            SmartDashboard.putNumber('driver/target_distance_inches', self.target_distance_inches)
        else:
            SmartDashboard.putNumber('driver/target_distance_inches', 0.0)
        NetworkTables.flush()


class DistancePIOutput(PIDOutput):

    def pidWrite(self, output):
        self.output = output