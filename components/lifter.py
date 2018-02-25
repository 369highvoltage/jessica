from wpilib import DigitalInput, AnalogPotentiometer, SmartDashboard
from ctre import WPI_TalonSRX, NeutralMode, FeedbackDevice, ControlMode
from enum import Enum, auto
from components.position import Position


class MovementDir(Enum):
    UP = auto()
    DOWN = auto()
    STOP = auto()


"""
    Class Lifter (extends Elevator)
"""
class Lifter(Position):
    elevator_motor: WPI_TalonSRX
    elevator_bottom_switch: DigitalInput

    carriage_motor: WPI_TalonSRX
    carriage_bottom_switch: DigitalInput
    carriage_top_switch: DigitalInput
    carriage_pot: AnalogPotentiometer

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

    ALLOWABLE_ERROR = 0

    def __init__(self):
        self.carriage_motor_speed = 0.0
        self.elevator_motor_speed = 0.0
        self.manual_control = True
        self.is_reset = False
        self.speed = 1.0
        self.direction = MovementDir.STOP

    def setup(self):
        self.configure_talons()

    def move_elevator(self, speed: float):
        self.elevator_motor_speed = speed

    def move_carriage(self, speed: float):
        self.carriage_motor_speed = speed

    def reset_position(self):
        if self.elevator_bottom_switch.get() and self.carriage_bottom_switch.get():
            self._limit_elevator(0)
            self._limit_carriage(0)
            self.elevator_motor.setSelectedSensorPosition(0, 0, Lifter.TIMEOUT_MS)
            self.is_reset = True
        self._limit_elevator(-0.25)
        self._limit_carriage(-0.25)
        self.is_reset = False

    def move(self, direction: MovementDir):
        self.direction = direction

    def configure_talons(self):
        self.elevator_motor.setNeutralMode(NeutralMode.Brake)
        self.carriage_motor.setNeutralMode(NeutralMode.Brake)

        self.elevator_motor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, 0, Lifter.TIMEOUT_MS)
        self.elevator_motor.setSensorPhase(True)

        self.elevator_motor.setInverted(False)

        self.elevator_motor.configNominalOutputForward(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.elevator_motor.configNominalOutputReverse(Lifter.ELEVATOR_ZERO, Lifter.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputForward(Lifter.el_up, Lifter.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputReverse(Lifter.el_down, Lifter.TIMEOUT_MS)

        self.elevator_motor.configAllowableClosedloopError(0, Lifter.ALLOWABLE_ERROR, Lifter.TIMEOUT_MS)

        self.elevator_motor.config_kF(0, Lifter.ELEVATOR_kF, Lifter.TIMEOUT_MS)
        self.elevator_motor.config_kP(0, Lifter.ELEVATOR_kP, Lifter.TIMEOUT_MS)
        self.elevator_motor.config_kI(0, Lifter.ELEVATOR_kI, Lifter.TIMEOUT_MS)
        self.elevator_motor.config_kD(0, Lifter.ELEVATOR_kD, Lifter.TIMEOUT_MS)

    def _limit_elevator(self, speed):
        if self.elevator_bottom_switch.get() and speed < 0:
            self.elevator_motor.set(Lifter.ELEVATOR_ZERO)
        else:
            self.elevator_motor.set(speed + Lifter.ELEVATOR_ZERO)

    def _limit_carriage(self, speed):
        if (self.carriage_bottom_switch.get() and speed < 0) \
                or (self.carriage_top_switch.get() and speed > 0):
            self.carriage_motor.set(Lifter.CARRIAGE_ZERO)
        else:
            self.carriage_motor.set(speed + Lifter.CARRIAGE_ZERO)

    def execute(self):
        if self.manual_control:
            self.is_reset = False
            # self._limit_elevator(self.elevator_motor_speed)
            # self._limit_carriage(self.carriage_motor_speed)
            if self.direction is MovementDir.STOP:
                self._limit_elevator(0)
                self._limit_carriage(0)
            if self.direction is MovementDir.UP:
                self._limit_elevator(self.speed)
                self._limit_carriage(self.speed)
            if self.direction is MovementDir.DOWN:
                self._limit_elevator(-self.speed)
                self._limit_carriage(-self.speed)
        else:
            if self.is_reset:
                # self.elevator_motor.set(WPI_TalonSRX.ControlMode.Position, self.get_target_distances()["elevator"])
                pass
            else:
                self.reset_position()

        SmartDashboard.putBoolean('lifter/elevator_bottom_switch', self.elevator_bottom_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_bottom_switch', self.carriage_bottom_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_top_switch', self.carriage_top_switch.get())
        SmartDashboard.putNumber('lifter/elevator_motor_speed', self.elevator_motor_speed)
        SmartDashboard.putNumber('lifter/carriage_motor_speed', self.carriage_motor_speed)
        SmartDashboard.putNumber('lifter/elevator_encoder', self.elevator_motor.getQuadraturePosition())
        SmartDashboard.putNumber('lifter/carriage_potentiometer', self.carriage_pot.get())

    def current_distance(self) -> dict:
        return {
            "encoder": self.elevator_motor.getSelectedSensorPosition(),
            "carriage": 0
        }

    @property
    def _current_enc_position(self):
        pass

    @property
    def _current_pot_position(self):
        pass
