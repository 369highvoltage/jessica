import asyncio
import threading

from concurrent.futures import ThreadPoolExecutor
from time import sleep

from feedback_controller import FeedbackController


class ControlSystem():
    __loop = asyncio.get_event_loop()
    
    # Global interrupt flag
    __interrupted = threading.Event()
    __pool: ThreadPoolExecutor

    @staticmethod
    def __init__(threads=5):
        ControlSystem.__pool = ThreadPoolExecutor(threads)

    @staticmethod
    def get_event_loop():
        return ControlSystem.__loop

    @staticmethod
    def create_controller(gains, period=0.05, num_samples=8) -> FeedbackController:
        """Thread factory function. Call this function inside components which require PID Control.

        Returns FeedbackController objects, which have callable public API functions.
        """
        controller = FeedbackController(ControlSystem.__interrupted, gains, period, num_samples)
        ControlSystem.__loop.run_until_complete(ControlSystem._spawn_thread(controller.execute))
        return controller

    @staticmethod
    def set_interrupt():
        """Call this from TimedRobot/robot.py's autonomous/teleopInit() to signal an interrupt to all commands.
        
        On interrupt, all asynchronous commands & threads will shutdown on the next iteration.
        """
        ControlSystem.__interrupted.set()

    @staticmethod
    def clear_interrupt():
        """Call this from TimedRobot/robot.py after calling set_interrupt() in autonomous/teleopInit functions.

        Allow some time to pass after set_interrupt() before calling this. Standard example:

        teleopInit()
            ControlSystem.set_interrupt()
            loop.call_later(0.4, ControlSystem.clear_interrupt)
        """
        ControlSystem.__interrupted.clear()

    @staticmethod
    async def _spawn_thread(handler):
        await asyncio.wait(ControlSystem.__loop.run_in_executor(ControlSystem.__pool, handler))
