from autonomous.autonomous import Auto
from wpilib import DriverStation
from components.driver import GearMode, Driver
from magicbot.state_machine import state

class Scale(Auto):
    DEFAULT = True
    MODE_NAME = "Scale"

    def __init__(self):
        # super().__init__()
        # DriverStation.getLocation()

        side = "L"
        if side == "L":
            self.angle = 90
        elif side == "R":
            self.angle = -90

        self.states = [
            { "state": "lift", "position": "portal" },
            { "state": "move", "linear": 0.25, "displacement": 60 },  # 324
            { "state": "turn", "linear": 0.0, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
            {"state": "move", "linear": 0.25, "displacement": -12},
            {"state": "lift", "position": "scale_mid"},
            { "state": "shoot" },
            {"state": "stop_shooting"},
            { "state": "turn", "linear": 0.0, "angular": self.angle/(-abs(self.angle) * 2), "angle": 0.0 },
            { "state": "finish" }
        ]

        super().__init__()

class Switch(Auto):
    MODE_NAME = "Switch"

    def __init__(self):
        # super().__init__()
        # DriverStation.getLocation()

        side = "L"
        if side == "L":
            self.angle = 90
        elif side == "R":
            self.angle = -90

        self.states = [
            { "state": "lift", "position": "portal" },
            { "state": "move", "linear": 0.25, "displacement": 168 },
            { "state": "turn", "linear": 0.0, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
            {"state": "lift", "position": "scale_low"},
            { "state": "shoot" },
            {"state": "stop_shooting"},
            { "state": "turn", "linear": 0.0, "angular": self.angle/(-abs(self.angle) * 2), "angle": 0.0 },
            { "state": "finish" }
        ]

        super().__init__()