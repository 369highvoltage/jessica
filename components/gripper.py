from wpilib import Talon, DoubleSolenoid, SmartDashboard
from magicbot import tunable
from enum import Enum, auto


class GripState(Enum):
    PUSH = auto()
    PULL = auto()
    STOP = auto()


class Gripper:
    claw_left_motor: Talon
    claw_right_motor: Talon



    claw_open_solenoid: DoubleSolenoid


    def __init__(self):
        self.open_state = None
        self.grip_state = GripState.STOP
        self.speed = 1.0

    def on_enable(self):
        self.set_claw_open_state(True)

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

    def execute(self):
        if self.grip_state == GripState.STOP:
            self.claw_left_motor.set(0)
            self.claw_right_motor.set(0)
        else:
            sp = self.speed
            if self.grip_state is GripState.PUSH:
                sp = -self.speed
            self.claw_left_motor.set(sp)
            self.claw_right_motor.set(-sp)

        if self.grip_state is GripState.STOP:
            SmartDashboard.putString('gripper/grip_state', 'STOP')
        if self.grip_state is GripState.PULL:
            SmartDashboard.putString('gripper/grip_state', 'PULL')
        if self.grip_state is GripState.PUSH:
            SmartDashboard.putString('gripper/grip_state', 'PUSH')
