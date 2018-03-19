from components.driver import Driver
from wpilib import ADXRS450_Gyro
from components.lifter import Lifter
from components.gripper import Gripper
# from robotpy_ext.autonomous import state as auto_state
from magicbot.state_machine import AutonomousStateMachine, timed_state, state


class Auto(AutonomousStateMachine):
    driver = Driver
    driver_gyro = ADXRS450_Gyro
    lifter = Lifter
    gripper = Gripper

    def __init__(self):
        # self.states = []
        self.__current_state = {}
        self.gen_instance = None

    # Generator which moves to the next state when ready.
    def get_next_state(self):
        for c_state in self.states:
            yield c_state

    # Call next() in each state, ala Express.js
    def next(self, now=False):
        self.__current_state = next(self.gen_instance)
        if now:
            self.next_state_now(self.__current_state ["state"])
        else:
            self.next_state(self.__current_state ["state"])

    @state(first=True)
    def start(self):
        self.gen_instance = self.get_next_state()
        self.next(now=True)

    @state
    def lift(self):
        # self.lifter.lift_to(self.__current_state ["position"])
        self.next(now=True)

    @state
    def turn(self, initial_call):
        if initial_call:
            self.driver.reset_drive_sensors()
        self.driver.set_curve(self.__current_state ["linear"], self.__current_state ["angular"]) # Turn at 0.5 speed.

        if (self.__current_state ["angle"]) - 1.0 < self.driver_gyro.getAngle() < (self.__current_state ["angle"] + 1.0):
            self.next()

    @state
    def move(self, initial_call):
        if initial_call:
            self.driver.reset_drive_sensors()
        self.driver.set_curve(self.__current_state ["linear"], 0.0)

        if self.driver.current_distance >= self.__current_state ["displacement"]:
            self.next()

    @timed_state(duration=0.25, must_finish=True)
    def shoot(self):
        # self.gripper.shoot()
        self.next()

    @state
    def finish(self):
        # Reset states
        self.__current_state  = self.states[0]
