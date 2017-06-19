import inspect


class Command(object):
    def __init__(self, names, function):
        self.function = function
        self.names = names
        self.required = {}
        self.default = {}

        signature = inspect.signature(function)
        for param in signature.parameters.values():
            if param.default is param.empty:
                self.required[param.name] = []
            else:
                self.default[param.name] = []
            
    def validate_args(self, args):
        min_args = len(self.required)
        max_args = min_args + len(self.default)
        if len(args) < min_args or len(args) > max_args:
            raise RuntimeError('Incorrect Number of Arguments')

        if isinstance(args, dict):
            # Check if args does not contain all required arguments
            for arg in self.required:
                if arg not in args:
                    raise RuntimeError('Missing Required Argument')
            # Check if args contains an extraneous argument
            for arg in args:
                if arg not in self.required and arg not in self.default:
                    raise RuntimeError('Extraneous Argument')

    def invoke(self, args):
        self.validate_args(args)
        self.function(**args) if isinstance(args, dict) else self.function(*args)


