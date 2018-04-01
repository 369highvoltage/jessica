class CommandGroup():
    def __init__(self, events):
        self._command_list = []
        print("Default CommandGroup instructor - Overload me")
    
    def add_parallel(self, commands):
        """Takes in a list of commands."""
        self._command_list.append(commands)
        return self

    def add_sequential(self, command):
        """Takes in a single command."""
        self._command_list.append([command])
        return self

    def get_generator(self):
        return self._get_next_state()

    def _get_next_state(self):
        for commands in self._command_list:
            yield commands