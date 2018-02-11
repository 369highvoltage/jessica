import wpilib

"""
    Class Lifter (extends Elevator)
"""
class Climber(Elevator):
    def __init__(self, pin):
        Elevator.__init__(pin)
        self.positions = {
            "top": 500,
            "bottom": 1500
        }


    def move(self, value):
        motor.set(ControlMode.Position, value)

    def ascend(self):
        self.move(self.positions["top"])
    
    def descend(self):
        self.move(self.positions["bottom"])