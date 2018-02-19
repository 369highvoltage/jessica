from autonomous import Auto

class MiddleSwitch(Auto):
    def __init__(self, side):
        if side == "L":
            self.angle = -90
            self.displacement = 5000 # Whatever initial distance is
        elif side == "R":
            self.angle = 90
            self.displacement = 3000
        
        self.states = [
            { "state": "lift", "position": "switch" },
            { "state": "turn", "linear": 0.1, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
            { "state": "move", "linear": 0.5, "displacement": self.displacement },
            { "state": "turn", "linear": 0.2, "angular": self.angle/(-abs(self.angle) * 2), "angle": -self.angle },
            { "state": "move", "linear": 0.5, "displacement": 1000 },
            { "state": "shoot" },
            { "state": "move", "linear": -0.1, "displacement": 1000},
            { "state": "turn", "linear": 0.0, "angular": self.angle/(abs(self.angle) * 2), "angle": 0.0 },
            { "state": "finish" }
        ]

        super.__init__()