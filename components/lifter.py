from wpilib import DigitalInput, AnalogPotentiometer, SmartDashboard, AnalogInput
from ctre import WPI_TalonSRX, NeutralMode, FeedbackDevice, ControlMode
from enum import Enum, auto
from components.position import Position


class MovementDir(Enum):
    UP = auto()
    DOWN = auto()
    STOP = auto()


class Lifter(Position):
    elevator_motor: WPI_TalonSRX
    elevator_bottom_switch: DigitalInput

    carriage_motor: WPI_TalonSRX
    carriage_bottom_switch: DigitalInput
    carriage_top_switch: DigitalInput

    el_down = -1
    el_up = 1
    carriage_down = -1
    carriage_up = 1
    MAX_SPEED = 0.5
    ELEVATOR_ZERO = 0.0
    CARRIAGE_ZERO = 0.0
    TIMEOUT_MS = 0

    ELEVATOR_kF = 0.0
    ELEVATOR_kP = 0.1
    ELEVATOR_kI = 0.0
    ELEVATOR_kD = 0.0

    ALLOWABLE_ERROR = 2

    def __init__(self):
        super().__init__()
        self.carriage_motor_speed = 0.0
        self.elevator_motor_speed = 0.0
        self.manual_control = False
        self.is_reset = False
        self.speed = 1.0
        self.direction = MovementDir.STOP

    def setup(self):
        self.configure_talons()

    def move_sync(self, speed: float):
        self.move_elevator(speed)
        self.move_carriage(speed)

    def move_elevator(self, speed: float):
        self.elevator_motor_speed = speed

    def move_carriage(self, speed: float):
        self.carriage_motor_speed = speed

    def manual_reset(self):
        self.is_reset = True
        self.reset_encoders()
        self.target_position = self.positions[0]
        self.index = 0

    def reset_encoders(self):
        self.carriage_motor.setSelectedSensorPosition(0, 0, Lifter.TIMEOUT_MS)
        self.elevator_motor.setSelectedSensorPosition(0, 0, Lifter.TIMEOUT_MS)

    def reset_position(self):
        if self.elevator_bottom_switch.get() and self.carriage_bottom_switch.get():
            self._limit_elevator(0)
            self._limit_carriage(0)
            self.reset_encoders()
            self.is_reset = True
            self.target_position = self.positions[0]
            self.index = 0
        else:
            if not self.elevator_bottom_switch.get():
                self._limit_elevator(-0.25)
            if not self.carriage_bottom_switch.get():
                self._limit_carriage(-0.25)
            self.is_reset = False

    def move(self, direction: MovementDir):
        self.direction = direction

    def configure_talons(self):
        # elevator config

        self.elevator_motor.setNeutralMode(NeutralMode.Brake)

        self.elevator_motor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, 0, Lifter.TIMEOUT_MS)

        self.elevator_motor.setSensorPhase(True)
        self.elevator_motor.setInverted(True)

        self.elevator_motor.configNominalOutputForward(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.elevator_motor.configNominalOutputReverse(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputForward(Lifter.el_up, Lifter.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputReverse(Lifter.el_down, Lifter.TIMEOUT_MS)

        self.elevator_motor.configNominalOutputForward(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.elevator_motor.configNominalOutputReverse(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputForward(Lifter.el_up, Lifter.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputReverse(Lifter.el_down, Lifter.TIMEOUT_MS)

        self.elevator_motor.configAllowableClosedloopError(0, Lifter.ALLOWABLE_ERROR, Lifter.TIMEOUT_MS)

        self.elevator_motor.config_kF(0, Lifter.ELEVATOR_kF, Lifter.TIMEOUT_MS)
        self.elevator_motor.config_kP(0, Lifter.ELEVATOR_kP, Lifter.TIMEOUT_MS)
        self.elevator_motor.config_kI(0, Lifter.ELEVATOR_kI, Lifter.TIMEOUT_MS)
        self.elevator_motor.config_kD(0, Lifter.ELEVATOR_kD, Lifter.TIMEOUT_MS)

        # carriage config

        self.carriage_motor.setNeutralMode(NeutralMode.Brake)

        self.carriage_motor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, 0, Lifter.TIMEOUT_MS)

        self.carriage_motor.setSensorPhase(True)
        self.carriage_motor.setInverted(True)

        self.carriage_motor.configNominalOutputForward(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.carriage_motor.configNominalOutputReverse(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputForward(Lifter.el_up, Lifter.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputReverse(Lifter.el_down, Lifter.TIMEOUT_MS)

        self.carriage_motor.configNominalOutputForward(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.carriage_motor.configNominalOutputReverse(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputForward(Lifter.el_up, Lifter.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputReverse(Lifter.el_down, Lifter.TIMEOUT_MS)

        self.carriage_motor.configAllowableClosedloopError(0, Lifter.ALLOWABLE_ERROR, Lifter.TIMEOUT_MS)

        self.carriage_motor.config_kF(0, Lifter.ELEVATOR_kF, Lifter.TIMEOUT_MS)
        self.carriage_motor.config_kP(0, Lifter.ELEVATOR_kP, Lifter.TIMEOUT_MS)
        self.carriage_motor.config_kI(0, Lifter.ELEVATOR_kI, Lifter.TIMEOUT_MS)
        self.carriage_motor.config_kD(0, Lifter.ELEVATOR_kD, Lifter.TIMEOUT_MS)

    def _limit_elevator(self, speed):
        # if self.elevator_bottom_switch.get() and speed < 0:
        #     self.elevator_motor.set(Lifter.ELEVATOR_ZERO)
        if (self.elevator_bottom_switch.get() and speed < 0) \
                or (self.current_distance()["elevator"]*Lifter.ELEVATOR_CONV_FACTOR >= Lifter.ELEVATOR_MAX_HEIGHT - 2 and speed > 0):
            self.elevator_motor.set(Lifter.ELEVATOR_ZERO)
        else:
            s = speed + Lifter.ELEVATOR_ZERO
            self.elevator_motor.set(s * 0.75)

    def _limit_carriage(self, speed):
        if (self.carriage_bottom_switch.get() and speed < 0) \
                or (self.carriage_top_switch.get() and speed > 0):
                # or (self.current_distance()["carriage"]*Lifter.CARRIAGE_CONV_FACTOR >= Lifter.CARRIAGE_MAX_HEIGHT - 2 and speed > 0):
        # if self.carriage_top_switch.get() and speed > 0:
        # if self.carriage_bottom_switch.get() and speed < 0:
            self.carriage_motor.set(Lifter.CARRIAGE_ZERO)
        else:
            s = speed + Lifter.CARRIAGE_ZERO
            self.carriage_motor.set(s * 0.75)

    def execute(self):
        if not self.manual_control:
            if self.is_reset:
                distances = self.get_target_distances()
                # if self.is_at_target_distance():
                #     self.elevator_motor.set(Lifter.ELEVATOR_ZERO)
                #     self.carriage_motor.set(Lifter.CARRIAGE_ZERO)
                # else:
                self.elevator_motor.set(WPI_TalonSRX.ControlMode.Position, distances["elevator"])
                self.carriage_motor.set(WPI_TalonSRX.ControlMode.Position, distances["carriage"])
            else:
                self.reset_position()
        else:
            self._limit_elevator(self.elevator_motor_speed)
            self._limit_carriage(self.carriage_motor_speed)






        # if self.manual_control:
        #     # self.is_reset = False
        #     # self._limit_elevator(self.elevator_motor_speed)
        #     # self._limit_carriage(self.carriage_motor_speed)
        #     if self.direction is MovementDir.STOP:
        #         self._limit_elevator(0)
        #         self._limit_carriage(0)
        #     if self.direction is MovementDir.UP:
        #         self._limit_elevator(self.speed)
        #         self._limit_carriage(self.speed)
        #     if self.direction is MovementDir.DOWN:
        #         self._limit_elevator(-self.speed)
        #         self._limit_carriage(-self.speed)
        # else:
        #     if self.is_reset:
        #         distances = self.get_target_distances()
        #         self.elevator_motor.set(WPI_TalonSRX.ControlMode.Position, distances["elevator"])
        #         self.carriage_motor.set(WPI_TalonSRX.ControlMode.Position, distances["carriage"])
        #     else:
        #         self.reset_position()

        SmartDashboard.putBoolean('lifter/elevator_bottom_switch', self.elevator_bottom_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_bottom_switch', self.carriage_bottom_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_top_switch', self.carriage_top_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_bottom_switch', self.carriage_bottom_switch.get())
        SmartDashboard.putNumber('lifter/elevator_motor_speed', self.elevator_motor_speed)
        SmartDashboard.putNumber('lifter/carriage_motor_speed', self.carriage_motor_speed)
        SmartDashboard.putNumber('lifter/elevator_encoder', self.elevator_motor.getSelectedSensorPosition(0))
        SmartDashboard.putNumber('lifter/carriage_encoder', self.carriage_motor.getSelectedSensorPosition(0))
        cd = self.current_distance()
        SmartDashboard.putNumber('lifter/current_dist_elevator', cd["elevator"] * Position.ELEVATOR_CONV_FACTOR)
        SmartDashboard.putNumber('lifter/current_dist_carriage', cd["carriage"] * Position.CARRIAGE_CONV_FACTOR)
        tg = self.get_target_distances()
        SmartDashboard.putNumber('lifter/target_dist_elevator', tg["elevator"])
        SmartDashboard.putNumber('lifter/target_dist_carriage', tg["carriage"])
        SmartDashboard.putNumber('lifter/position_current_distance', self._current_distance)
        SmartDashboard.putNumber('lifter/position_target_distance', self.target_distance)
        SmartDashboard.putBoolean('lifter/is_at_target_distance', self.is_at_target_distance())

    def current_distance(self) -> dict:
        return {
            "elevator": self.elevator_motor.getSelectedSensorPosition(0),
            "carriage": self.carriage_motor.getSelectedSensorPosition(0)
        }

    @property
    def _current_enc_position(self):
        pass

    @property
    def _current_pot_position(self):
        pass
