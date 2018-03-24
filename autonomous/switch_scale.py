from autonomous.autonomous import Auto
from wpilib import DriverStation
from components.driver import GearMode, Driver
from magicbot.state_machine import state


class SwitchScale(Auto):
    DEFAULT = True
    MODE_NAME = "SwitchScale"

    @state(first=True)
    def start(self):
        angle = 0
        scale = False
        switch = False

        if self.scale_position == "L":
            if self.start_location == 1:
                angle = 90
                scale = True
            if self.start_location == 3:
                scale = False
                if self.switch_position == "L":
                    switch = False
                if self.switch_position == "R":
                    switch = True
                    angle = -90
        if self.scale_position == "R":
            if self.start_location == 1:
                scale = False
                if self.switch_position == "L":
                    switch = True
                    angle = 90
                if self.switch_position == "R":
                    switch = False
            if self.start_location == 3:
                scale = True
                angle = -90

        if self.start_location != 2:
            if scale:
                self.states = [
                    {"state": "lift", "position": "floor"},
                    {"state": "move", "linear": 0.25, "displacement": 192},  # 324
                    # {"state": "turn", "linear": 0.0, "angular": angle / (abs(angle) * 2), "angle": angle},
                    {"state": "move", "linear": 0.25, "displacement": -12},
                    {"state": "lift", "position": "scale_high"},
                    {"state": "shoot"},
                    {"state": "stop_shooting"},
                    # {"state": "turn", "linear": 0.0, "angular": angle / (-abs(angle) * 2), "angle": 0.0},
                    {"state": "finish"}
                ]
            elif switch:
                self.states = [
                    { "state": "lift", "position": "switch" },
                    { "state": "move", "linear": 0.5, "displacement": 168 },
                    { "state": "turn", "linear": 0.1, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
                    { "state": "move", "linear": 0.5, "displacement": 12 },
                    { "state": "shoot" },
                    {"state": "stop_shooting"},
                    { "state": "move", "linear": -0.5, "displacement": 12},
                    { "state": "turn", "linear": 0.1, "angular": self.angle/(-abs(self.angle) * 2), "angle": 0.0 },
                    { "state": "finish" }
                ]
            else:
                self.states = [
                    {"state": "move", "linear": 0.25, "displacement": 196},  # 324
                    {"state": "finish"}
                ]

        self.next(now=True)
