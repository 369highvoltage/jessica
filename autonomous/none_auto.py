from autonomous.autonomous import Auto
from wpilib import DriverStation
from components.driver import GearMode, Driver
from magicbot.state_machine import state

class Scale(Auto):
    DEFAULT = True
    MODE_NAME = "Nothing"

    def __init__(self):

        self.states = [
            { "state": "finish" }
        ]

        super().__init__()
