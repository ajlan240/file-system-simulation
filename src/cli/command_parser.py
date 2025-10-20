# src/cli/command_parser.py

def parse_command(raw: str):
    """
    Parse a raw command line string into (command, args).

    Special handling for 'echo ... > filename':
    - Groups all words before '>' as the text.
    - Takes the token after '>' as the filename.
    - If no '>' is present, everything after 'echo' is treated as text only.
    """
    parts = raw.strip().split()
    if not parts:
        return None, []

    cmd = parts[0]

    if cmd == "echo":
        # Case 1: echo without redirection
        if ">" not in parts:
            text = " ".join(parts[1:])
            return "echo", [text]

        # Case 2: echo with redirection
        idx = parts.index(">")
        text = " ".join(parts[1:idx])  # everything before '>'
        filename = parts[idx + 1] if idx + 1 < len(parts) else ""
        return "echo", [text, ">", filename]

    # Default: return command and remaining args
    return cmd, parts[1:]