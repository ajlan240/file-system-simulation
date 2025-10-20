# src/cli/command_executor.py

from src.persistence.file_api import (
    create_file,
    delete_file,
    list_files,
    write_file,
    read_file,
)

def execute_command(cmd: str, args: list[str]):
    """
    Execute a parsed command with arguments.
    Supports: touch, ls, rm, echo, cat, help
    """

    # Normalize filenames to absolute paths
    def norm(name: str) -> str:
        return name if name.startswith("/") else "/" + name

    if cmd == "touch":
        if not args:
            print("[ERROR] Missing filename for 'touch'")
            return
        try:
            create_file(norm(args[0]))
        except Exception as e:
            print(f"[ERROR] Failed to create file: {e}")

    elif cmd == "ls":
        try:
            files = list_files()
            if not files:
                print("[INFO] Directory is empty")
            else:
                for f in files:
                    print(f)
        except Exception as e:
            print(f"[ERROR] ls failed: {e}")

    elif cmd == "rm":
        if not args:
            print("[ERROR] Missing filename for 'rm'")
            return
        try:
            delete_file(norm(args[0]))
        except Exception as e:
            print(f"[ERROR] rm failed: {e}")

    elif cmd == "echo":
        # Expect: echo <text> > <filename>
        if len(args) < 3 or args[1] != ">":
            print("[ERROR] Usage: echo <text> > <filename>")
            return
        text, filename = args[0], norm(args[2])
        try:
            # If file doesn’t exist, create it first
            if filename.lstrip("/") not in list_files():
                create_file(filename)
            write_file(filename.lstrip("/"), text.encode())
        except Exception as e:
            print(f"[ERROR] echo failed: {e}")


    elif cmd == "cat":
        if not args:
            print("[ERROR] Missing filename for 'cat'")
            return
        filename = norm(args[0])
        try:
            data = read_file(filename.lstrip("/"))
            if data:
                print(data.decode(errors="replace"))
            else:
                print("")  # empty file
        except Exception as e:
            print(f"[ERROR] cat failed: {e}")

    elif cmd == "help":
        print("Available commands:")
        print("  touch <filename>         - Create an empty file")
        print("  echo <text> > <filename> - Write text to a file (creates if missing)")
        print("  cat <filename>           - Display file contents")
        print("  rm <filename>            - Delete a file")
        print("  ls                       - List files")
        print("  exit                     - Exit the simulator")

    else:
        print(f"[ERROR] Unknown command: {cmd}")