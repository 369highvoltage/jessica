from Command import Command
from typing import List


class CommandGroup(Command):
    _command_list: List[List[Command]]

    def __init__(self):
        super().__init__()
        self._command_list = []

    def add_parallel(self, commands: List[Command]):
        """Takes in a list of commands."""
        self._command_list.append(commands)
        return self

    def add_sequential(self, command: Command):
        """Takes in a single command."""
        self._command_list.append([command])
        return self

    def execute(self) -> None:
        # Filter out finished commands first.
        commands = [commands for commands in self._command_list[0] if not commands.is_done()]

        # First check if entire command list is exhausted.
        # Then check if the current commands are finished.
        # Otherwise run remaining commands.
        if len(self._command_list <= 0):
            self.finished()
            return
        elif len(commands) <= 0:
            del self._command_list[0]
        else:
            self._command_list[0] = commands
            
            # Command may finish, but it should be gone in the next iteration of execute().
            for command in commands:
                command.run()
            


    def on_end(self):
        pass

    def on_start(self):
        pass
