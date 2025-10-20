# src/cli/cli_utils.py
# Utility functions for CLI formatting and messages.

def print_welcome():
    print("Welcome to the Mini OS Filesystem Simulator CLI")
    print("Type 'help' for available commands, 'exit' to quit.")

def print_error(msg: str):
    print(f"[ERROR] {msg}")

def print_help():
    print("Available commands:")
    print("  ls                     - list files")
    print("  touch <name>           - create empty file")
    print("  mkdir <name>           - create directory")
    print("  cat <name>             - display file contents")
    print("  echo <text> > <name>   - write text to file")
    print("  rm <name>              - delete file")
    print("  truncate <name>        - clear file contents")
    print("  exit                   - quit shell")