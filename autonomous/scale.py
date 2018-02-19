from autonomous import Auto

class Scale(Auto):
    def __init__(self, side):
        if side == "L":
            self.angle = 90
        elif side == "R":
            self.angle = -90
        
        self.states = [
            { "state": "lift", "position": "switch" },
            { "state": "move", "linear": 0.5, "displacement": 10000 },
            { "state": "lift", "position": "scale" },
            { "state": "turn", "linear": 0.0, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
            { "state": "shoot" },
            { "state": "turn", "linear": 0.0, "angular": self.angle/(-abs(self.angle) * 2), "angle": 0.0 },
            { "state": "finish" }
        ]

        super.__init__()