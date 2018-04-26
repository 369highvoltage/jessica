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
    Ultrasonic, \
    PIDController
from ctre import WPI_TalonSRX, FeedbackDevice, RemoteSensorSource, PigeonIMU, ParamEnum, ControlMode, NeutralMode
from wpilib.drive import DifferentialDrive
from Command import InstantCommand, Command
from wpilib.timer import Timer
from enum import Enum, auto
import math
from Events import Events
from pid_helpers import Gains, PIDOutput, PIDSource

class FollowerType(object):
    PercentOutput = int(0)
    AuxOutput1 = int(1)

class DemandType(object):
    Neutral = int(0)
    AuxPID = int(1)
    ArbitraryFeedForward = int(2)

class StatusFrame(object):
    Status_1_General = 0x1400
    Status_2_Feedback0 = 0x1440
    Status_4_AinTempVbat = 0x14C0
    Status_6_Misc = 0x1540
    Status_7_CommStatus = 0x1580
    Status_9_MotProfBuffer = 0x1600

    Status_10_MotionMagic = 0x1640

    Status_10_Targets = 0x1640
    Status_12_Feedback1 = 0x16C0
    Status_13_Base_PIDF0 = 0x1700
    Status_14_Turn_PIDF1 = 0x1740
    Status_15_FirmwareApiStatus = 0x1780

class SensorTerm(object):
    Sum0 = int(0)
    Sum1 = int(1)
    Diff0 = int(2)
    Diff1 = int(3)


class GearMode:
    OFF = auto()
    LOW = auto()
    HIGH = auto()


