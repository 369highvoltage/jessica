from wpilib import run, Joystick, SmartDashboard, CameraServer, SendableChooser
from utilities import truncate_float, normalize_range
from AsyncRobot import AsyncRobot
from CommandGroup import CommandGroup
from Command import Command, InstantCommand
from robot_map import RobotMap
from components.DriverComponent import DriverComponent
from components.DriverComponent.DriveCommands import DriveByTime, DriveByDistance, Turn, curve_drive, toggle_gear
# from components.LifterComponent.LifterCommands import move_lifter, MoveUp, MoveDown, move_down_instant, move_up_instant, Reset, MoveToPosition, move_to_position_instant, lock_carriage_move_elevator
from components.GripperComponent.GripperCommands import move_left_right, toggle_spread, SpitFast, LiftTo, Toggle
from autonomous.switch_scale import switch_scale, drive_straight
from components.ClimbComponent.ClimbCommands import climb, stop


class Jessica(AsyncRobot):

    def __init__(self):
        super().__init__()

    # Create motors and stuff here
    def robotInit(self):
        self.controller = Joystick(0)
        self.joystick = Joystick(1)
        CameraServer.launch('vision.py:main')

        self.autoChooser = SendableChooser()

        self.autoChooser.addDefault("switch_scale", switch_scale)
        # self.autoChooser.addObject("drive_forward", drive_straight)
        SmartDashboard.putData("Autonomous Mode Chooser", self.autoChooser)

        self.autoSideChooser = SendableChooser()

        self.autoSideChooser.addDefault("left", "L")
        self.autoSideChooser.addObject("right", "R")
        self.autoSideChooser.addObject("middle", "M")
        SmartDashboard.putData("Side Chooser", self.autoSideChooser)

    def robotPeriodic(self):
        SmartDashboard.putNumber("driver/current_distance", RobotMap.driver_component.current_distance)
        SmartDashboard.putNumber("driver/left_encoder",
                                 RobotMap.driver_component.left_encoder_motor.getSelectedSensorPosition(0))
        SmartDashboard.putNumber("driver/right_encoder",
                                 RobotMap.driver_component.right_encoder_motor.getSelectedSensorPosition(0))
        SmartDashboard.putNumber("driver/gyro", RobotMap.driver_component.driver_gyro.getAngle())

        if RobotMap.driver_component.back_distance_sensor.isRangeValid():
            SmartDashboard.putNumber("driver/back_distance_sensor", RobotMap.driver_component.back_distance_sensor.getRangeInches())
        
        vision_width = SmartDashboard.getNumber("vision/vision_width", 0)
        vision = SmartDashboard.getNumber("vision/vision_pid", 0)
        vision_min = -(vision_width / 2)
        vision_max = vision_width / 2
        
        clamped_vision = normalize_range(vision, vision_min, vision_max, -1, 1)
        SmartDashboard.putNumber("vision/vision_percent", clamped_vision)
        """
        SmartDashboard.putNumber("lifter/current_position", RobotMap.lifter_component.current_position)
        SmartDashboard.putNumber("lifter/current_elevator_position", RobotMap.lifter_component.current_elevator_position)
        SmartDashboard.putNumber("lifter/current_carriage_position", RobotMap.lifter_component.current_carriage_position)
        SmartDashboard.putBoolean("lifter/carriage_top_switch", RobotMap.lifter_component.carriage_top_switch.get())
        SmartDashboard.putBoolean("lifter/carriage_bottom_switch", RobotMap.lifter_component.carriage_bottom_switch.get())
        SmartDashboard.putBoolean("lifter/elevator_bottom_switch", RobotMap.lifter_component.elevator_bottom_switch.get())
        SmartDashboard.putNumber("gripper/gripper_pot", RobotMap.gripper_component.pot.get())
        """


    def autonomousInit(self):
        # Insert decision tree logic here.
        game_data = self.ds.getGameSpecificMessage()
        switch_position = game_data[0]
        scale_position = game_data[1]
        start_position = self.autoSideChooser.getSelected()
        aut = self.autoChooser.getSelected()
        self.start_command(aut(scale_position, switch_position, start_position))
        # self.start_command(Turn(45, 1))

    def disabledInit(self):
        RobotMap.driver_component.moving_angular.clear()
        RobotMap.driver_component.moving_linear.clear()

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        self.man_mode = False
        self.climb_mode = False
        # self.start_command(Reset())
    
    def teleopPeriodic(self):
        # if self.joystick.getRawButtonPressed(1):

        # p1
        left_y = -self.controller.getRawAxis(1)
        right_x = self.controller.getRawAxis(2)
        self.start_command(curve_drive(left_y, right_x))
        if self.controller.getRawButtonPressed(3):
            self.start_command(Toggle())
        if self.controller.getRawButtonPressed(14):
            RobotMap.driver_component.toggle_gear()
            # self.start_command(toggle_gear())
        if self.controller.getRawButtonPressed(5):
            RobotMap.driver_component.set_low_gear()
        if self.controller.getRawButtonPressed(6):
            RobotMap.driver_component.set_high_gear()
        
        
        
        # cube_left = 
        """
        # vision = SmartDashboard.getNumber("vision", 0)
        # vision_min = SmartDashboard.getNumber("vision_min", 0)
        # vision_max = SmartDashboard.getNumber("vision_max", 0)
        # clamped_vision = normalize_range(vision, vision_min, vision_max, -1, 1)
        # left_vision = max(1 - abs(min(clamped_vision, 0)), 0)

        # right_vision = abs(max(clamped_vision, 0))
        # clamped_vision = min(max(vision, -1), 1)
        # left_vision = 1 - abs(clamped_vision)
        # right_vision = abs(clamped_vision)

        # if not (vision_min == 0 and vision_max == 0):
        #     self.controller.setRumble(Joystick.RumbleType.kLeftRumble, clamped_vision)
        #     self.controller.setRumble(Joystick.RumbleType.kRightRumble, clamped_vision)

        # p2
        # l2 = -normalize_range(self.joystick.getRawAxis(3), -1, 1, 0, 1)
        # r2 = normalize_range(self.joystick.getRawAxis(4), -1, 1, 0, 1)
        # speed = r2 + l2
        # if self.man_mode:
        #     self.start_command(move_lifter(speed))


        right_y = -self.joystick.getRawAxis(5)
        #up
        if not self.climb_mode:
            if self.joystick.getPOV() == 0:
                self.start_command(move_lifter(1))
                self.man_mode = True
            elif self.joystick.getPOV() == 180:
                self.start_command(move_lifter(-1))
                self.man_mode = True
            elif self.man_mode:
                self.start_command(move_lifter(0))
        else:
            if self.joystick.getPOV() == 0:
                self.start_command(lock_carriage_move_elevator(1))
                self.man_mode = True
            elif self.joystick.getPOV() == 180:
                self.start_command(lock_carriage_move_elevator(right_y))
                self.man_mode = True
            elif self.man_mode:
                self.start_command(lock_carriage_move_elevator(right_y))


        l1 = 5
        r1 = 6
        square = 1
        x = 2
        circle = 3
        triangle = 4
        touchpad = 14

        if self.joystick.getRawButtonPressed(touchpad):
            self.climb_mode = not self.climb_mode
            if self.climb_mode:
                self.man_mode = True
                self.start_command(LiftTo("up"))

        if self.joystick.getRawButton(7) and self.climb_mode:
            self.start_command(climb())

        if not self.joystick.getRawButton(7) and self.climb_mode:
            self.start_command(stop())

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

        if self.joystick.getRawButtonPressed(r1) and not self.climb_mode:
            self.start_command(move_to_position_instant("scale_high"))
            self.man_mode = False
        if self.joystick.getRawButtonPressed(l1) and not self.climb_mode:
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
        if self.joystick.getRawButton(8):
            self.start_command(LiftTo("up"))
        """


if __name__ == '__main__':
    print("hello world")
    run(Jessica)
