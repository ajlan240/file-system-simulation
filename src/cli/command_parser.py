# src/cli/command_executor.py
# Execute parsed commands by calling File API and File I/O.

from src.file_api import create_file, delete_file, list_files, get_file_metadata, truncate_file
from src.fileio import open_file, close_file, read_file, write_file, seek_file
from .cli_utils import print_help

def execute_command(cmd: str, args: list):
    if cmd == "help":
        print_help()

    elif cmd == "ls":
        files = list_files()
        for f in files:
            meta = get_file_metadata(f)
            size = meta.get("size_bytes", 0)
            ftype = meta.get("file_type", "file")
            print(f"{f}\t{ftype}\t{size}B")

    elif cmd == "touch":
        if not args:
            print("Usage: touch <filename>")
            return
        create_file(args[0])

    elif cmd == "mkdir":
        if not args:
            print("Usage: mkdir <dirname>")
            return
        create_file(args[0], is_directory=True)

    elif cmd == "cat":
        if not args:
            print("Usage: cat <filename>")
            return
        fd = open_file(args[0], "r")
        data = read_file(fd, 10**6)  # read up to 1MB
        print(data.decode("utf-8", errors="ignore"))
        close_file(fd)

    elif cmd == "echo":
        if len(args) != 2 or args[1] is None:
            print("Usage: echo <text> > <filename>")
            return
        text, filename = args
        fd = open_file(filename, "w")
        write_file(fd, text.encode("utf-8"))
        close_file(fd)

    elif cmd == "rm":
        if not args:
            print("Usage: rm <filename>")
            return
        delete_file(args[0])

    elif cmd == "truncate":
        if not args:
            print("Usage: truncate <filename>")
            return
        truncate_file(args[0])

    else:
        print(f"Unknown command: {cmd}. Type 'help' for commands.")