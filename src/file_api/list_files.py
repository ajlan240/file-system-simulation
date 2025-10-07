import os
import datetime

def get_file_metadata(path):
    """
    Retrieves metadata for a given file.

    Args:
        path (str): The path to the file.

    Returns:
        dict or str: A dictionary of metadata or an error message string.
    """
    if not os.path.exists(path):
        return f"Error: Path '{path}' not found."
    try:
        stat = os.stat(path)
        return {
            "path": os.path.abspath(path),
            "size_bytes": stat.st_size,
            "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_directory": os.path.isdir(path)
        }
    except OSError as e:
        return f"Error getting metadata for '{path}': {e}"