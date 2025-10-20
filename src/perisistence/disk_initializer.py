# src/persistence/disk_initializer.py
# Creates disk.img and writes a real serialized superblock and reserved regions.

import math
import os
from typing import Optional
from src.design.superblock_serialization import SuperblockLayout, to_bytes
from src.design.inode_serialization import INODE_SIZE

def _compute_layout(
    total_blocks: int,
    block_size_bytes: int,
    inode_count: int
) -> SuperblockLayout:
    """
    Compute a simple layout:
    - Block 0: Superblock (serialized to a single block, regardless of block_size_bytes)
    - Next blocks: inode table
    - Next blocks: bitmap (1 bit per block)
    - Remaining: data region
    """
    # Inode table blocks: ceil(inode_count * INODE_SIZE / block_size)
    inode_table_bytes = inode_count * INODE_SIZE
    inode_table_blocks = math.ceil(inode_table_bytes / block_size_bytes)

    # Bitmap: 1 bit per block => total_blocks bits => bytes => blocks
    bitmap_bytes = math.ceil(total_blocks / 8)
    bitmap_blocks = math.ceil(bitmap_bytes / block_size_bytes)

    inode_start_block = 1  # immediately after superblock
    bitmap_start_block = inode_start_block + inode_table_blocks
    data_start_block = bitmap_start_block + bitmap_blocks

    if data_start_block >= total_blocks:
        raise ValueError("Layout exceeds total blocks. Increase total_blocks or reduce inode_count.")

    return SuperblockLayout(
        magic=0xF1F51,
        version=1,
        total_size_bytes=total_blocks * block_size_bytes,
        block_size_bytes=block_size_bytes,
        total_blocks=total_blocks,
        inode_count=inode_count,
        inode_table_blocks=inode_table_blocks,
        bitmap_blocks=bitmap_blocks,
        inode_start_block=inode_start_block,
        bitmap_start_block=bitmap_start_block,
        data_start_block=data_start_block,
        root_inode_number=0,
        checksum=0
    )

def initialize_disk(
    disk_path: str = "disk.img",
    total_blocks: int = 2048,
    block_size_bytes: int = 512,
    inode_count: int = 256
) -> SuperblockLayout:
    """
    Create the disk image of size total_blocks * block_size_bytes and write a serialized superblock.
    Returns the SuperblockLayout used.
    """
    # Compute layout
    sb = _compute_layout(total_blocks=total_blocks, block_size_bytes=block_size_bytes, inode_count=inode_count)

    # Create/resize disk file
    os.makedirs(os.path.dirname(disk_path), exist_ok=True) if os.path.dirname(disk_path) else None
    with open(disk_path, "wb") as f:
        f.truncate(total_blocks * block_size_bytes)

    # Write the superblock into block 0 (always exactly one block)
    sb_bytes = to_bytes(sb)
    if len(sb_bytes) > sb.block_size_bytes:
        # If superblock serialization uses a fixed size larger than block size, that's an invalid config
        raise ValueError("Superblock bytes exceed block size")
    # Pad to full block size
    sb_block = sb_bytes.ljust(sb.block_size_bytes, b"\x00")
    with open(disk_path, "r+b") as f:
        f.seek(0)
        f.write(sb_block)

    # Zero the inode table and bitmap regions
    zero_block = b"\x00" * sb.block_size_bytes
    with open(disk_path, "r+b") as f:
        # Inode table region
        for i in range(sb.inode_table_blocks):
            f.seek((sb.inode_start_block + i) * sb.block_size_bytes)
            f.write(zero_block)
        # Bitmap region
        for i in range(sb.bitmap_blocks):
            f.seek((sb.bitmap_start_block + i) * sb.block_size_bytes)
            f.write(zero_block)

    print(f"[INIT] Disk created at {disk_path}")
    print(f"[INIT] Blocks: {sb.total_blocks}, Block size: {sb.block_size_bytes} bytes")
    print(f"[INIT] Inode table blocks: {sb.inode_table_blocks}, Bitmap blocks: {sb.bitmap_blocks}")
    print(f"[INIT] Data starts at block: {sb.data_start_block}")

    return sb
