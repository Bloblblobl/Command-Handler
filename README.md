# Command Handler
Command Handler is a little (soon-to-be) package which is designed to provide a simple, generic CLI that supports
arbitrary user-defined commands.

## Why Command Handler?
I've noticed that for every project I've worked on where I want the user to be able to interact with the program 
with a simple CLI, I've been hard-coding all the commands I want to give them access to into the same simple CLI-like 
structure. Command Handler is my generic solution for this problem.

## What's a CLI?
CLI stands for [Command Line Interface.](https://en.wikipedia.org/wiki/Command-line_interface) From wikipedia: 
"A command-line interface [...] is a means of interacting with a computer program where the user (or client) issues 
commands to the program in the form of successive lines of text (command lines)."

## Technical Details
I've always been slightly obsessed with superfluous customizability, so I've added a lot of potentially useful, but
most likely unneeded features to Command Handler, which slightly complicates its usage for the layman.

### Simple Usage
`calc_example.py` showcases a very simple use case for command handler. To implement Command Handler into your code,
all you need to do is import it and instantiate a CommandHandler object, then add your commands to it. 
Eventually the CommandHandler class will able to run its own simple CLI loop, but for now you have to define your 
own CLI loop, as seen in `calc_example.py`.

### Adding Commands
The `add_commands` function accepts a list of dictionaries as its sole argument. Here is an example of the structure
for the list of commands:
```
[
    {
        '<command1 name>': <command1 name>,
        'metadata':
        { //OPTIONAL
            'args':
            {
                'required': ['<required argument1>', '<required argument2>', ...],
                'default': ['<default argument1>', '<default argument2>', ...]
                'synonyms': [('<argument1>', 'synonym1'), ('<argument2>', 'synonym2'>), ...]
            }
            'synonyms': ['command synonym1', 'command synonym2', ...]
        }
    },

    ...
]
```
Let's break this down into its components:
- Each `command` dictionary has 2 fields:
    - The first field is the `command name`, the string used to call the command in the CLI, and it's value is 
      the function itself.
    - The second field is `metadata`, and it's value is a complicated dictionary which is explained below.
- The `metadata` dictionary is where, unsurprisingly, all the metadata for the command is stored. This dictionary is 
  optional when adding a command to the command list, as CommandHandler will generate a `metadata` dictionary for you.*
    - The `args` dictionary carries all the information for the command's arguments.
    - `required` is a list of strings corresponding to the command's required arguments.
    - `default` is a list of strings corresponding to the command's default arguments a.k.a arguments that 
      have a default value.
    - `synonyms` is a list of tuples, with the first item in each tuple being the string corresponding to the 
      actual argument name, and the second item being the synonym for the argument.
    - The `metadata` dictionary also has a `synonyms` field at the top level, where it stores the synonyms for the 
      command name, this time simply as a list of strings, as all the synonyms in this list are for the same command.

***WARNING:** I highly advise against defining your own `metadata` dictionary when adding commands, as messing with 
the `args` dictionary can result in fatal errors.
  
#### Unique Names
Command Handler enforces unique names/synonyms both for command names and arguments. Trying to add/define a command 
or argument with the same name or synonym as an existing name or synonym will result in a RuntimeError. (Unique 
names/synonyms for arguments are not enforced globally, only within a single command.) Additionally, there are some 
command names reserved for built-ins. They are listed in the built-in commands section.

### Command Formatting
The Command Handler class has a property called `ch_format`, which is a config dictionary that Command Handler refers 
to when parsing commands. `ch_format` has 5 fields:
- `arg_dict`: If True, Command Handler will parse command arguments as a dictionary. If False, it will 
  parse command arguments as a list.
- `command_arg_splitter`: The string Command Handler will look for to split the command name and arguments. 
    - Default = '|' 
    - Example: `<command name>|<command arguments>`
- `arg_value_splitter`: The string Command Handler will look for to split the argument names and values if `arg_dict` 
  is True.
    - Default = '='
    - Example: `<command name>|<arg name>=<arg value>`
- `dict_arg_splitter`: The string Command Handler will look for to split the argument name-value pairs if `arg_dict` 
  is True.
    - Default = ' '
    - Example: `<command name>|<arg1 name>=<arg1 value> <arg2 name>=<arg2 value> <arg3 name>=<arg3 value>`
- `list_arg_splitter`: The string Command Handler will look for to split the argument values if `arg_dict` 
  is False.
    - Default = ','
    - Example: `<command name>|<arg1>,<arg2>,<arg3>`
    