class DriverComponent(Events):
    # CONV_FACTOR = 0.0524
    CONV_FACTOR = 0.0524 * 0.846
    LINEAR_DECELERATION_THRESHOLD = 0.05
    ANGULAR_DECELERATION_THRESHOLD = 0.3

    PID_PRIMARY = 0
    REMOTE_0 = 0
    REMOTE_1 = 1
    PID_TURN = 1
    TimeOut_ms = 0
    pigeonUnitsPerRotation = 8192
    turnTravelUnitsPerRotation = 3600
    sensor_units_per_rotation = 1440
    rotations_to_travel = 6

    nuetral_deadband = 0.1

    slot_0 = 0
    slot_1 = 1
    slot_2 = 2
    slot_3 = 3

    slot_distance =  slot_0
    slot_turning = slot_1
    slot_velocity = slot_2
    slot_motprof = slot_3
    
    gains_distance = Gains(p=0.1, i=0.0, d=0.0, f=0.0, intergral_zone=100, peak_out=0.50)
    gains_turning = Gains(p=0.02, i=0.0001, d=0.02, f=0.0)
    gains_velocity = Gains(p=0.0, i=0.0, d=0.0, f=0.0, intergral_zone=300, peak_out=0.50)
    gains_motprof = Gains(p=0.0, i=0.0, d=0.0, f=0.0, intergral_zone=400, peak_out=1.0)

    class EVENTS(object):
        driving = "driving"
        right_encoder_motor: WPI_TalonSRX
        left_encoder_motor: WPI_TalonSRX
        pigeon_talon: WPI_TalonSRX
        pigeon: PigeonIMU

    def __init__(self):
        Events.__init__(self)
        # left_front = Victor(3)
        self.pigeon_talon = left_front = WPI_TalonSRX(6)
        self.left_encoder_motor = left = left_rear = WPI_TalonSRX(1)
        self.right_encoder_motor = right = right_front = WPI_TalonSRX(4)
        # self.left_encoder_motor = left_rear = WPI_TalonSRX(1)
        # self.right_encoder_motor = right_front = WPI_TalonSRX(4)
        # right_rear = Victor(6)
        right_rear = WPI_TalonSRX(7)
        self.pigeon = PigeonIMU(self.pigeon_talon)

        # left = SpeedControllerGroup(left_rear, left_front)
        # right = SpeedControllerGroup(right_rear, right_front)
        # left_front.follow(left_rear)
        # right_rear.follow(right_front)
        
        self.gear_solenoid = DoubleSolenoid(0, 1)
        self.driver_gyro = ADXRS450_Gyro()

        self.drive_train = DifferentialDrive(left, right)

        # setup encoders
        self.left_encoder_motor.setSensorPhase(False)
        self.drive_train.setDeadband(0.1)

        self.last_linear_input = 0.0
        self.last_angular_input = 0.0

        self.back_distance_sensor = Ultrasonic(7, 8)
        self.back_distance_sensor.setAutomaticMode(True)
        self.back_distance_sensor.setEnabled(True)

        self.front_distance_sensor = Ultrasonic(5, 6)
        self.front_distance_sensor.setAutomaticMode(True)
        self.front_distance_sensor.setEnabled(True)

        self._create_event(DriverComponent.EVENTS.driving)
        
        self._angular_pid = 0.0

        def set_angular(output):
            self._angular_pid = output

        def set_distance(output):
            self._linear_pid = output

        self._angular_controller = PIDController(
            DriverComponent.gains_turning.p,
            DriverComponent.gains_turning.i,
            DriverComponent.gains_turning.d,
            self.driver_gyro,
            output=PIDOutput(set_angular)
        )
        self._angular_controller.setInputRange(-360, 360)
        self._angular_controller.setOutputRange(-1, 1)
        self._angular_controller.setAbsoluteTolerance(0.5)

        self._linear_pid = 0.0

        self._distance_controller = PIDController(
            DriverComponent.gains_turning.p,
            DriverComponent.gains_turning.i,
            DriverComponent.gains_turning.d,
            PIDSource(lambda: self.current_distance),
            output=PIDOutput(set_distance)
        )
        self._distance_controller.setOutputRange(-1, 1)
        self._distance_controller.setAbsoluteTolerance(0.5)

    def setup_talons(self):
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
            DriverComponent.REMOTE_1,
            DriverComponent.TimeOut_ms
        )

        # setup sum and difference signals
        self.right_encoder_motor.configSensorTerm(SensorTerm.Sum0, FeedbackDevice.RemoteSensor0, DriverComponent.TimeOut_ms)
        self.right_encoder_motor.configSensorTerm(SensorTerm.Sum1, FeedbackDevice.QuadEncoder, DriverComponent.TimeOut_ms)
        self.right_encoder_motor.configSensorTerm(SensorTerm.Diff1, FeedbackDevice.RemoteSensor0, DriverComponent.TimeOut_ms)
        self.right_encoder_motor.configSensorTerm(SensorTerm.Diff0, FeedbackDevice.QuadEncoder, DriverComponent.TimeOut_ms)

        # select sum for distance(0), different for turn(1)
        self.right_encoder_motor.configSelectedFeedbackSensor(FeedbackDevice.SensorSum, DriverComponent.PID_PRIMARY, DriverComponent.TimeOut_ms)

        # config heading with pigeon
        self.right_encoder_motor.configSelectedFeedbackCoefficient(
            1.0,
            DriverComponent.PID_PRIMARY,
            DriverComponent.TimeOut_ms
        )
        self.right_encoder_motor.configSelectedFeedbackSensor(
            FeedbackDevice.RemoteSensor1,
            DriverComponent.PID_TURN,
            DriverComponent.TimeOut_ms
        )
        self.right_encoder_motor.configSelectedFeedbackCoefficient(
            DriverComponent.turnTravelUnitsPerRotation / DriverComponent.pigeonUnitsPerRotation,
            DriverComponent.PID_TURN,
            DriverComponent.TimeOut_ms
        )

        # telemetry
        self.right_encoder_motor.setStatusFramePeriod(
            StatusFrame.Status_12_Feedback1,
            20,
            DriverComponent.TimeOut_ms
        )
        # talonRght.setStatusFramePeriod(StatusFrame.Status_12_Feedback1, 20, Constants.kTimeoutMs);
        self.right_encoder_motor.setStatusFramePeriod(
            StatusFrame.Status_13_Base_PIDF0,
            20,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.setStatusFramePeriod(StatusFrame.Status_13_Base_PIDF0, 20, Constants.kTimeoutMs);
        self.right_encoder_motor.setStatusFramePeriod(
            StatusFrame.Status_14_Turn_PIDF1,
            20,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.setStatusFramePeriod(StatusFrame.Status_14_Turn_PIDF1, 20, Constants.kTimeoutMs);
        self.right_encoder_motor.setStatusFramePeriod(
            StatusFrame.Status_14_Turn_PIDF1,
            20,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.setStatusFramePeriod(StatusFrame.Status_10_Targets, 20, Constants.kTimeoutMs);
        self.right_encoder_motor.setStatusFramePeriod(
            StatusFrame.Status_10_Targets,
            20,
            DriverComponent.TimeOut_ms
        )
        # /* speed up the left since we are polling it's sensor */
        # _talonLeft.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 5, Constants.kTimeoutMs);
        self.left_encoder_motor.setStatusFramePeriod(
            StatusFrame.Status_2_Feedback0,
            5,
            DriverComponent.TimeOut_ms
        )

        # _talonLeft.configNeutralDeadband(Constants.kNeutralDeadband, Constants.kTimeoutMs);
        self.left_encoder_motor.configNeutralDeadband(
            DriverComponent.nuetral_deadband,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.configNeutralDeadband(Constants.kNeutralDeadband, Constants.kTimeoutMs);
        self.right_encoder_motor.configNeutralDeadband(
            DriverComponent.nuetral_deadband,
            DriverComponent.TimeOut_ms
        )

        # _talonRght.configMotionAcceleration(1000, Constants.kTimeoutMs);
        # self.right_encoder_motor.configMotionAcceleration(1000, DriverComponent.TimeOut_ms)
        # _talonRght.configMotionCruiseVelocity(1000, Constants.kTimeoutMs);
        # self.right_encoder_motor.configMotionCruiseVelocity(1000, DriverComponent.TimeOut_ms)

        # /* max out the peak output (for all modes).  However you can
        #     * limit the output of a given PID object with configClosedLoopPeakOutput().
        #     */
        # _talonLeft.configPeakOutputForward(+1.0, Constants.kTimeoutMs);
        self.left_encoder_motor.configPeakOutputForward(1.0, DriverComponent.TimeOut_ms)
        # _talonLeft.configPeakOutputReverse(-1.0, Constants.kTimeoutMs);
        self.left_encoder_motor.configPeakOutputReverse(-1.0, DriverComponent.TimeOut_ms)
        # _talonRght.configPeakOutputForward(+1.0, Constants.kTimeoutMs);
        self.right_encoder_motor.configPeakOutputForward(1.0, DriverComponent.TimeOut_ms)
        # _talonRght.configPeakOutputReverse(-1.0, Constants.kTimeoutMs);
        self.right_encoder_motor.configPeakOutputReverse(-1.0, DriverComponent.TimeOut_ms)

        self.left_encoder_motor.configAllowableClosedloopError(DriverComponent.slot_distance, int(2 / DriverComponent.CONV_FACTOR), DriverComponent.TimeOut_ms)
        self.right_encoder_motor.configAllowableClosedloopError(DriverComponent.slot_distance, int(2 / DriverComponent.CONV_FACTOR), DriverComponent.TimeOut_ms)

        # distance servo
        self.config_talon_pid(
            self.right_encoder_motor,
            DriverComponent.slot_distance,
            DriverComponent.gains_distance
        )

        # turn servo
        self.config_talon_pid(
            self.right_encoder_motor,
            DriverComponent.slot_turning,
            DriverComponent.gains_turning
        )

        # magic servo
        self.config_talon_pid(
            self.right_encoder_motor,
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof
        )

        # velocity servo
        self.config_talon_pid(
            self.right_encoder_motor,
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity
        )
        """

        self.left_encoder_motor.setNeutralMode(NeutralMode.Brake)
        self.right_encoder_motor.setNeutralMode(NeutralMode.Brake)
        
        """
        # /* 1ms per loop.  PID loop can be slowed down if need be.
        #     * For example,
        #     * - if sensor updates are too slow
        #     * - sensor deltas are very small per update, so derivative error never gets large enough to be useful.
        #     * - sensor movement is very slow causing the derivative error to be near zero.
        #     */
        # int closedLoopTimeMs = 1;
        clost_loop_time_ms = 1
        # _talonRght.configSetParameter(ParamEnum.ePIDLoopPeriod, closedLoopTimeMs, 0x00, Constants.PID_PRIMARY, Constants.kTimeoutMs);
        self.right_encoder_motor.configSetParameter(
            ParamEnum.ePIDLoopPeriod,
            clost_loop_time_ms,
            0x00,
            DriverComponent.PID_PRIMARY,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.configSetParameter(ParamEnum.ePIDLoopPeriod, closedLoopTimeMs, 0x00, Constants.PID_TURN, Constants.kTimeoutMs);
        self.right_encoder_motor.configSetParameter(
            ParamEnum.ePIDLoopPeriod,
            clost_loop_time_ms,
            0x00,
            DriverComponent.PID_TURN,
            DriverComponent.TimeOut_ms
        )

        # /**
        #     * false means talon's local output is PID0 + PID1, and other side Talon is PID0 - PID1
        #     * true means talon's local output is PID0 - PID1, and other side Talon is PID0 + PID1
        #     */
        # _talonRght.configAuxPIDPolarity(false, Constants.kTimeoutMs);
        self.right_encoder_motor.configAuxPIDPolarity(False, DriverComponent.TimeOut_ms)
        self.reset_drive_sensors()
        """
        
    
    def config_talon_pid(self, motor: WPI_TalonSRX, slot: int, gains: Gains):
        motor.config_kP(slot, gains.p, DriverComponent.TimeOut_ms)
        
        motor.config_kI(slot, gains.i, DriverComponent.TimeOut_ms)
        
        motor.config_kD(slot, gains.d, DriverComponent.TimeOut_ms)
        
        motor.config_kF(slot, gains.f, DriverComponent.TimeOut_ms)
        
        # motor.config_IntegralZone(slot, gains.intergral_zone, DriverComponent.TimeOut_ms)

        # motor.configClosedLoopPeakOutput(slot, gains.peak_out, DriverComponent.TimeOut_ms)
    
    def neutralMotors(self):
        self.left_encoder_motor.neutralOutput()
        self.right_encoder_motor.neutralOutput()
    
    def clamp_deceleration(self, current_input, last_input, threshold):
        # Clamp huge swings in velocity.
        if abs(current_input - last_input) > threshold:
            last_input -= min(threshold, max(-threshold, last_input - current_input))
        # General clamp for any other acceleration.
        else:
            last_input = current_input
        
        return last_input

    def set_curve_raw(self, linear, angular):
        if -0.1 < linear < 0.1:
            self.drive_train.curvatureDrive(linear, angular, True)
        else:
            self.drive_train.curvatureDrive(linear, angular, False)
    """
    def set_percent_output(self, linear: float, angular: float):
        self.left_encoder_motor.set(ControlMode.PercentOutput, linear, DemandType.ArbitraryFeedForward, angular)
        self.right_encoder_motor.set(ControlMode.PercentOutput, linear, DemandType.ArbitraryFeedForward, -angular)
    
    def set_velocity_mode(self):
        self.neutralMotors()
        self.reset_drive_sensors()

        self.right_encoder_motor.selectProfileSlot(DriverComponent.slot_velocity, DriverComponent.PID_PRIMARY)
        self.right_encoder_motor.selectProfileSlot(DriverComponent.slot_turning, DriverComponent.PID_TURN)

    def set_velocity(self, linear: float, angular: float):
        target_rpm = linear * 500
        target_units_per_100ms = target_rpm * DriverComponent.sensor_units_per_rotation / 600.0

        heading_units = DriverComponent.turnTravelUnitsPerRotation * -angular

        # set velocity mode

        self.right_encoder_motor.set(ControlMode.Velocity, target_units_per_100ms, DemandType.AuxPID, heading_units)
        self.left_encoder_motor.follow(self.right_encoder_motor, FollowerType.AuxOutput1)

    def set_position_mode(self):
        self.neutralMotors()
        self.reset_drive_sensors()

        self.right_encoder_motor.selectProfileSlot(DriverComponent.slot_distance, DriverComponent.PID_PRIMARY)
        self.right_encoder_motor.selectProfileSlot(DriverComponent.slot_turning, DriverComponent.PID_TURN)

    def set_position(self, inches: float):
        target_sensor_units = 36 / DriverComponent.CONV_FACTOR
        target_turn = 0

        print("closed loop error: {}".format(self.right_encoder_motor.getClosedLoopError(DriverComponent.slot_distance)))
        # print("closed loop target: {}".format(self.right_encoder_motor.getClosedLoopTarget(DriverComponent.slot_distance)))

        self.right_encoder_motor.set(ControlMode.Position, target_sensor_units)
        self.left_encoder_motor.follow(self.right_encoder_motor, FollowerType.AuxOutput1)
    """

    def update_move_to_position(self, inches: float):
        self._distance_controller.setSetpoint(inches)
        self._angular_controller.setSetpoint(0)
        if not self._distance_controller.isEnabled():
            self._distance_controller.enable()
        if not self._angular_controller.isEnabled():
            self._angular_controller.enable()
        self.set_curve(self._linear_pid, self._angular_pid)
        

    def update_turn_angle(self, degrees: float):
        self._angular_controller.setSetpoint(degrees)
        if not self._angular_controller.isEnabled():
            self._angular_controller.enable()
        self.set_curve(0, self._angular_pid)

    def disable_pid(self):
        if self._angular_controller.isEnabled():
            self._angular_controller.disable()
        if self._distance_controller.isEnabled():
            self._distance_controller.disable()

    def set_curve(self, linear, angular):
        self.disable_pid()
        self.last_linear_input = self.clamp_deceleration(linear, self.last_linear_input, DriverComponent.LINEAR_DECELERATION_THRESHOLD)
        self.last_angular_input = self.clamp_deceleration(angular, self.last_angular_input, DriverComponent.ANGULAR_DECELERATION_THRESHOLD)
        self.set_curve_raw(self.last_linear_input, self.last_angular_input)

    def reset_drive_sensors(self):
        self.disable_pid()
        self.left_encoder_motor.getSensorCollection().setQuadraturePosition(0, DriverComponent.TimeOut_ms)
        self.right_encoder_motor.getSensorCollection().setQuadraturePosition(0, DriverComponent.TimeOut_ms)
        self.driver_gyro.reset()
        self.pigeon.setYaw(0, DriverComponent.TimeOut_ms)
        self.pigeon.setAccumZAngle(0, DriverComponent.TimeOut_ms)

    @property
    def current_distance(self):
        return DriverComponent.CONV_FACTOR * self.left_encoder_motor.getSelectedSensorPosition(0)
        # return DriverComponent.CONV_FACTOR * self.right_encoder_motor.getSelectedSensorPosition(0)
        # return DriverComponent.CONV_FACTOR * ((self.left_encoder_motor.getSelectedSensorPosition(0) + self.right_encoder_motor.getSelectedSensorPosition(0)) / 2)

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
