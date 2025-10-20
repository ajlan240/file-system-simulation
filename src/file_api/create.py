# src/file_api/create.py
# Create files/directories in the simulated filesystem.

from typing import Optional
from src.inode_directory.resolver import (
    allocate_inode,
    update_inode,
    add_entry,
    resolve,
    get_inode,
)
from src.block_bitmap.block_allocator import allocate_block
from src.persistence.mount import STATE

def create_file(filename: str, is_directory: bool = False) -> int:
    """
    Create a file or directory entry in the simulated FS.
    Returns the inode number.
    """
    if not STATE.get("mounted"):
        raise RuntimeError("Disk not mounted. Call mount() first.")

    # Prevent duplicates
    if resolve(filename) is not None:
        raise FileExistsError(f"'{filename}' already exists")

    inode = allocate_inode()
    inode.file_type = "dir" if is_directory else "file"
    inode.file_size = 0
    # Ensure direct_blocks is an indexable list of block pointers (None or int)
    # If architecture initializes differently, keep the shape consistent.
    if not hasattr(inode, "direct_blocks") or inode.direct_blocks is None:
        inode.direct_blocks = []

    # For directories, optionally allocate a data block to hold directory data later (future use)
    # Keeping directory payload minimal; Member 3 stores directory map separately.
    update_inode(inode)
    add_entry(filename, inode.inode_number)
    return inode.inode_number