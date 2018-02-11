from wpilib.drive import DifferentialDrive

class Driver:
    left_motor = Talon()
    right_motor = Talon()
    drivetrain = DifferentialDrive(left_motor, right_motor)

    def __init__(self):
        # Components
        pass
        
    def drive(self, linear, angular):
        if -0.1 < linear < 0.1:
            drivetrain.curvatureDrive(linear, angular, True)
        else:
            drivetrain.curvatureDrive(linear, angular, False)
    
    def get_linear_displacement(self):
        return (right_motor.getSelectedSensorVelocity(0) + left_motor.getSelectedSensorVelocity(0))/2
    
    def get_strafing_displacement(self):
        return right_motor.getSelectedSensorVelocity(0) - left_motor.getSelectedSensorVelocity()
