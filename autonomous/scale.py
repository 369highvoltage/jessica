from components import drive
from robotpy_ext.autonomous import timed_state, StatefulAutonomous
import wpilib
from magicbot.magic_tunable import tunable

class Scale():
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
            { "state": "move", "linear": 0.5, "displacement": 10000 },
            { "state": "lift", "position": "scale" },
            { "state": "turn", "linear": 0.0, "angular": self.angle/(abs(self.angle) * 2), "angle": self.angle },
            { "state": "shoot" },
            { "state": "turn", "linear": 0.0, "angular": self.angle/(-abs(self.angle) * 2), "angle": 0.0 },
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
        lifter.lift_to("scale")
        self.next_state_now("turn")
    
    @state
    def turn(self, angle):
        driver.drive(0.0, angle/(abs(angle) * 2))

        if gyro.getAngle() == angle:
            self.next_state_now("forward")
            self.forward_next = "release"
    
    @state
    def move(self, displacement):
        driver.drive(0.5, 0.0)

        if driver.get_linear_displacement() >= displacement:
            self.next_state_now(forward_next)

    @state
    def shoot(self):
        shooter.shoot()
        self.next_state_now("turn")
    
    @state
    def finish():
        # Reset states
        self.current_state = self.states[0]