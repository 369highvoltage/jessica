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
from ctre import WPI_TalonSRX, NeutralMode, FeedbackDevice, ControlMode


class LifterComponent:
    # RPM Multipliers
    ELEVATOR_MULTIPLIER = 1635.15 / 6317.67
    CARRIAGE_MULTIPLIER = 1.0 - ELEVATOR_MULTIPLIER

    # Max heights of each stage.
    ELEVATOR_MAX_HEIGHT = 40
    CARRIAGE_MAX_HEIGHT = 37

    # Conversion factors (counts to inches)
    # CHANGE THESE VALUES
    ELEVATOR_CONV_FACTOR = 0.00134
    CARRIAGE_CONV_FACTOR = 0.000977

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
        self.elevator_motor = WPI_TalonSRX(5)
        self.elevator_bottom_switch = DigitalInput(9)

        self.carriage_motor = WPI_TalonSRX(2)
        self.carriage_bottom_switch = DigitalInput(1)
        self.carriage_top_switch = DigitalInput(2)

        # configure elevator motor and encoder

        self.elevator_motor.setNeutralMode(NeutralMode.Brake)

        self.elevator_motor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, 0, LifterComponent.TIMEOUT_MS)

        self.elevator_motor.setSensorPhase(True)
        self.elevator_motor.setInverted(True)

        self.elevator_motor.configNominalOutputForward(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.configNominalOutputReverse(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputForward(LifterComponent.el_up, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputReverse(LifterComponent.el_down, LifterComponent.TIMEOUT_MS)

        self.elevator_motor.configNominalOutputForward(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.configNominalOutputReverse(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputForward(LifterComponent.el_up, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.configPeakOutputReverse(LifterComponent.el_down, LifterComponent.TIMEOUT_MS)

        self.elevator_motor.configAllowableClosedloopError(0, LifterComponent.ALLOWABLE_ERROR, LifterComponent.TIMEOUT_MS)

        self.elevator_motor.config_kF(0, LifterComponent.ELEVATOR_kF, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.config_kP(0, LifterComponent.ELEVATOR_kP, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.config_kI(0, LifterComponent.ELEVATOR_kI, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.config_kD(0, LifterComponent.ELEVATOR_kD, LifterComponent.TIMEOUT_MS)

        # configure carriage motor and encoder

        self.carriage_motor.setNeutralMode(NeutralMode.Brake)

        self.carriage_motor.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, 0, LifterComponent.TIMEOUT_MS)

        self.carriage_motor.setSensorPhase(True)
        self.carriage_motor.setInverted(True)

        self.carriage_motor.configNominalOutputForward(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.configNominalOutputReverse(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputForward(LifterComponent.el_up, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputReverse(LifterComponent.el_down, LifterComponent.TIMEOUT_MS)

        self.carriage_motor.configNominalOutputForward(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.configNominalOutputReverse(LifterComponent.ELEVATOR_ZERO, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputForward(LifterComponent.el_up, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.configPeakOutputReverse(LifterComponent.el_down, LifterComponent.TIMEOUT_MS)

        self.carriage_motor.configAllowableClosedloopError(0, LifterComponent.ALLOWABLE_ERROR, LifterComponent.TIMEOUT_MS)

        self.carriage_motor.config_kF(0, LifterComponent.ELEVATOR_kF, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.config_kP(0, LifterComponent.ELEVATOR_kP, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.config_kI(0, LifterComponent.ELEVATOR_kI, LifterComponent.TIMEOUT_MS)
        self.carriage_motor.config_kD(0, LifterComponent.ELEVATOR_kD, LifterComponent.TIMEOUT_MS)

    def set_elevator_speed(self, speed):
        if (speed > 0 and self.current_elevator_position >= LifterComponent.ELEVATOR_MAX_HEIGHT - 2) \
                or (speed < 0 and self.elevator_bottom_switch.get()):
            self.elevator_motor.set(0)
        else:
            self.elevator_motor.set(speed)

    def set_carriage_speed(self, speed):
        if (speed > 0 and self.carriage_top_switch.get()) \
                or (speed < 0 and self.carriage_bottom_switch.get()):
            self.carriage_motor.set(0)
        else:
            self.carriage_motor.set(speed)

    @property
    def current_elevator_position(self) -> float:
        return self.elevator_motor.getSelectedSensorPosition(0) * LifterComponent.ELEVATOR_CONV_FACTOR

    @property
    def current_carriage_position(self) -> float:
        return self.carriage_motor.getSelectedSensorPosition(0) * LifterComponent.CARRIAGE_CONV_FACTOR

    @property
    def current_position(self) -> float:
        return self.current_elevator_position + self.current_carriage_position

    def elevator_to_target_position(self, position: float):
        self.elevator_motor.set(WPI_TalonSRX.ControlMode.Position, position)

    def carriage_to_target_position(self, position: float):
        self.carriage_motor.set(WPI_TalonSRX.ControlMode.Position, position)

    def is_at_position(self, position: float) -> bool:
        return position - 5 < self.current_position < position + 5
