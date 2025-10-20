# src/cli/cli_main.py
# Entry point for the CLI shell.

from .command_parser import parse_command
from .command_executor import execute_command
from .cli_utils import print_welcome, print_error

def run_cli():
    print_welcome()
    while True:
        try:
            raw = input("fs> ").strip()
            if not raw:
                continue
            cmd, args = parse_command(raw)
            if cmd == "exit":
                print("Exiting filesystem shell.")
                break
            execute_command(cmd, args)
        except KeyboardInterrupt:
            print("\nExiting filesystem shell.")
            break
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    run_cli()