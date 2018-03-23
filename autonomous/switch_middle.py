# from autonomous.autonomous import Auto
# from wpilib import DriverStation
#
# class MiddleSwitch(Auto):
#     MODE_NAME = "Middle_Switch"
#     def __init__(self):
#         side = self.ds.getGameSpecificMessage()[0]
#         if side == "L":
#             self.angle = -90
#             self.displacement = 168 # Whatever initial distance is
#         elif side == "R":
#             self.angle = 90
#             self.displacement = 168
#
#         self.states = [
#             { "state": "lift", "position": "scale_low" },
#             { "state": "turn", "linear": 0.1, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
#             { "state": "move", "linear": 0.5, "displacement": self.displacement },
#             { "state": "turn", "linear": 0.2, "angular": self.angle/(-abs(self.angle) * 2), "angle": -self.angle },
#             { "state": "move", "linear": 0.5, "displacement": 12 },
#             { "state": "shoot" },
#             {"state": "stop_shooting"},
#             { "state": "move", "linear": -0.5, "displacement": 12},
#             { "state": "turn", "linear": 0.0, "angular": self.angle/(abs(self.angle) * 2), "angle": 0.0 },
#             { "state": "finish" }
#         ]
#
#         super.__init__()