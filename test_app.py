from command_handler import CommandHandler


def add(op1, op2):
    return int(op1) + int(op2)


def subtract(op1, op2):
    return int(op1) - int(op2)


def multiply(op1, op2):
    return int(op1) * int(op2)


def divide(op1, op2):
    return int(op1) / int(op2)


def main():
    ch = CommandHandler()
    ch.add_commands([dict(add=add),
                     dict(subtract=subtract),
                     dict(multiple=multiply),
                     dict(divide=divide)])
    while True:
        result = ch.handle_command(input('>>>'))
        if result:
            print(result)


if __name__ == '__main__':
    main()
