from autonomous.autonomous import Auto
from wpilib import DriverStation
from components.driver import GearMode, Driver
from magicbot.state_machine import state

class Scale(Auto):
    MODE_NAME = "Nothing"

    @state(first=True)
    def start(self):
        self.states = [
            { "state": "finish" }
        ]

        self.next(now=True)
