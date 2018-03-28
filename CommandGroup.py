class CommandGroup():
    def __init__(self, events):
        self._command_list = []
        self._generator = self._get_next_state()
        print("Default CommandGroup instructor - Overload me")
    
    def _get_next_state(self):
        for commands in self._command_list:
            yield commands

    def next(self):
        """Generator Wrapper"""
        return next(self._generator)