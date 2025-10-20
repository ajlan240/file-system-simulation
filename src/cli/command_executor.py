# src/cli/command_parser.py
# Parse raw input into (command, args).

def parse_command(raw: str):
    tokens = raw.split()
    if not tokens:
        return None, []
    cmd = tokens[0]

    # Special handling for echo with redirection
    if cmd == "echo":
        if ">" in tokens:
            idx = tokens.index(">")
            text = " ".join(tokens[1:idx])
            filename = tokens[idx + 1] if idx + 1 < len(tokens) else None
            return "echo", [text, filename]
        else:
            return "echo", [" ".join(tokens[1:]), None]

    return cmd, tokens[1:]