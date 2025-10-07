import os

def create_file(path, is_directory=False, content=""):
    """
    Creates a file or directory at the specified path.

    Args:
        path (str): The full path for the new file or directory.
        is_directory (bool): True to create a directory, False for a file.
        content (str): The content to write to the file if creating a file.

    Returns:
        str: A success or error message.
    """
    try:
        if is_directory:
            os.makedirs(path, exist_ok=True)
            return f"Directory created: {path}"
        else:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(path, 'w') as f:
                f.write(content)
            return f"File created: {path}"
    except IOError as e:
        return f"Error creating '{path}': {e}"