from wpilib import DigitalInput, AnalogPotentiometer, SmartDashboard
from ctre import WPI_TalonSRX, NeutralMode


"""
    Class Lifter (extends Elevator)
"""
class Lifter:
    elevator_motor: WPI_TalonSRX
    elevator_bottom_switch: DigitalInput

    lifter_motor: WPI_TalonSRX
    lifter_bottom_switch: DigitalInput
    lifter_pot: AnalogPotentiometer

    el_down = -1
    el_up = 1
    lift_down = -1
    lift_up = 1
    MAX_SPEED = 0.5

    def __init__(self):
        self.positions = (
            { "name": "floor", "enc_dist": 0.0, "pot_dist": 0.0 },
            { "name": "switch", "enc_dist": 0.0, "pot_dist": 100.0 },
            { "name": "scale-bot", "enc_dist": 40.0, "pot_dist": 0.0 },
            { "name": "scale-mid", "enc_dist": 40.0, "pot_dist": 50.0 },
            { "name": "scale-top", "enc_dist": 40.0, "pot_dist": 100.0 }
        )
        self.target_position = None
        self.current_position = None
        self.isReady = False
        self.lift_motor_speed = 0.0
        self.elevator_motor_speed = 0.0
        self.manual_control = True

    def setup(self):
        self.configure_talons()

    def move_elevator(self, speed: float):
        self.elevator_motor_speed = speed

    def move_carriage(self, speed: float):
        self.lift_motor_speed = speed

    def reset_position(self):
        if not self.elevator_bottom_switch.get():
            self.elevator_motor.set(Lifter.el_down * Lifter.MAX_SPEED)
        else:
            self.elevator_motor.stopMotor()
        if not self.lifter_bottom_switch.get():
            self.lifter_motor.set(Lifter.el_down * Lifter.MAX_SPEED)
        else:
            self.lifter_motor.stopMotor()

        if self.elevator_bottom_switch and self.lifter_bottom_switch:
            self.current_position = self.positions[0]
            self.isReady = True

    def configure_talons(self):
        self.elevator_motor.setNeutralMode(NeutralMode.Brake)
        self.lifter_motor.setNeutralMode(NeutralMode.Brake)

    def set_target_position(self, position_name: str):
        for pos in self.positions:
            if pos.name == position_name:
                self.target_position = pos
                break

    def execute(self):
        if self.manual_control:
            self.elevator_motor.set(self.elevator_motor_speed + 0.175)
            self.lifter_motor.set(self.lift_motor_speed + 0.125)
        else:
            if self.isReady:
                if self.target_position:
                    done = 0
                    if self._move_elv_to_target_dist():
                        done += 1
                    if self._move_lift_to_target_dist():
                        done += 1

                    if done == 2:
                        self.current_position = self.target_position
                        self.target_position = None
            else:
                self.configure_talons()
                self.reset_position()

        SmartDashboard.putNumber('lifter/elevator_motor_speed', self.elevator_motor_speed)
        SmartDashboard.putNumber('lifter/carriage_motor_speed', self.lift_motor_speed)
        SmartDashboard.putNumber('lifter/elevator_encoder', self.elevator_motor.getQuadraturePosition())
        SmartDashboard.putNumber('lifter/carriage_potentiometer', self.lifter_pot.get())



    def _move_elv_to_target_dist(self):
        diff = self.elevator_motor.getQuadraturePosition() - self.current_position["enc_dist"]
        if -5 < diff < 5:
            v = max(min(Lifter.el_up * diff, Lifter.MAX_SPEED), Lifter.MAX_SPEED)
            self.elevator_motor.set(v)
            return False
        else:
            return True

    def _move_lift_to_target_dist(self):
        diff = self.lifter_pot.get() - self.current_position["pos_dist"]
        if -5 < diff < 5:
            v = max(min(Lifter.lift_up * diff, Lifter.MAX_SPEED), Lifter.MAX_SPEED)
            self.lifter_motor.set(v)
            return False
        else:
            return True

    @property
    def _current_enc_position(self):
        pass

    @property
    def _current_pot_position(self):
        pass
