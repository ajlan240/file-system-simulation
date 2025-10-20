# src/file_api/delete.py
from src.persistence.mount import STATE
from src.inode_directory.resolver import resolve, get_inode, remove_entry
from src.inode_directory.inode_table import free_inode
from src.block_bitmap.block_allocator import free_block
from src.persistence.disk_io import write_block
from .files import _truncate_inode_blocks

def delete_file(filename: str) -> None:
    """
    Delete a file (or empty directory) from the simulated FS.
    """
    if not STATE.get("mounted"):
        raise RuntimeError("Disk not mounted. Call mount() first")

    inum = resolve(filename)
    if inum is None:
        raise FileNotFoundError(f"'{filename}' not found")

    inode = get_inode(inum)
    if getattr(inode, "file_type", "file") == "file":
        _truncate_inode_blocks(inode)
        inode.file_size = 0

    remove_entry(filename)
    free_inode(inum)