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
        # get current command and remove current if it is done
        cur_commands = None
        for commands in self._command_list:
            if len(commands) > 0:
                cur_commands = commands
                break
            self._command_list.remove(commands)
        # check if there are no more command lists, stop if there are no more
        if len(self._command_list) <= 0:
            self.finished()
            return
        # run all the commands in a command list, remove the ones that are complete
        for command in cur_commands:
            if command.is_done():
                cur_commands.remove(command)
                continue
            command.run()
