from command_handler import CommandHandler


def main():
    ch = CommandHandler()
    while True:
        result = ch.handle_command(input('>>>'))
        if result:
            print(result)


if __name__ == '__main__':
    main()