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
    # ELEVATOR_MULTIPLIER = 1635.15 / 6317.67
    ELEVATOR_MULTIPLIER = 2102.35 / 3631.33
    CARRIAGE_MULTIPLIER = 1.0 - ELEVATOR_MULTIPLIER

    # Max heights of each stage.
    ELEVATOR_MAX_HEIGHT = 40
    CARRIAGE_MAX_HEIGHT = 40

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

    # ALLOWABLE_ERROR = 2

    CARRIAGE_ALLOWABLE_ERROR = int(2 / CARRIAGE_CONV_FACTOR)
    ELEVATOR_ALLOWABLE_ERROR = int(2 / ELEVATOR_CONV_FACTOR)

    # positions = {
    #     "floor": 2.0,
    #     "portal": 34.0,
    #     "scale_low": 48.0,
    #     "scale_mid": 60.0,
    #     "scale_high": 72.0,
    #     "max_height": 84.0
    # }

    positions = {
        "floor": 0.5,
        "portal": 34.0,
        "scale_low": 52.0,
        "scale_mid": 68.0,
        "scale_high": 78.0
    }

    def __init__(self):
        # self.elevator_motor = WPI_TalonSRX(5)
        self.elevator_motor = None
        self.elevator_bottom_switch = DigitalInput(9)

        self.carriage_motor = WPI_TalonSRX(3)
        self.carriage_bottom_switch = DigitalInput(1)
        self.carriage_top_switch = DigitalInput(2)

        self._is_reset = False

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

        self.elevator_motor.configAllowableClosedloopError(0, LifterComponent.ELEVATOR_ALLOWABLE_ERROR, LifterComponent.TIMEOUT_MS)

        self.elevator_motor.configForwardSoftLimitThreshold(int(LifterComponent.ELEVATOR_MAX_HEIGHT / LifterComponent.ELEVATOR_CONV_FACTOR), 0)

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

        self.carriage_motor.configAllowableClosedloopError(0, LifterComponent.CARRIAGE_ALLOWABLE_ERROR, LifterComponent.TIMEOUT_MS)

        self.carriage_motor.configForwardSoftLimitThreshold(int(LifterComponent.CARRIAGE_MAX_HEIGHT / LifterComponent.CARRIAGE_CONV_FACTOR), 0)

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

    def reset_sensors(self):
        self.carriage_motor.setSelectedSensorPosition(0, 0, LifterComponent.TIMEOUT_MS)
        self.elevator_motor.setSelectedSensorPosition(0, 0, LifterComponent.TIMEOUT_MS)
        self._is_reset = True

    @property
    def current_elevator_position(self) -> float:
        return self.elevator_motor.getSelectedSensorPosition(0) * LifterComponent.ELEVATOR_CONV_FACTOR

    @property
    def current_carriage_position(self) -> float:
        return self.carriage_motor.getSelectedSensorPosition(0) * LifterComponent.CARRIAGE_CONV_FACTOR

    @property
    def current_position(self) -> float:
        return self.current_elevator_position + self.current_carriage_position

    def elevator_to_target_position(self, inches: float):
        if self._is_reset:
            self.elevator_motor.set(WPI_TalonSRX.ControlMode.Position, inches / LifterComponent.ELEVATOR_CONV_FACTOR)

    def carriage_to_target_position(self, inches: float):
        if self._is_reset:
            self.carriage_motor.set(WPI_TalonSRX.ControlMode.Position, inches / LifterComponent.CARRIAGE_CONV_FACTOR)

    def lift_to_distance(self, inches):
        i = inches + 6
        elevator = min(i * LifterComponent.ELEVATOR_MULTIPLIER, LifterComponent.ELEVATOR_MAX_HEIGHT)
        carriage = i - elevator

        print("lift_to_distance carriage" + str(carriage))
        print("lift_to_distance elevate" + str(elevator))
        print("lift_to_distance lifter" + str(carriage + elevator))

        self.elevator_to_target_position(elevator)
        self.carriage_to_target_position(carriage)

    def is_at_position(self, position: str) -> bool:
        return self.is_at_distance(LifterComponent.positions[position])

    def is_at_distance(self, inches: float) -> bool:
        return inches - 5 < self.current_position < inches + 5

    def closest_position(self) -> tuple:
        # returns the key for the position closest to the current position
        positions = [(key, position) for key, position in LifterComponent.positions.items()]
        return min(positions, key=lambda position: abs(self.current_position-position[1]))

    def next_position(self) -> str:
        position = self.closest_position()
        positions = [(key, position) for key, position in LifterComponent.positions.items()]
        index = positions.index(position)
        if index == len(positions) - 1:
            return position[0]
        return positions[index + 1][0]

    def prev_position(self) -> str:
        position = self.closest_position()
        positions = [(key, position) for key, position in LifterComponent.positions.items()]
        index = positions.index(position)
        if index == 0:
            return position[0]
        return positions[index - 1][0]