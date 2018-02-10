import magicbot
import wpilib


class Jessica(magicbot.MagicRobot):

    # Create motors and stuff here
    def createObjects(self):
        pass

    def robotInit(self):
        pass
    
    # Init: Called when mode starts; optional 
    # Periodic: Called on each iteration of the control loop
    def autonomousInit(self):
        pass
    
    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        pass
    
    def teleopPeriodic(self):
        pass

if __name__ is '__main__':
    wpilib.run(Jessica)