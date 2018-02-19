from components.lifter import Lifter
from robotpy_ext.autonomous import state, timed_state
import wpilib

class LevelSelector():
    lifter = Lifter

    def __init__(self, level):
        self.level = level
    
    @state(first=True)
    def lift(self):
        lifter.lift_to(self.level)
    