import asyncio
import threading

from concurrent.futures import ThreadPoolExecutor
from time import sleep

from feedback_controller import FeedbackController

class ControlSystem():
    __loop = asyncio.get_event_loop()
    
    # Global interrupt flag
    __interrupted = threading.Event()

    def __init__(self, threads=5):
        self._pool = ThreadPoolExecutor(threads)
    
    def get_event_loop(self):
        return self.__loop

    def create_controller(self, gains, options) -> FeedbackController:
        """Thread factory function. Call this function inside components which require PID Control.

        Returns FeedbackController objects, which have callable public API functions.
        """
        controller = FeedbackController(self.__interrupted, gains, options)
        self.__loop.run_until_complete(self._spawn_thread(controller.execute))
        return controller
    
    def set_interrupt(self):
        """Call this from TimedRobot/robot.py's autonomous/teleopInit() to signal an interrupt to all commands.
        
        On interrupt, all asynchronous commands & threads will shutdown on the next iteration.
        """
        self.__interrupted.set()
    
    def clear_interrupt(self):
        """Call this from TimedRobot/robot.py after calling set_interrupt() in autonomous/teleopInit functions.

        Allow some time to pass after set_interrupt() before calling this. Standard example:

        teleopInit()
            ControlSystem.set_interrupt()
            loop.call_later(0.4, ControlSystem.clear_interrupt)
        """
        self.__interrupted.clear()
    
    async def _spawn_thread(self, handler):
        await asyncio.wait(self.__loop.run_in_executor(self._pool, handler))
