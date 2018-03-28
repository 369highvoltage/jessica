class Command():
    def __init__(self, events):
        self._spin = events["spin"]
        self._switch = events["switch_mode"]
        self._interrupted = events["interrupted"]
        self._done = False

    def is_done(self) -> bool:
        """Called externally from robot.py"""
        return self._done

    def _callback(self) -> None:
        print("Default execute() function - Overload me!")

    def _end(self) -> None:
        print("Default end() function - Overload me!")

    def _is_finished(self) -> bool:
        """Called internally by execute()"""
        print("Default is_finished() function - Overload me!")
    
    def _is_interrupted(self) -> bool:
        return self._interrupted.is_set()

    def start(self) -> None:
        # Setup objects here.
        print("Default start() function - Overload me!")

        self.execute()

    def execute(self) -> None:
        if self._is_finished() or self._is_interrupted():
            self._done = True
            self._end()
        else:
            self._callback()