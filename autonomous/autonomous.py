from abc import ABC, abstractmethod
from components import Driver, Gyro, Lifter, Shooter
from robotpy_ext.autonomous import state, timed_state
import wpilib

class Auto(ABC):
    driver = Driver
    gyro = Gyro
    lifter = Lifter
    shooter = Shooter

    @abstractmethod
    def __init__(self):
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

