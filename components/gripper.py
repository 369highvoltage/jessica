from wpilib import Talon, DoubleSolenoid, SmartDashboard, DigitalInput, Relay
from magicbot import tunable
from enum import Enum, auto


class GripState(Enum):
    PUSH = auto()
    PULL = auto()
    STOP = auto()

class GripLiftState(Enum):
    UP = auto()
    DOWN = auto()
    STOP = auto()


class Gripper:
    claw_left_motor: Talon
    claw_right_motor: Talon

    claw_up_limit: DigitalInput
    claw_lift_motor: Relay

    claw_open_solenoid: DoubleSolenoid

    def __init__(self):
        self.open_state = None
        self.grip_state = GripState.STOP
        self.speed = 1.0
        self.default_speed = 1.0
        self.lift_state = GripLiftState.STOP

    def on_enable(self):
        self.set_claw_open_state(True)

    def set_grip_speed(self, speed: float):
        self.speed = speed

    def set_claw_open_state(self, open_state: bool):
        if open_state:
            self.claw_open_solenoid.set(DoubleSolenoid.Value.kForward)
            self.open_state = True
        else:
            self.claw_open_solenoid.set(DoubleSolenoid.Value.kReverse)
            self.open_state = False

    def toggle_open(self):
        self.set_claw_open_state(not self.open_state)

    def set_grip_state(self, grip_state: GripState):
        self.grip_state = grip_state

    def set_lift_state(self, lift_state: GripLiftState):
        self.lift_state = lift_state

    def execute(self):
        if self.grip_state is GripState.STOP:
            self.claw_left_motor.set(0)
            self.claw_right_motor.set(0)
        else:
            sp = self.speed
            if self.grip_state is GripState.PUSH:
                sp = -self.speed
            self.claw_left_motor.set(sp)
            self.claw_right_motor.set(-sp)

        if self.lift_state is GripLiftState.STOP:
            self.claw_lift_motor.set(Relay.Value.kOff)
        elif self.lift_state is GripLiftState.UP:
            if self.claw_up_limit.get():
                self.claw_lift_motor.set(Relay.Value.kOff)
            else:
                self.claw_lift_motor.set(Relay.Value.kForward)
        elif self.lift_state is GripLiftState.DOWN:
            self.claw_lift_motor.set(Relay.Value.kReverse)

        if self.grip_state is GripState.STOP:
            SmartDashboard.putString('gripper/grip_state', 'STOP')
        if self.grip_state is GripState.PULL:
            SmartDashboard.putString('gripper/grip_state', 'PULL')
        if self.grip_state is GripState.PUSH:
            SmartDashboard.putString('gripper/grip_state', 'PUSH')

        if self.lift_state is GripLiftState.STOP:
            SmartDashboard.putString('gripper/lift_state', 'STOP')
        if self.lift_state is GripLiftState.DOWN:
            SmartDashboard.putString('gripper/lift_state', 'DOWN')
        if self.lift_state is GripLiftState.UP:
            SmartDashboard.putString('gripper/lift_state', 'UP')

        SmartDashboard.putString('gripper/lift_up_limit', self.claw_up_limit.get())

