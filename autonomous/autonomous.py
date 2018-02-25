from components.driver import Driver
from wpilib import ADXRS450_Gyro
from components.lifter import Lifter
from components.gripper import Gripper
# from robotpy_ext.autonomous import state as auto_state
from magicbot import AutonomousStateMachine, timed_state, state


class Auto(AutonomousStateMachine):
    driver = Driver
    driver_gyro = ADXRS450_Gyro
    lifter = Lifter
    gripper = Gripper

    def __init__(self):
        self.states = []
        self.current_state = {}

    # Generator which moves to the next state when ready.
    def get_next_state(self):
        for c_state in self.states:
            yield c_state

    # Call next() in each state, ala Express.js
    def next(self, now=False):
        self.current_state = self.get_next_state()
        if now:
            self.next_state_now(self.current_state["state"])
        else:
            self.next_state(self.current_state["state"])

    @state(first=True)
    def start(self):
        self.next(now=True)

    @state
    def lift(self):
        # self.lifter.lift_to(self.current_state["position"])
        self.next(now=True)

    @state
    def turn(self, initial_call):
        if initial_call:
            self.driver.reset_drive_sensors()
        self.driver.set_curve(self.current_state["linear"], self.current_state["angular"]) # Turn at 0.5 speed.

        if (self.current_state["angle"]) - 1.0 < self.driver_gyro.getAngle() < (self.current_state["angle"] + 1.0):
            self.next()

    @state
    def move(self, initial_call):
        if initial_call:
            self.driver.reset_drive_sensors()
        self.driver.set_curve(self.current_state["linear"], 0.0)

        if self.driver.current_distance >= self.current_state["displacement"]:
            self.next()

    @timed_state(duration=0.25, must_finish=True)
    def shoot(self):
        # self.gripper.shoot()
        self.next()

    @state
    def finish(self):
        # Reset states
        self.current_state = self.states[0]
