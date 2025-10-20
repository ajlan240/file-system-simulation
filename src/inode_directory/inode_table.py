# src/inode_directory/inode_table.py
# Persistence-backed inode table: allocate/get/update/free inodes on disk.

from typing import Optional
from src.persistence.mount import STATE
from src.persistence.disk_io import read_block, write_block
from src.design.inode_serialisation import INODE_SIZE, inode_to_bytes, bytes_to_inode
from src.design.architecture import Inode
import math

def _require_mounted():
    if not STATE.get("mounted") or STATE.get("superblock") is None:
        raise RuntimeError("Disk not mounted. Call mount() first.")

def _inode_table_bounds():
    sb = STATE["superblock"]
    start = sb.inode_start_block
    blocks = sb.inode_table_blocks
    return start, blocks, sb.block_size_bytes, sb.inode_count

def _inode_slot_location(inode_number: int):
    start, _, block_size, _ = _inode_table_bounds()
    if inode_number < 0:
        raise IndexError("Invalid inode number")
    # Each inode occupies INODE_SIZE bytes; compute its block and offset
    byte_offset = inode_number * INODE_SIZE
    block_index = byte_offset // block_size
    offset_in_block = byte_offset % block_size
    return start + block_index, offset_in_block

def get_inode(inode_number: int) -> Inode:
    """
    Read an inode from the inode table and deserialize it.
    """
    _require_mounted()
    start, blocks, block_size, inode_count = _inode_table_bounds()
    if inode_number < 0 or inode_number >= inode_count:
        raise IndexError("Invalid inode number")

    block_num, offset = _inode_slot_location(inode_number)
    if block_num < start or block_num >= start + blocks:
        raise IndexError("Inode location out of inode table bounds")

    # If the inode crosses block boundary, read two blocks and slice
    buf = read_block(block_num)
    if offset + INODE_SIZE <= block_size:
        inode_bytes = buf[offset:offset + INODE_SIZE]
    else:
        # Spans into next block
        first_part = buf[offset:block_size]
        next_buf = read_block(block_num + 1)
        remaining = INODE_SIZE - len(first_part)
        inode_bytes = first_part + next_buf[:remaining]

    return bytes_to_inode(inode_bytes)

def update_inode(inode: Inode) -> None:
    """
    Serialize and write the inode back to the inode table.
    """
    _require_mounted()
    start, blocks, block_size, inode_count = _inode_table_bounds()
    if inode.inode_number < 0 or inode.inode_number >= inode_count:
        raise IndexError("Invalid inode number")

    inode_bytes = inode_to_bytes(inode)
    if len(inode_bytes) != INODE_SIZE:
        raise ValueError("Serialized inode size mismatch")

    block_num, offset = _inode_slot_location(inode.inode_number)
    if block_num < start or block_num >= start + blocks:
        raise IndexError("Inode location out of inode table bounds")

    # If write crosses the block boundary, perform two writes
    if offset + INODE_SIZE <= block_size:
        write_block(block_num, inode_bytes, offset=offset)
    else:
        first_len = block_size - offset
        write_block(block_num, inode_bytes[:first_len], offset=offset)
        write_block(block_num + 1, inode_bytes[first_len:], offset=0)

def allocate_inode() -> Inode:
    """
    Find a free inode slot and return an initialized Inode.
    Free slots are indicated by inode_number field == index and default values.
    Strategy: first-fit scan for an inode with file_type 'file' and size==0 and no blocks,
    but we rely on a simple marker: file_type empty (not set). We create a fresh Inode.
    """
    _require_mounted()
    _, _, _, inode_count = _inode_table_bounds()

    # Scan for a slot whose direct_blocks are all None and file_size==0 and file_type unset
    # We will read each inode; if it's an uninitialized block (all zeros), bytes_to_inode should map to defaults.
    for i in range(inode_count):
        inode = get_inode(i)
        # Heuristic: consider free if both file_size==0 and file_type=='file' and no blocks,
        # but this can collide. More robust: we treat 'flags' field later.
        # For now: if file_size==0 and all blocks None and indirect None and filename not set (architecture has no filename).
        if inode.file_size == 0 and all(b is None for b in inode.direct_blocks) and inode.indirect_block is None:
            # Assign as 'file' by default; directory will overwrite file_type if needed.
            inode.file_type = "file"
            inode.inode_number = i
            update_inode(inode)
            return inode

    raise RuntimeError("No free inodes available")

def free_inode(inode_number: int) -> None:
    """
    Mark inode as free by zeroing its serialized bytes.
    """
    _require_mounted()
    # Write an all-zero inode record at the slot to mark it free
    zero = b"\x00" * INODE_SIZE
    block_num, offset = _inode_slot_location(inode_number)
    start, blocks, block_size, _ = _inode_table_bounds()
    if block_num < start or block_num >= start + blocks:
        raise IndexError("Inode location out of inode table bounds")

    if offset + INODE_SIZE <= block_size:
        write_block(block_num, zero, offset=offset)
    else:
        first_len = block_size - offset
        write_block(block_num, zero[:first_len], offset=offset)
        write_block(block_num + 1, zero[first_len:], offset=0)