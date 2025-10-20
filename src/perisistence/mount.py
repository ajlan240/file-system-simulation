# src/persistence/mount.py
# Mount the disk, load the superblock, and set global I/O state.

from typing import Dict, Any
from src.design.superblock_serialization import from_bytes, SUPERBLOCK_SIZE
from .disk_io import BLOCK_SIZE as IO_BLOCK_SIZE, DISK_FILE as IO_DISK_FILE
from .disk_io import read_block, write_block  # for consumers (re-export after mount)

# Keep a simple global state
STATE: Dict[str, Any] = {
    "mounted": False,
    "superblock": None,
    "disk_path": None,
}

def mount(disk_path: str = "disk.img") -> None:
    """
    Mount the disk:
    - Read block 0 and parse the superblock.
    - Set global BLOCK_SIZE and DISK_FILE for disk I/O.
    """
    # Temporarily set disk path so read_block can open the file
    # We’ll set globals once we know the real block size from superblock
    from . import disk_io as io

    # Read the first 512 bytes (serialized superblock payload) independent of block size
    # We must open raw to read initial SUPERBLOCK_SIZE bytes
    try:
        with open(disk_path, "rb") as f:
            sb_raw = f.read(SUPERBLOCK_SIZE)
    except FileNotFoundError:
        raise FileNotFoundError("Disk image not found. Initialize it first.")

    sb = from_bytes(sb_raw)

    # Set global I/O configuration to superblock’s block size and disk path
    io.DISK_FILE = disk_path
    io.BLOCK_SIZE = sb.block_size_bytes

    STATE["mounted"] = True
    STATE["superblock"] = sb
    STATE["disk_path"] = disk_path

    print(f"[MOUNT] Disk mounted: {disk_path}")
    print(f"[MOUNT] Block size: {sb.block_size_bytes}, Total blocks: {sb.total_blocks}")
    print(f"[MOUNT] Inode table starts at block {sb.inode_start_block} ({sb.inode_table_blocks} blocks)")
    print(f"[MOUNT] Bitmap starts at block {sb.bitmap_start_block} ({sb.bitmap_blocks} blocks)")
    print(f"[MOUNT] Data region starts at block {sb.data_start_block}")
