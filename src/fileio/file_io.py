# src/fileio/file_io.py
# File descriptor table and open/close/read/write/seek over the simulated filesystem.

from typing import Dict, Optional
from dataclasses import dataclass
from src.persistence.mount import STATE
from src.persistence.disk_io import read_block, write_block
from src.inode_directory.resolver import resolve as resolve_name, get_inode, update_inode
from src.block_bitmap.block_allocator import allocate_block, free_block
from src.fileio.offset_mapper import logical_to_block_index, logical_to_block_inner_offset

@dataclass
class FDEntry:
    inode_number: int
    mode: str        # 'r', 'w', 'a', 'rw'
    cursor: int      # current file pointer in bytes

# Global file descriptor table
_FD_TABLE: Dict[int, FDEntry] = {}
_NEXT_FD: int = 3  # mimic OS (0,1,2 reserved)

def _require_mounted():
    if not STATE.get("mounted"):
        raise RuntimeError("Disk not mounted. Call mount() first.")

def _block_size() -> int:
    return STATE["superblock"].block_size_bytes

def _mode_perms(mode: str):
    m = mode.lower()
    can_read = 'r' in m or 'rw' in m
    can_write = 'w' in m or 'a' in m or 'rw' in m
    return can_read, can_write, 'a' in m

def open_file(filename: str, mode: str = 'r') -> int:
    """
    Open a file and return a file descriptor.
    Modes: 'r' (read), 'w' (write truncate), 'a' (append), 'rw' (read/write no truncate).
    """
    _require_mounted()
    inum = resolve_name(filename)
    if inum is None:
        raise FileNotFoundError(f"'{filename}' not found")

    inode = get_inode(inum)
    if getattr(inode, "file_type", "file") != "file":
        raise IsADirectoryError(f"'{filename}' is a directory")

    can_read, can_write, is_append = _mode_perms(mode)
    if not (can_read or can_write):
        raise ValueError("Invalid mode. Use 'r', 'w', 'a', or 'rw'.")

    # 'w' truncates
    if 'w' in mode and 'a' not in mode:
        _truncate_inode_blocks(inode)
        inode.file_size = 0
        update_inode(inode)

    # initial cursor
    cursor = inode.file_size if is_append else 0

    global _NEXT_FD
    fd = _NEXT_FD
    _NEXT_FD += 1
    _FD_TABLE[fd] = FDEntry(inode_number=inum, mode=mode, cursor=cursor)
    return fd

def close_file(fd: int) -> None:
    """
    Close a file descriptor.
    """
    if fd not in _FD_TABLE:
        raise ValueError("Invalid file descriptor")
    del _FD_TABLE[fd]

def seek_file(fd: int, offset: int, whence: int = 0) -> int:
    """
    Move the file pointer.
    whence: 0 = start, 1 = current, 2 = end
    Returns the new cursor position.
    """
    entry = _FD_TABLE.get(fd)
    if entry is None:
        raise ValueError("Invalid file descriptor")

    inode = get_inode(entry.inode_number)
    size = getattr(inode, "file_size", 0)

    if whence == 0:
        new_pos = offset
    elif whence == 1:
        new_pos = entry.cursor + offset
    elif whence == 2:
        new_pos = size + offset
    else:
        raise ValueError("whence must be 0, 1, or 2")

    if new_pos < 0:
        raise ValueError("seek before start of file")
    entry.cursor = new_pos
    return entry.cursor

def read_file(fd: int, size: int) -> bytes:
    """
    Read up to 'size' bytes from the current cursor.
    """
    entry = _FD_TABLE.get(fd)
    if entry is None:
        raise ValueError("Invalid file descriptor")
    can_read, _, _ = _mode_perms(entry.mode)
    if not can_read:
        raise PermissionError("File not open for reading")

    inode = get_inode(entry.inode_number)
    bs = _block_size()
    file_size = getattr(inode, "file_size", 0)
    if entry.cursor >= file_size or size <= 0:
        return b""

    to_read = min(size, file_size - entry.cursor)
    data = _read_range(inode, entry.cursor, to_read, bs)
    entry.cursor += len(data)
    return data

