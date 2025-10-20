# src/block_bitmap/block_allocator.py
# Public allocation API aligned with Member 1's contracts.

from typing import Optional
from src.persistence.mount import STATE
from .bitmap import ensure_bitmap_loaded, mark_reserved_regions
from .bitmap import allocate_first_free, free_block_num, is_allocated as _is_alloc

def _require_mounted():
    if not STATE.get("mounted"):
        raise RuntimeError("Disk not mounted. Call mount() first.")

def allocate_block() -> int:
    """
    Allocate a free block from the bitmap and return its block number.
    Raises RuntimeError if no free blocks are available.
    """
    _require_mounted()
    ensure_bitmap_loaded()
    # Ensure reserved regions are marked so they are never allocated
    mark_reserved_regions()
    b = allocate_first_free(start_from=STATE["superblock"].data_start_block)
    if b is None:
        raise RuntimeError("No free blocks available")
    return b

def free_block(block_num: int) -> None:
    """
    Free the given block number.
    """
    _require_mounted()
    # Prevent freeing reserved regions
    sb = STATE["superblock"]
    reserved = {0}
    reserved.update(range(sb.inode_start_block, sb.inode_start_block + sb.inode_table_blocks))
    reserved.update(range(sb.bitmap_start_block, sb.bitmap_start_block + sb.bitmap_blocks))
    if block_num in reserved:
        raise ValueError("Attempt to free a reserved block")
    free_block_num(block_num)

def is_allocated(block_num: int) -> bool:
    """
    Check allocation status for a block number.
    """
    _require_mounted()
    return _is_alloc(block_num)