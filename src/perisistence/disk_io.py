# src/persistence/disk_io.py
# Low-level block I/O with dynamic BLOCK_SIZE set at mount time.

import os
from typing import Optional

# These will be set by mount() based on the superblock
DISK_FILE: Optional[str] = None
BLOCK_SIZE: Optional[int] = None

def _ensure_ready():
    if DISK_FILE is None or BLOCK_SIZE is None:
        raise RuntimeError("Persistence not initialized. Call mount() first.")

def read_block(block_num: int) -> bytes:
    """
    Read a full block from the disk image.
    Returns an exact BLOCK_SIZE bytes buffer.
    """
    _ensure_ready()
    if block_num < 0:
        raise ValueError("block_num must be non-negative")
    with open(DISK_FILE, "rb") as f:
        f.seek(block_num * BLOCK_SIZE)
        data = f.read(BLOCK_SIZE)
        # If the file is shorter than expected, pad with zeros
        if len(data) < BLOCK_SIZE:
            data = data + (b"\x00" * (BLOCK_SIZE - len(data)))
        return data

def write_block(block_num: int, data: bytes, offset: int = 0) -> None:
    """
    Write bytes into a block at optional byte offset.
    - If offset == 0 and len(data) <= BLOCK_SIZE, the block will be overwritten and padded.
    - If 0 < offset < BLOCK_SIZE, the data will be written starting at that offset.
    """
    _ensure_ready()
    if block_num < 0:
        raise ValueError("block_num must be non-negative")
    if offset < 0 or offset >= BLOCK_SIZE:
        raise ValueError("offset must be in [0, BLOCK_SIZE-1]")
    if offset + len(data) > BLOCK_SIZE:
        raise ValueError("write exceeds block boundary: offset + len(data) > BLOCK_SIZE")

    # Ensure the disk file exists and is large enough
    os.makedirs(os.path.dirname(DISK_FILE), exist_ok=True) if os.path.dirname(DISK_FILE) else None
    if not os.path.exists(DISK_FILE):
        with open(DISK_FILE, "wb"):
            pass

    with open(DISK_FILE, "r+b") as f:
        # Read current block into buffer to preserve bytes not overwritten
        f.seek(block_num * BLOCK_SIZE)
        existing = f.read(BLOCK_SIZE)
        if len(existing) < BLOCK_SIZE:
            existing = existing + (b"\x00" * (BLOCK_SIZE - len(existing)))

        # Overlay the new data at offset
        buf = bytearray(existing)
        buf[offset:offset + len(data)] = data

        # Write back the full block
        f.seek(block_num * BLOCK_SIZE)
        f.write(bytes(buf))
