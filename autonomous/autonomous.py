from components.driver import Driver, GearMode
from wpilib import ADXRS450_Gyro, DriverStation
from components.lifter import Lifter
from components.gripper import Gripper, GripState
# from robotpy_ext.autonomous import state as auto_state
from magicbot.state_machine import AutonomousStateMachine, timed_state, state


class Auto(AutonomousStateMachine):
    driver: Driver
    driver_gyro: ADXRS450_Gyro
    lifter: Lifter
    gripper: Gripper

    def __init__(self):
        super().__init__()
        # self.states = []
        self.__current_state = {}
        self.gen_instance = None
        self.gen_instance = self.get_next_state()

    def on_enable(self):
        super().on_enable()
        ds = DriverStation.getInstance()
        self.start_location = ds.getLocation()

        game_data = ds.getGameSpecificMessage()

        self.switch_position = game_data[0]
        self.scale_position = game_data[1]

        self.driver.set_gear(gear=GearMode.LOW)
        self.gripper.set_claw_open_state(False)
        self.lifter.manual_control = False
        self.gripper.set_position_bottom()

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

    @state
    def call_next(self):
        self.next()

    @state(must_finish=True)
    def lift(self):
        self.lifter.set_position(self.__current_state ["position"])
        if self.lifter.is_at_target_distance():
            self.next()
            # self.next(now=True)

    @state(must_finish=True)
    def turn(self, initial_call):
        if initial_call:
            self.driver.reset_drive_sensors()
        self.driver.set_curve(self.__current_state ["linear"], self.__current_state ["angular"]) # Turn at 0.5 speed.

        if (self.__current_state ["angle"]) - 15.0 < self.driver_gyro.getAngle() < (self.__current_state ["angle"] + 15.0):
            self.driver.set_curve(0, 0)
            self.next()

    @state(must_finish=True)
    def move(self, initial_call):
        if initial_call:
            self.driver.reset_drive_sensors()
        self.driver.set_curve(self.__current_state ["linear"], 0.0)

        if self.driver.current_distance >= self.__current_state ["displacement"]:
            self.driver.set_curve(0.0, 0.0)
            self.next()

    @timed_state(duration=5.0, must_finish=True, next_state="call_next")
    def shoot(self):
        # self.gripper.shoot()
        self.gripper.set_grip_state(grip_state=GripState.PUSH)

    @state
    def stop_shooting(self):
        self.gripper.set_grip_state(grip_state=GripState.STOP)
        self.next()

    @state
    def finish(self):
        # Reset states
        self.__current_state  = self.states[0]
        self.gen_instance = self.get_next_state()
