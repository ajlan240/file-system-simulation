import os
import shutil

def delete_file(path):
    """
    Deletes a file or an entire directory tree.

    Args:
        path (str): The path to the file or directory to delete.

    Returns:
        str: A success or error message.
    """
    try:
        if not os.path.exists(path):
            return f"Error: Path '{path}' not found."

        if os.path.isfile(path):
            os.remove(path)
            return f"File deleted: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Directory deleted: {path}"
    except (OSError, shutil.Error) as e:
        return f"Error deleting '{path}': {e}"

