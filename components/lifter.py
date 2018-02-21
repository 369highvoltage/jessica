from wpilib import DigitalInput, AnalogPotentiometer, SmartDashboard
from ctre import WPI_TalonSRX, NeutralMode



"""
    Class Lifter (extends Elevator)
"""
class Lifter:
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

    def __init__(self):
        self.carriage_motor_speed = 0.0
        self.elevator_motor_speed = 0.0
        self.manual_control = True
        self.isReady = False

    def setup(self):
        self.configure_talons()

    def move_elevator(self, speed: float):
        self.elevator_motor_speed = speed

    def move_carriage(self, speed: float):
        self.carriage_motor_speed = speed

    def reset_position(self):
        if not self.elevator_bottom_switch.get():
            self.elevator_motor.set(Lifter.el_down * Lifter.MAX_SPEED)
        else:
            self.elevator_motor.stopMotor()
        if not self.carriage_bottom_switch.get():
            self.carriage_motor.set(Lifter.el_down * Lifter.MAX_SPEED)
        else:
            self.carriage_motor.stopMotor()

        if self.elevator_bottom_switch and self.carriage_bottom_switch:
            self.isReady = True

    def configure_talons(self):
        self.elevator_motor.setNeutralMode(NeutralMode.Brake)
        self.carriage_motor.setNeutralMode(NeutralMode.Brake)

    def execute(self):
        if self.manual_control:
            if self.elevator_bottom_switch.get() and self.elevator_motor_speed < 0:
                self.elevator_motor.set(0.175)
            else:
                self.elevator_motor.set(self.elevator_motor_speed + 0.175)
            if (self.carriage_bottom_switch.get() and self.carriage_motor_speed < 0) \
                    or (self.carriage_top_switch.get() and self.carriage_motor_speed > 0):
                self.carriage_motor.set(0.125)
            else:
                self.carriage_motor.set(self.carriage_motor_speed + 0.125)

        SmartDashboard.putBoolean('lifter/elevator_bottom_switch', self.elevator_bottom_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_bottom_switch', self.carriage_bottom_switch.get())
        SmartDashboard.putBoolean('lifter/carriage_top_switch', self.carriage_top_switch.get())
        SmartDashboard.putNumber('lifter/elevator_motor_speed', self.elevator_motor_speed)
        SmartDashboard.putNumber('lifter/carriage_motor_speed', self.carriage_motor_speed)
        SmartDashboard.putNumber('lifter/elevator_encoder', self.elevator_motor.getQuadraturePosition())
        SmartDashboard.putNumber('lifter/carriage_potentiometer', self.carriage_pot.get())

    @property
    def _current_enc_position(self):
        pass

    @property
    def _current_pot_position(self):
        pass
