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


class GripperComponent:

    lift_positions = {
        "up": 0.13,
        "down": 0.54,
        # "up": 0.2,
        # "down": 0.595
        # "up": 2.2,
        # "down": 4.0
    }

    def __init__(self):
        self.left_motor = Victor(0)
        self.right_motor = Victor(1)
        self.solenoid = DoubleSolenoid(2, 3)
        self.lift_motor = Victor(4)
        self.pot = AnalogPotentiometer(0)

        # state
        self._lift_state = None
        self._spread_state = None

    def set_spread_state(self, spread: bool):
        if spread:
            self.solenoid.set(DoubleSolenoid.Value.kForward)
            self._spread_state = True
        else:
            self.solenoid.set(DoubleSolenoid.Value.kReverse)
            self._spread_state = False

    def toggle_spread_state(self):
        if self._spread_state is None:
            self.set_spread_state(False)
        else:
            self.set_spread_state(not self._spread_state)

    def set_motor_speeds(self, left: float, right: float):
        self.left_motor.set(left)
        self.right_motor.set(-right)

    def set_lift_motor(self, speed):
        self.lift_motor.set(speed)

    def current_lift_state(self) -> str:
        positions = [(key, position) for key, position in GripperComponent.lift_positions.items()]
        return min(positions, key=lambda position: abs(self.pot.get() - position[1]))[0]


