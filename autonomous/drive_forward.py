from autonomous.autonomous import Auto
from wpilib import DriverStation
from components.driver import GearMode, Driver
from magicbot.state_machine import state

class Scale(Auto):
    MODE_NAME = "Drive_Froward"

    @state(first=True)
    def start(self):
        self.states = [
            {"state": "move", "linear": 0.25, "displacement": 196},  # 324
            {"state": "finish"}
        ]

        self.next(now=True)