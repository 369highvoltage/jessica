# validated: 2018-02-09 DS 5ca00dddbeff edu/wpi/first/wpilibj/TimedRobot.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import asyncio
import hal
import logging

from wpilib.livewindow import LiveWindow
from wpilib.smartdashboard import SmartDashboard
from wpilib.iterativerobotbase import IterativeRobotBase
from wpilib.notifier import Notifier
from wpilib.resource import Resource
from wpilib.robotcontroller import RobotController
from wpilib.timer import Timer
from Command import Command

__all__ = ["AsyncRobot"]


class AsyncRobot(IterativeRobotBase):
    """AsyncRobot implements the IterativeRobotBase robot program framework.

    The AsyncRobot class is intended to be subclassed by a user creating a robot program.

    The asyncio Event loop schedules loopFunc() and periodic()
    functions, instead of being run directly.
    """
    DEFAULT_PERIOD = .02
    logger = logging.getLogger("robot")

    def __init__(self):
        super().__init__()
        hal.report(hal.UsageReporting.kResourceType_Framework, hal.UsageReporting.kFramework_Iterative)

        self._loop = asyncio.get_event_loop()
        self._active_commands = []

    def startCompetition(self) -> None:
        """Provide an alternate "main loop" via startCompetition()"""
        self.robotInit()
        hal.observeUserProgramStarting()

        # Loop forever, calling the appropriate mode-dependent function
        self._loop.run_until_complete(self._run_robot())

    def getEventLoop(self):
        """Use this function to access the event loop in robot.py"""
        return self._loop

    async def _run_robot(self):
        while True:
            self.loopFunc()
            await asyncio.sleep(AsyncRobot.DEFAULT_PERIOD)

    def _run_commands(self):
        for command in self._active_commands:
            # check if the command is done, if so then remove it from queue
            if command.is_done():
                self._active_commands.remove(command)
                continue
            # command.run()
            self._loop.call_soon(command.run)

    def _flush_commands(self):
        # self._loop.
        for command in self._active_commands:
            command.finished()
        self._active_commands.clear()

    def start_command(self, command: Command):
        self._active_commands.append(command)

    # Overriden function from IterativeRobotBase
    def loopFunc(self):
        """This version of loopFunc passes the event loop to all init() and periodic() functions."""
        if self.isDisabled():
            if self.last_mode is not self.Mode.kDisabled:
                LiveWindow.setEnabled(False)
                self._flush_commands()
                self.disabledInit()
                self.last_mode = self.Mode.kDisabled
            hal.observeUserProgramDisabled()
            self.disabledPeriodic()
        elif self.isAutonomous():
            if self.last_mode is not self.Mode.kAutonomous:
                LiveWindow.setEnabled(False)
                self._flush_commands()
                self.autonomousInit()
                self.last_mode = self.Mode.kAutonomous
            hal.observeUserProgramAutonomous()
            self.autonomousPeriodic()
        elif self.isOperatorControl():
            if self.last_mode is not self.Mode.kTeleop:
                LiveWindow.setEnabled(False)
                self._flush_commands()
                self.teleopInit()
                self.last_mode = self.Mode.kTeleop
            hal.observeUserProgramTeleop()
            self.teleopPeriodic()
        else:
            if self.last_mode is not self.Mode.kTest:
                LiveWindow.setEnabled(True)
                self._flush_commands()
                self.testInit()
                self.last_mode = self.Mode.kTest
            hal.observeUserProgramTest()
            self.testPeriodic()
        self.robotPeriodic()
        self._run_commands()
        SmartDashboard.updateValues()
        LiveWindow.updateValues()