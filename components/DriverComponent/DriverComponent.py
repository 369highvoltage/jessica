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
from ctre import WPI_TalonSRX, FeedbackDevice, RemoteSensorSource, PigeonIMU, ParamEnum
from wpilib.drive import DifferentialDrive
from Command import InstantCommand, Command
from wpilib.timer import Timer
from enum import Enum, auto
import math
from Events import Events


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

class Gains(object):
    def __init__(self, p: float = 0.0, i: float = 0.0, d: float = 0.0, f: float = 0.0, intergral_zone: int = 0, peak_out: float = 0.0):
        self.p = p
        self.i = i
        self.d = d
        self.f = f
        self.intergral_zone = intergral_zone
        self.peak_out = peak_out


class DriverComponent(Events):
    CONV_FACTOR = 0.0524 * 0.846
    LINEAR_DECELERATION_THRESHOLD = 0.3
    ANGULAR_DECELERATION_THRESHOLD = 0.6

    PID_PRIMARY = 0
    REMOTE_0 = 0
    REMOTE_1 = 1
    PID_TURN = 1
    TimeOut_ms = 0
    pigeonUnitsPerRotation = 8192
    turnTravelUnitsPerRotation = 3600

    nuetral_deadband = 0.1

    slot_0 = 0
    slot_1 = 1
    slot_2 = 2
    slot_3 = 3

    slot_distance =  slot_0
    slot_turning = slot_1
    slot_velocity = slot_2
    slot_motprof = slot_3

    gains_distance = Gains(p=0.0, i=0.0, d=0.0, f=0.0, intergral_zone=100, peak_out=0.50)
    gains_turning = Gains(p=0.0, i=0.0, d=0.0, f=0.0, intergral_zone=200, peak_out=1.0)
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
        # right_rear = Victor(6)
        right_rear = WPI_TalonSRX(7)
        self.pigeon = PigeonIMU(self.pigeon_talon)

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
        self.right_encoder_motor.configMotionAcceleration(1000, DriverComponent.TimeOut_ms)
        # _talonRght.configMotionCruiseVelocity(1000, Constants.kTimeoutMs);
        self.right_encoder_motor.configMotionCruiseVelocity(1000, DriverComponent.TimeOut_ms)

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

        # /* distance servo */
        # _talonRght.config_kP(Constants.kSlot_Distanc, Constants.kGains_Distanc.kP, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kP(
            DriverComponent.slot_distance,
            DriverComponent.gains_distance.p,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kI(Constants.kSlot_Distanc, Constants.kGains_Distanc.kI, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kI(
            DriverComponent.slot_distance,
            DriverComponent.gains_distance.i,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kD(Constants.kSlot_Distanc, Constants.kGains_Distanc.kD, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kD(
            DriverComponent.slot_distance,
            DriverComponent.gains_distance.d,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kF(Constants.kSlot_Distanc, Constants.kGains_Distanc.kF, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kF(
            DriverComponent.slot_distance,
            DriverComponent.gains_distance.f,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_IntegralZone(Constants.kSlot_Distanc, (int)Constants.kGains_Distanc.kIzone, Constants.kTimeoutMs);
        self.right_encoder_motor.config_IntegralZone(
            DriverComponent.slot_distance,
            DriverComponent.gains_distance.intergral_zone,
            DriverComponent.TimeOut_ms
        )
        
        # _talonRght.configClosedLoopPeakOutput(	Constants.kSlot_Distanc,
        #                                         Constants.kGains_Distanc.kPeakOutput,
        #                                         Constants.kTimeoutMs);
        self.right_encoder_motor.configClosedLoopPeakOutput(
            DriverComponent.slot_distance,
            DriverComponent.gains_distance.peak_out,
            DriverComponent.TimeOut_ms
        )

        # /* turn servo */
        # _talonRght.config_kP(Constants.kSlot_Turning, Constants.kGains_Turning.kP, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kP(
            DriverComponent.slot_turning,
            DriverComponent.gains_turning.p,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kI(Constants.kSlot_Turning, Constants.kGains_Turning.kI, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kI(
            DriverComponent.slot_turning,
            DriverComponent.gains_turning.i,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kD(Constants.kSlot_Turning, Constants.kGains_Turning.kD, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kD(
            DriverComponent.slot_turning,
            DriverComponent.gains_turning.d,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kF(Constants.kSlot_Turning, Constants.kGains_Turning.kF, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kF(
            DriverComponent.slot_turning,
            DriverComponent.gains_turning.f,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_IntegralZone(Constants.kSlot_Turning, (int)Constants.kGains_Turning.kIzone, Constants.kTimeoutMs);
        self.right_encoder_motor.config_IntegralZone(
            DriverComponent.slot_turning,
            DriverComponent.gains_turning.intergral_zone,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.configClosedLoopPeakOutput(	Constants.kSlot_Turning,
        #                                         Constants.kGains_Turning.kPeakOutput,
        #                                         Constants.kTimeoutMs);
        self.right_encoder_motor.configClosedLoopPeakOutput(
            DriverComponent.slot_turning,
            DriverComponent.gains_turning.peak_out,
            DriverComponent.TimeOut_ms
        )

        # /* magic servo */
        # _talonRght.config_kP(Constants.kSlot_MotProf, Constants.kGains_MotProf.kP, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kP(
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof.p,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kI(Constants.kSlot_MotProf, Constants.kGains_MotProf.kI, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kI(
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof.i,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kD(Constants.kSlot_MotProf, Constants.kGains_MotProf.kD, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kD(
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof.d,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kF(Constants.kSlot_MotProf, Constants.kGains_MotProf.kF, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kF(
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof.f,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_IntegralZone(Constants.kSlot_MotProf, (int)Constants.kGains_MotProf.kIzone, Constants.kTimeoutMs);
        self.right_encoder_motor.config_IntegralZone(
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof.intergral_zone,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.configClosedLoopPeakOutput(	Constants.kSlot_MotProf,
        #                                         Constants.kGains_MotProf.kPeakOutput,
        #                                         Constants.kTimeoutMs);
        self.right_encoder_motor.configClosedLoopPeakOutput(
            DriverComponent.slot_motprof,
            DriverComponent.gains_motprof.peak_out,
            DriverComponent.TimeOut_ms
        )

        # /* velocity servo */
        # _talonRght.config_kP(Constants.kSlot_Velocit, Constants.kGains_Velocit.kP, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kP(
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity.p,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kI(Constants.kSlot_Velocit, Constants.kGains_Velocit.kI, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kI(
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity.i,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kD(Constants.kSlot_Velocit, Constants.kGains_Velocit.kD, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kD(
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity.d,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_kF(Constants.kSlot_Velocit, Constants.kGains_Velocit.kF, Constants.kTimeoutMs);
        self.right_encoder_motor.config_kF(
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity.f,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.config_IntegralZone(Constants.kSlot_Velocit, (int)Constants.kGains_Velocit.kIzone, Constants.kTimeoutMs);
        self.right_encoder_motor.config_IntegralZone(
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity.intergral_zone,
            DriverComponent.TimeOut_ms
        )
        # _talonRght.configClosedLoopPeakOutput(	Constants.kSlot_Velocit,
        #                                         Constants.kGains_Velocit.kPeakOutput,
        #                                         Constants.kTimeoutMs);
        self.right_encoder_motor.configClosedLoopPeakOutput(
            DriverComponent.slot_velocity,
            DriverComponent.gains_velocity.peak_out,
            DriverComponent.TimeOut_ms
        )

        # _talonLeft.setNeutralMode(NeutralMode.Brake);
        # _talonRght.setNeutralMode(NeutralMode.Brake);
        
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
        self.left_encoder_motor.getSensorCollection().setQuadraturePosition(0, DriverComponent.TimeOut_ms)
        self.right_encoder_motor.getSensorCollection().setQuadraturePosition(0, DriverComponent.TimeOut_ms)
        self.pigeon.setYaw(0, DriverComponent.TimeOut_ms)
        self.pigeon.setAccumZAngle(0, DriverComponent.TimeOut_ms)

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
