from wpilib import DigitalInput, AnalogPotentiometer
from ctre import WPI_TalonSRX


"""
    Class Lifter (extends Elevator)
"""
class Lifter:
    elevator_motor: WPI_TalonSRX
    elevator_buttom_switch: DigitalInput

    lifter_motor: WPI_TalonSRX
    lifter_bottom_switch: DigitalInput
    lifter_pot: AnalogPotentiometer

    el_down = -1
    el_up = 1
    lift_down = -1
    lift_up = 1
    MAX_SPEED = 0.5

    def __init__(self):
        self.positions = [
            { "name": "floor", "enc_dist": 0.0, "pot_dist": 0.0 },
            { "name": "switch", "enc_dist": 0.0, "pot_dist": 100.0 },
            { "name": "scale-bot", "enc_dist": 40.0, "pot_dist": 0.0 },
            {"name": "scale-mid", "enc_dist": 40.0, "pot_dist": 50.0 },
            { "name": "scale-top", "enc_dist": 40.0, "pot_dist": 100.0 }
        ]
        self.target_position = None
        self.current_position = None
        self.isReady = False

    def reset_position(self):
        if not self.elevator_buttom_switch.get():
            self.elevator_motor.set(self.el_down * self.MAX_SPEED)
        else:
            self.elevator_motor.stopMotor()
        if not self.lifter_bottom_switch.get():
            self.lifter_motor.set(self.el_down * self.MAX_SPEED)
        else:
            self.lifter_motor.stopMotor()

        if self.elevator_buttom_switch and self.lifter_bottom_switch:
            self.current_position = self.positions[0]
            self.isReady = True



    def set_target_position(self, position_name: str):
        for pos in self.positions:
            if pos.name == position_name:
                self.target_position = pos
                break


    def execute(self):
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
            self.reset_position()

    def _move_elv_to_target_dist(self):
        diff = self.elevator_motor.getQuadraturePosition() - self.current_position["enc_dist"]
        if -5 < diff < 5:
            v = self.el_up * diff
            if v < 0:
                v = min(v, -1*self.MAX_SPEED)
            if v > 0:
                v = max(v, self.MAX_SPEED)
            self.elevator_motor.set(v)
            return False
        else:
            return True

    def _move_lift_to_target_dist(self):
        diff = self.lifter_pot.get() - self.current_position["pos_dist"]
        if -5 < diff < 5:
            v = self.lift_up * diff
            if v < 0:
                v = min(v, -1*self.MAX_SPEED)
            if v > 0:
                v = max(v, self.MAX_SPEED)
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
