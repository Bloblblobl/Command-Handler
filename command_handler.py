import inspect
import datetime


class CommandHandler(object):
    """
    A class to handle an arbitrary list of commands for embedded CLIs.

    command_list stores a dictionary of all possible commands:
        <command name>: {function: <function>, metadata: <metadata>}

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
    """
    def __init__(self, commands):
        command_list = {}
        if commands:
            self.add_commands(commands)

        ch_format = dict(arg_dict=True,
                         command_arg_splitter='|',
                         arg_value_splitter='=',
                         dict_arg_splitter=' ',
                         list_arg_splitter=',')
        invocation_history = []

    def _check_args(self, command_name, args):
        """
        Assert that the correct number of arguments are provided.

        If arg_dict is True, also assert that all required arguments
        are provided and no extraneous arguments are provided.
        """
        command_metadata = self.command_list[command_name]['metadata']
        min_args = len(command_metadata['required'])
        max_args = min_args + len(command_metadata['default'])
        if len(args) < min_args or len(args) > max_args:
            return False

        if self.ch_format['arg_dict']:
            # Check if args does not contain all required arguments
            for a in command_metadata['required']:
                if a not in args:
                    return False
            # Check if args contains an extraneous argument
            for a in args:
                if a not in command_metadata['required'] and a not in command_metadata['required']:
                    return False

        return True

    def get_command_metadata(self, command_name):
        """Get the metadata for a command in the form of a dictionary."""
        command = self.command_list[command_name]['function']
        command_signature = inspect.signature(command)
        command_args = dict(required=[], default=[])
        for param in command_signature.parameters.values():
            if param.default is param.empty:
                command_args['required'].append(param.name)
            else:
                command_args['default'].append(param.name)
        return command_args

    def add_commands(self, commands):
        """Add a dictionary of commands to the command_list."""
        for key in commands:
            command_metadata = self.get_command_metadata(commands[key])
            self.command_list[key] = dict(function=commands[key], metadata=command_metadata)

    def handle_command(self, command_text):
        """Parse command_text and calls execute_command."""
        command_text = command_text.split(self.ch_format['command_arg_splitter'])
        command_name, command_args = command_text[0], command_text[1]
        if self.ch_format['arg_dict']:
            args_list = command_args.split(self.ch_format['dict_arg_splitter'])
            command_args = {}
            for kvpair in args_list:
                kvpair = kvpair.split(self.ch_format['arg_value_splitter'])
                arg_key, arg_value = kvpair[0], kvpair[1]
                command_args[arg_key] = arg_value
        else:
            command_args = command_args.split(self.ch_format['list_arg_splitter'])
        self.execute_command(command_name, command_args)

    def execute_command(self, command_name, args):
        """Call the function corresponding to the command_name from command_list with args."""
        # Add in error handling here
        if self.ch_format['arg_dict']:
            result = self.command_list[command_name](**args)
        else:
            result = self.command_list[command_name](*args)

        if result:
            timestamp = datetime.datetime.utcnow()
            result = dict(timestamp=timestamp, args=args, command=command_name, ch_format=self.ch_format)
            self.invocation_history.append(result)
