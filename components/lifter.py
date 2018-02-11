import wpilib

"""
    Class Lifter (extends Elevator)
"""
class Lifter(Elevator):
    def __init__(self, pin):
        Elevator.__init__(pin)
        self.positions = [
            { "name": "floor", "distance": 500 },
            { "name": "switch", "distance": 1500 },
            { "name": "scale", "distance": 5000 },
            { "name": "bar", "distance": 6000 }
        ]
        self.currentPosition = positions[0]
    
    """ For direct analog joystick control """
    def move(self, value):
        motor.set(ControlMode.Position, value)
    
    
    """ For autonomous usage. Pass in a string to set the level. """
    def lift_to(self, level):
        pos  = (dist for position in positions if position["name"] == level).next()
        self.currentPosition = positions.index(pos)
        self.move(pos["distance"])
    
    """ For DPad button control """
    def lift_up_one(self):
        if self.currentPosition < len(positions):
            self.currentPosition += 1
            self.move(positions[self.currentPosition]["distance"])
    
    def lift_down_one(self):
        if self.currentPosition > 0:
            self.currentPosition -= 1
            self.move(positions[self.currentPosition]["distance"])