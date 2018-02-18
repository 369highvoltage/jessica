from components import drive
from robotpy_ext.autonomous import timed_state, StatefulAutonomous
import wpilib
from magicbot.magic_tunable import tunable

class MiddleSwitch():
    driver = Driver
    gyro = Gyro
    lifter = Lifter
    shooter = Shooter

    def __init__(self, side):
        if side == "L":
            self.angle = 90
        elif side == "R":
            self.angle = -90
        
        self.states = [
            { "state": "lift", "position": "switch" },
            { "state": "move", "linear": 0.5, "displacement": 5000 },
            { "state": "turn", "linear": 0.1, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
            { "state": "move", "linear": 0.1, "displacement": 1000 },
            { "state": "shoot" },
            { "state": "move", "linear": -0.1, "displacement": 1000},
            { "state": "turn", "linear": 0.1, "angular": self.angle/(-abs(self.angle) * 2), "angle": 0.0 },
            { "state": "finish" }
        ]

        self.current_state = {}
    
    # Generator which moves to the next state when ready.
    def get_next_state():
        for state in self.states:
            yield state
    
    # Call next() in each state, ala Express.js
    def next(now=False):
        self.current_state = self.get_next_state()
        if now:
            self.next_state_now(self.current_state["state"])
        else:
            self.next_state(self.current_state["state"])

    @state(first=True)
    def start(self):
        self.next(now=True)
    
    @state
    def lift(self):
        lifter.lift_to(self.current_state["position"])
        self.next(now=True)
    
    @state
    def turn(self):
        driver.drive(self.current_state["linear"], self.current_state["angular"]) # Turn at 0.5 speed.
        
        if (self.current_state["angle"]) - 1.0 < gyro.getAngle() < (self.current_state["angle"] + 1.0):
            self.next()
    
    @state
    def move(self):
        driver.drive(self.current_state["linear"], 0.0)

        if driver.current_distance() >= displacement:
            self.next()

    @timed_state(duration=0.25, must_finish=True)
    def shoot(self):
        shooter.shoot()
        self.next()

    @state
    def finish():
        # Reset states
        self.current_state = self.states[0]