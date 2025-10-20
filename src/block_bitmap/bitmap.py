# src/block_bitmap/bitmap.py
# Bitmap management: load/save and bit operations over the on-disk block bitmap.

from typing import Optional, List
from src.persistence.mount import STATE
from src.persistence.disk_io import read_block, write_block

# In-memory bitmap cache (bytearray), loaded at mount time.
_BITMAP: Optional[bytearray] = None

def _require_mounted():
    if not STATE.get("mounted") or STATE.get("superblock") is None:
        raise RuntimeError("Disk not mounted. Call mount() first.")

def _bitmap_total_bytes() -> int:
    sb = STATE["superblock"]
    # 1 bit per block
    return (sb.total_blocks + 7) // 8

def _bitmap_total_blocks() -> int:
    sb = STATE["superblock"]
    return sb.bitmap_blocks

def _bitmap_start_block() -> int:
    sb = STATE["superblock"]
    return sb.bitmap_start_block

def _block_size() -> int:
    sb = STATE["superblock"]
    return sb.block_size_bytes

def _load_bitmap() -> None:
    """
    Load the bitmap bytes from disk into the _BITMAP cache.
    """
    global _BITMAP
    _require_mounted()
    total_bytes = _bitmap_total_bytes()
    buf = bytearray(total_bytes)
    bs = _block_size()
    start = _bitmap_start_block()
    blocks = _bitmap_total_blocks()

    # Read contiguous bitmap region
    cursor = 0
    for i in range(blocks):
        b = read_block(start + i)
        take = min(bs, total_bytes - cursor)
        if take <= 0:
            break
        buf[cursor:cursor + take] = b[:take]
        cursor += take

    _BITMAP = buf

def _save_bitmap() -> None:
    """
    Persist the _BITMAP cache back to disk.
    """
    _require_mounted()
    if _BITMAP is None:
        return
    total_bytes = len(_BITMAP)
    bs = _block_size()
    start = _bitmap_start_block()
    blocks = _bitmap_total_blocks()

    cursor = 0
    for i in range(blocks):
        take = min(bs, total_bytes - cursor)
        if take <= 0:
            # write zero block for remaining region
            write_block(start + i, b"\x00" * bs, offset=0)
            continue
        # Prepare full block buffer: existing bytes (take) + zero padding
        buf = bytearray(bs)
        buf[:take] = _BITMAP[cursor:cursor + take]
        write_block(start + i, bytes(buf), offset=0)
        cursor += take

def ensure_bitmap_loaded() -> None:
    """
    Public helper: call to ensure the bitmap is loaded into memory.
    Safe to call multiple times.
    """
    global _BITMAP
    if _BITMAP is None:
        _load_bitmap()

def _set_bit(block_num: int, value: bool) -> None:
    """
    Set or clear a block allocation bit.
    """
    ensure_bitmap_loaded()
    if block_num < 0 or block_num >= STATE["superblock"].total_blocks:
        raise ValueError("block_num out of range")

    byte_index = block_num // 8
    bit_index = block_num % 8
    mask = 1 << bit_index

    if value:
        _BITMAP[byte_index] = _BITMAP[byte_index] | mask
    else:
        _BITMAP[byte_index] = _BITMAP[byte_index] & (~mask & 0xFF)

def _get_bit(block_num: int) -> bool:
    """
    Return True if block is marked allocated, False if free.
    """
    ensure_bitmap_loaded()
    if block_num < 0 or block_num >= STATE["superblock"].total_blocks:
        return False
    byte_index = block_num // 8
    bit_index = block_num % 8
    mask = 1 << bit_index
    return (_BITMAP[byte_index] & mask) != 0

def mark_reserved_regions() -> None:
    """
    Ensure superblock, inode table, and bitmap regions are marked allocated.
    Should be called during initialization after mount and bitmap load.
    """
    ensure_bitmap_loaded()
    sb = STATE["superblock"]

    # Reserve block 0 (superblock)
    _set_bit(0, True)

    # Reserve inode table region
    for i in range(sb.inode_table_blocks):
        _set_bit(sb.inode_start_block + i, True)

    # Reserve bitmap region
    for i in range(sb.bitmap_blocks):
        _set_bit(sb.bitmap_start_block + i, True)

    _save_bitmap()

def is_allocated(block_num: int) -> bool:
    """
    Public API: check if a block is allocated.
    """
    return _get_bit(block_num)

def allocate_first_free(start_from: int = 0) -> Optional[int]:
    """
    Scan the bitmap for the first free block starting from 'start_from'.
    Returns the allocated block number or None if full.
    """
    ensure_bitmap_loaded()
    sb = STATE["superblock"]
    for b in range(max(0, start_from), sb.total_blocks):
        if not _get_bit(b):
            _set_bit(b, True)
            _save_bitmap()
            return b
    return None

def free_block_num(block_num: int) -> None:
    """
    Free a block and persist the change.
    """
    ensure_bitmap_loaded()
    if block_num < 0 or block_num >= STATE["superblock"].total_blocks:
        raise ValueError("block_num out of range")
    _set_bit(block_num, False)
    _save_bitmap()