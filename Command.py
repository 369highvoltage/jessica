from typing import Callable


class Command:
    def __init__(self):
        self._done = False
        self._first = True
        self._ending = False

    def run(self) -> None:
        if self._first:
            self.on_start()
            self._first = False
        elif self._ending:
            self.on_end()
            self._done = True
        else:
            self.execute()

    def is_done(self) -> bool:
        return self._done

    def finished(self) -> None:
        self._ending = True

    # These methods should be implemented by command creator

    def on_start(self) -> None:
        print("Default on_start() function - Overload me!")

    def on_end(self) -> None:
        print("Default on_end() function - Overload me!")

    def execute(self) -> None:
        print("Default execute() function - Overload me!")


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