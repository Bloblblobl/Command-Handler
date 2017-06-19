import datetime
from command import Command


class CommandHandler(object):
    """A class to handle an arbitrary list of commands for embedded CLIs."""

    def __init__(self, commands=None):
        """
        command_list is a dictionary of Command objects

        ch_format is a dictionary of configuration settings for the CommandHandler
            --> If arg_dict is True, commands will be processed like a dictionary:
                    <command name>|<arg1 name>=<arg1 value> <arg2 name>=<arg2 value>
                Otherwise, commands will be processed like a dictionary:
                    <command name>|<arg1 value>, <arg2 value>, <arg3 value>
            --> command_arg_splitter is the character the CommandHandler will look for
                between the command and the arguments.
            --> arg_value_splitter is the character the CommandHandler will look for
                between the argument names and their values when arg_dict is True.
            --> dict_arg_splitter is the character the CommandHandler will look for
                between the argument-value pairs when arg_dict is True.
            --> list_arg_splitter is the character the CommandHandler will look for
                between the arguments when arg_dict is False.

        :param commands: list of dictionaries - <command name>: {function: <function>, metadata: <metadata>}
        """
        self.commands = {}
        if commands:
            self.add_commands(commands)

        self.ch_format = dict(arg_dict=True,
                         command_arg_splitter='|',
                         arg_value_splitter='=',
                         dict_arg_splitter=' ',
                         list_arg_splitter=',')
        self.invocation_history = []

    def _parse_args(self, command_args):
        """
        Parse arguments into a dictionary or list.

        :param command_args:
        :return:
        """
        if self.ch_format['arg_dict']:
            args_list = [a for a in command_args.split(self.ch_format['dict_arg_splitter']) if a]
            command_args = {}

            for kvpair in args_list:
                kvpair = [a for a in kvpair.split(self.ch_format['arg_value_splitter']) if a]
                arg_key, arg_value = kvpair[0], kvpair[1] if len(kvpair) > 1 else None
                if not arg_value:
                    raise RuntimeError('Incorrect Argument Format')
                command_args[arg_key] = arg_value
        else:
            command_args = [a for a in command_args.split(self.ch_format['list_arg_splitter']) if a]
        return command_args

    def add_commands(self, commands):
        """
        Add commands to the command_dict.

        :param commands: list of tuples of command names and function - [[<command names>], <function>]
        :return:
        """
        for command in commands:
            command_names, command_func = command[0], command[1]
            self.commands[command_names] = Command(command_names, command_func)

    def handle_command(self, command_text):
        """
        Parse command_text and call execute_command.

        :param command_text: string to be parsed into command_text and args
        :return:
        """
        command_text = [s for s in command_text.split(self.ch_format['command_arg_splitter']) if s != '']
        command_name = command_text[0]
        command_args = command_text[1] if len(command_text) > 1 else None

        command = None
        for command_pair in self.commands:
            if command_name in command_pair[0]:
                command = command_pair[1]
        if command is None:
            raise RuntimeError('Unknown Command')

        command_args = self._parse_args(command_args) if command_args else None

        return self.execute_command(command, command_args, command_name)

    def execute_command(self, command, args, name):
        """
        Call the function corresponding to the command_name from command_dict with args.

        :param command_name: string that corresponds to command in self.commands
        :param args: list or dictionary containing arguments
        :return:
        """

        result = command.invoke(args)

        timestamp = datetime.datetime.utcnow()
        history_entry = dict(timestamp=timestamp,
                             args=args,
                             command=command.names[0],
                             ch_format=self.ch_format,
                             result=result)
        if name != command.names[0]:
            history_entry['synonym'] = name
        self.invocation_history.append(history_entry)
        return result
