import inspect
import datetime


class CommandHandler(object):
    """A class to handle an arbitrary list of commands for embedded CLIs."""

    def __init__(self, commands=[]):
        """
        command_list stores a dictionary of all possible commands

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
        self.command_list = {}
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
        Parse arguments into dictionary or list.

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

    def _validate_args(self, command_name, args):
        """
        Assert that the correct number of arguments are provided.

        If arg_dict is True, also assert that all required arguments
        are provided and no extraneous arguments are provided.

        :param command_name: string literal that corresponds to command in self.command_list
        :param args: list or dictionary containing arguments
        :return:
        """
        command_args_metadata = self.command_list[command_name]['metadata']['args']
        min_args = len(command_args_metadata['required'])
        max_args = min_args + len(command_args_metadata['default'])
        if len(args) < min_args or len(args) > max_args:
            raise RuntimeError('Missing Required Argument')

        if self.ch_format['arg_dict']:
            # Check if args does not contain all required arguments
            for a in command_args_metadata['required']:
                if a not in args:
                    raise RuntimeError('Missing Required Argument')
            # Check if args contains an extraneous argument
            for a in args:
                if a not in command_args_metadata['required'] and a not in command_args_metadata['required']:
                    raise RuntimeError('Unrecognized Argument')


    def get_command_metadata(self, command_name):
        """
        Get the metadata for a command in the form of a dictionary.

        :param command_name: string literal that corresponds to command in self.command_list
        :return: dictionary in metadata format
        """
        command = self.command_list[command_name]['function']
        command_signature = inspect.signature(command)
        command_args = dict(required=[], default=[])
        for param in command_signature.parameters.values():
            if param.default is param.empty:
                command_args['required'].append(param.name)
            else:
                command_args['default'].append(param.name)
        command_metadata = dict(args=command_args)
        return command_metadata

    def add_commands(self, commands):
        """
        Add a dictionary of commands to the command_list.

        :param commands: list of dictionaries - <command name>: <function>
        :return:
        """
        for command in commands:
            command_name = [key for key in command][0]
            self.command_list[command_name] = dict(function=command[command_name])
            command_metadata = self.get_command_metadata(command_name)
            self.command_list[command_name]['metadata'] = command_metadata

    def handle_command(self, command_text):
        """
        Parse command_text and calls execute_command.

        :param command_text: string literal to be parsed into command_text and args
        :return:
        """
        command_text = [s for s in command_text.split(self.ch_format['command_arg_splitter']) if s != '']
        command_name = command_text[0]
        command_args = command_text[1] if len(command_text) > 1 else None

        try:
            if command_name not in self.command_list:
                raise RuntimeError('Unknown Command')
            if command_args is None and len(self.command_list[command_text[0]]['metadata']['args']['required']) != 0:
                raise RuntimeError('Command Requires Arguments')

            command_args = self._parse_args(command_args) if command_args else None
            self._validate_args(command_name, command_args)

        except RuntimeError as e:
            return e

        return self.execute_command(command_name, command_args)

    def execute_command(self, command_name, args):
        """
        Call the function corresponding to the command_name from command_list with args.

        :param command_name: string literal that corresponds to command in self.command_list
        :param args: list or dictionary containing arguments
        :return:
        """
        if args:
            if self.ch_format['arg_dict']:
                result = self.command_list[command_name]['function'](**args)
            else:
                result = self.command_list[command_name]['function'](*args)
        else:
            result = self.command_list[command_name]['function']()

        if result:
            timestamp = datetime.datetime.utcnow()
            history_entry = dict(timestamp=timestamp,
                                 args=args,
                                 command=command_name,
                                 ch_format=self.ch_format,
                                 result=result)
            self.invocation_history.append(history_entry)
            return result
