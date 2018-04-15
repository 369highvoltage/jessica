from typing import Callable
from Events import Events


class Command(Events):
    class EVENTS:
        on_start = "on_start"
        on_end = "on_end"
        on_execute = "on_execute"
        on_interrupted = "on_interrupted"

    def __init__(self):
        Events.__init__()
        self._done = False
        self._first = True
        self._interupted = False
        self._create_events([
            Command.EVENTS.on_start,
            Command.EVENTS.on_end,
            Command.EVENTS.on_execute,
            Command.EVENTS.on_interrupted
        ])
        # call start
        self.add_listeners(Command.EVENTS.on_start, lambda: self.__on_start())
        self.add_listeners(Command.EVENTS.on_end, lambda: self.__on_end())
        self.add_listener(Command.EVENTS.on_execute, lambda: self.__on_execute())
        self.add_listener(Command.EVENTS.on_interrupted, lambda: self.__on_interrupted())

    def __on_start(self):
        self.on_start()
        self._first = False

    def __on_execute(self):
        self.execute()

    def __on_end(self):
        self.on_end()
        self._done = True

    def __on_interrupted(self):
        self.on_interrupted()
        self._interupted = True
        self.finished()

    def interrupt(self):
        self.trigger_event(Command.EVENTS.on_interrupted)

    def run(self) -> None:
        if self._first:
            self.trigger_event(Command.EVENTS.on_start)
        elif not self._done:
            self.trigger_event(Command.EVENTS.on_execute)

    def is_done(self) -> bool:
        return self._done

    def finished(self) -> None:
        self.trigger_event(Command.EVENTS.on_end)

    # These methods should be implemented by command creator

    def on_start(self) -> None:
        print("Default on_start() function - Overload me!")

    def on_end(self) -> None:
        print("Default on_end() function - Overload me!")

    def execute(self) -> None:
        print("Default execute() function - Overload me!")

    def on_interrupted(self) -> None:
        print("Default on_interupted() function - Overload me!")


class InstantCommand(Command):
    def __init__(self, method: Callable):
        super().__init__()
        self._instant_method = method

    def on_start(self):
        self._instant_method()
        self.finished()

    def on_end(self):
        pass

    def execute(self):
        pass