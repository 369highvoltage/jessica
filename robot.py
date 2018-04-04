from wpilib import run, Joystick, SmartDashboard
from components.driver import Driver, GearMode
from components.lifter import Lifter, MovementDir
from utilities import truncate_float, normalize_range
from components.gripper import Gripper, GripState, GripLiftState
from AsyncRobot import AsyncRobot
from CommandGroup import CommandGroup
from Command import Command, InstantCommand
from robot_map import RobotMap
from components.DriverComponent import DriverComponent
from components.DriverComponent.DriveCommands import DriveByTime, DriveByDistance, Turn, curve_drive
from components.LifterComponent.LifterCommands import move_lifter, MoveUp, MoveDown, move_down_instant, move_up_instant, Reset, MoveToPosition
from components.GripperComponent.GripperCommands import move_left_right, toggle_spread, SpitFast
from autonomous.switch_scale import switch_scale


class Jessica(AsyncRobot):

    def __init__(self):
        super().__init__()

    # Create motors and stuff here
    def robotInit(self):
        self.joystick = Joystick(1)

    def robotPeriodic(self):
        SmartDashboard.putNumber("driver/current_distance", RobotMap.driver_component.current_distance)
        SmartDashboard.putNumber("driver/left_encoder",
                                 RobotMap.driver_component.left_encoder_motor.getSelectedSensorPosition(0))
        SmartDashboard.putNumber("driver/right_encoder",
                                 RobotMap.driver_component.right_encoder_motor.getSelectedSensorPosition(0))
        SmartDashboard.putNumber("driver/gyro", RobotMap.driver_component.driver_gyro.getAngle())
        SmartDashboard.putNumber("lifter/current_position", RobotMap.lifter_component.current_position)
        SmartDashboard.putNumber("lifter/current_elevator_position", RobotMap.lifter_component.current_elevator_position)
        SmartDashboard.putNumber("lifter/current_carriage_position", RobotMap.lifter_component.current_carriage_position)

    def autonomousInit(self):
        # Insert decision tree logic here.
        game_data = self.ds.getGameSpecificMessage()
        switch_position = game_data[0]
        scale_position = game_data[1]
        start_position = "L"
        self.start_command(switch_scale(scale_position, switch_position, start_position))

        # auto = CommandGroup()
        # auto.add_sequential(Reset())
        # auto.add_sequential(MoveToPosition("portal"))
        # auto.add_sequential(SpitFast())
        # self.start_command(auto)

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.man_mode = False
    
    def teleopPeriodic(self):
        # if self.joystick.getRawButtonPressed(1):
        left_y = -self.joystick.getRawAxis(1)
        right_x = self.joystick.getRawAxis(2)
        self.start_command(curve_drive(left_y, right_x))

        l2 = -normalize_range(self.joystick.getRawAxis(3), -1, 1, 0, 1)
        r2 = normalize_range(self.joystick.getRawAxis(4), -1, 1, 0, 1)
        speed = r2 + l2
        if self.man_mode:
            self.start_command(move_lifter(speed))

        l1 = 5
        r1 = 6
        g_speed = 0.0
        if self.joystick.getRawButton(l1):
            g_speed += 1.0
        if self.joystick.getRawButton(r1):
            g_speed -= 1.0

        self.start_command(move_left_right(g_speed))

        triangle = 4
        if self.joystick.getRawButtonPressed(triangle):
            self.start_command(toggle_spread())

        square = 1
        x = 2
        if not self.man_mode:
            if self.joystick.getRawButtonPressed(square):
                self.start_command(move_up_instant())
            if self.joystick.getRawButtonPressed(x):
                self.start_command(move_down_instant())

        circle = 3
        if self.joystick.getRawButtonPressed(circle):
            self.man_mode = not self.man_mode

        options = 10
        if self.joystick.getRawButtonPressed(options):
            RobotMap.driver_component.reset_drive_sensors()

        share = 9
        if self.joystick.getRawButtonPressed(share):
            self.start_command(Reset())


if __name__ == '__main__':
    print("hello world")
    run(Jessica)
