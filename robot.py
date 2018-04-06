from wpilib import run, Joystick, SmartDashboard, CameraServer
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
from components.LifterComponent.LifterCommands import move_lifter, MoveUp, MoveDown, move_down_instant, move_up_instant, Reset, MoveToPosition, move_to_position_instant
from components.GripperComponent.GripperCommands import move_left_right, toggle_spread, SpitFast
from autonomous.switch_scale import switch_scale


class Jessica(AsyncRobot):

    def __init__(self):
        super().__init__()

    # Create motors and stuff here
    def robotInit(self):
        self.controller = Joystick(0)
        self.joystick = Joystick(1)
        CameraServer.launch()

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
        SmartDashboard.putBoolean("lifter/carriage_top_switch", RobotMap.lifter_component.carriage_top_switch.get())

    def autonomousInit(self):
        # Insert decision tree logic here.
        game_data = self.ds.getGameSpecificMessage()
        switch_position = game_data[0]
        scale_position = game_data[1]
        start_position = "M"
        self.start_command(switch_scale(scale_position, switch_position, start_position))
        # self.start_command(DriveByDistance(168, 0.25))
        # auto = CommandGroup()
        # auto.add_sequential(Reset())
        # auto.add_sequential(MoveToPosition("portal"))
        # auto.add_sequential(SpitFast())
        # self.start_command(auto)

    def disabledInit(self):
        RobotMap.driver_component.moving_angular.clear()
        RobotMap.driver_component.moving_linear.clear()

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.man_mode = False
        # self.start_command(Reset())
    
    def teleopPeriodic(self):
        # if self.joystick.getRawButtonPressed(1):

        # p1
        left_y = -self.controller.getRawAxis(1)
        right_x = self.controller.getRawAxis(2)
        self.start_command(curve_drive(left_y, right_x))


        # p2
        # l2 = -normalize_range(self.joystick.getRawAxis(3), -1, 1, 0, 1)
        # r2 = normalize_range(self.joystick.getRawAxis(4), -1, 1, 0, 1)
        # speed = r2 + l2
        # if self.man_mode:
        #     self.start_command(move_lifter(speed))

        #up
        if self.joystick.getPOV() == 0:
            self.start_command(move_lifter(1))
            self.man_mode = True
        elif self.joystick.getPOV() == 180:
            self.start_command(move_lifter(-1))
            self.man_mode = True
        elif self.man_mode:
            self.start_command(move_lifter(0))


        l1 = 5
        r1 = 6
        square = 1
        x = 2
        circle = 3
        triangle = 4
        touchpad = 14

        g_speed = 0.0
        if self.joystick.getRawButton(square):
            g_speed = -1.0
        if self.joystick.getRawButton(x):
            g_speed = 1.0

        if self.joystick.getRawButton(circle):
            g_speed = -0.50

        self.start_command(move_left_right(g_speed))

        if self.joystick.getRawButtonPressed(triangle):
            self.start_command(toggle_spread())

        if self.joystick.getRawButtonPressed(r1):
            self.start_command(move_to_position_instant("scale_high"))
            self.man_mode = False
        if self.joystick.getRawButtonPressed(l1):
            self.start_command(move_to_position_instant("floor"))
            self.man_mode = False

        # if self.joystick.getRawButtonPressed(touchpad):
        #     self.man_mode = not self.man_mode

        options = 10
        if self.joystick.getRawButtonPressed(options):
            RobotMap.driver_component.reset_drive_sensors()

        share = 9
        if self.joystick.getRawButtonPressed(share):
            self.start_command(Reset())


if __name__ == '__main__':
    print("hello world")
    run(Jessica)
