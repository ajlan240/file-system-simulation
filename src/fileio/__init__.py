# src/fileio/__init__.py
# Public API for file I/O layer (Member 7).
# Exposes only the high-level functions; helpers like offset_mapper remain internal.

from .file_io import (
    open_file,
    close_file,
    read_file,
    write_file,
    seek_file,
)