class Command():
    def __init__(self, events):
        self._spin = events["spin"]
        self._switch = events["switch_mode"]
        self._interrupted = events["interrupted"]
        self._done = False
        self._start()
    
    def enable(self):
        self._spin.set()

    def is_done(self) -> bool:
        """Called externally from robot.py"""
        return self._done

    def _callback(self):
        print("Default execute() function - Overload me!")

    def _end(self):
        self._done = True
        print("Default end() function - Overload me!")

    def _is_finished(self) -> bool:
        """Called internally by spin()"""
        print("Default is_finished() function - Overload me!")
    
    def _start(self):
        print("Default start() function - Overload me!")

    async def execute(self):
        if self._is_finished() or self._interrupted.is_set():
            self._end()
        else:
            self._callback()
        