def write_file(fd: int, data: bytes) -> int:
    """
    Write 'data' bytes at the current cursor; expand file and allocate blocks as needed.
    Returns the number of bytes written.
    """
    entry = _FD_TABLE.get(fd)
    if entry is None:
        raise ValueError("Invalid file descriptor")
    _, can_write, is_append = _mode_perms(entry.mode)
    if not can_write:
        raise PermissionError("File not open for writing")

    inode = get_inode(entry.inode_number)
    bs = _block_size()

    # If appending, cursor should already be at end
    # Ensure blocks exist to cover write range
    bytes_written = _write_range(inode, entry.cursor, data, bs)
    entry.cursor += bytes_written

    # Update inode size if we wrote past previous end
    new_end = entry.cursor
    if new_end > getattr(inode, "file_size", 0):
        inode.file_size = new_end
    update_inode(inode)
    return bytes_written

# Internal helpers

def _ensure_direct_capacity(inode, upto_block_index: int) -> None:
    """
    Ensure inode.direct_blocks list exists and has slots up to 'upto_block_index' (inclusive).
    """
    if not hasattr(inode, "direct_blocks") or inode.direct_blocks is None:
        inode.direct_blocks = []
    while len(inode.direct_blocks) <= upto_block_index:
        inode.direct_blocks.append(None)

def _allocate_block_for_index(inode, block_index: int) -> int:
    """
    Ensure a block exists at direct_blocks[block_index]; allocate if None.
    """
    _ensure_direct_capacity(inode, block_index)
    if inode.direct_blocks[block_index] is None:
        inode.direct_blocks[block_index] = allocate_block()
    return inode.direct_blocks[block_index]

def _read_range(inode, start_offset: int, length: int, bs: int) -> bytes:
    """
    Read 'length' bytes starting at 'start_offset' using direct blocks.
    """
    if length <= 0:
        return b""
    chunks = []
    remaining = length
    cursor = start_offset
    while remaining > 0:
        bidx = logical_to_block_index(cursor, bs)
        inner = logical_to_block_inner_offset(cursor, bs)
        # If no block, unread gap yields zeroes (or stop). We'll stop for simplicity.
        if not hasattr(inode, "direct_blocks") or bidx >= len(inode.direct_blocks):
            break
        bnum = inode.direct_blocks[bidx]
        if bnum is None:
            break
        raw = read_block(bnum)
        take = min(bs - inner, remaining)
        chunks.append(raw[inner:inner + take])
        cursor += take
        remaining -= take
    return b"".join(chunks)

def _write_range(inode, start_offset: int, data: bytes, bs: int) -> int:
    """
    Write 'data' starting at 'start_offset', allocating blocks as needed.
    Returns bytes written.
    """
    if not data:
        return 0
    remaining = len(data)
    cursor = start_offset
    written = 0
    while remaining > 0:
        bidx = logical_to_block_index(cursor, bs)
        inner = logical_to_block_inner_offset(cursor, bs)
        bnum = _allocate_block_for_index(inode, bidx)
        # Read current block to preserve existing bytes before/after write region
        block_buf = bytearray(read_block(bnum))
        take = min(bs - inner, remaining)
        src_slice = data[written:written + take]
        block_buf[inner:inner + take] = src_slice
        write_block(bnum, bytes(block_buf), offset=0)
        cursor += take
        written += take
        remaining -= take
    return written

def _truncate_inode_blocks(inode) -> None:
    """
    Free all direct blocks of the inode and clear list.
    """
    if not hasattr(inode, "direct_blocks") or inode.direct_blocks is None:
        return
    for b in inode.direct_blocks:
        if b is not None:
            free_block(b)
    inode.direct_blocks = []