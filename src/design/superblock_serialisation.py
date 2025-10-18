# src/design/superblock_serialization.py
# Pack/unpack the superblock into a single 512-byte block

import struct
from dataclasses import dataclass
from typing import Optional

SUPERBLOCK_SIZE = 512

@dataclass
class SuperblockLayout:
    magic: int
    version: int
    total_size_bytes: int
    block_size_bytes: int
    total_blocks: int
    inode_count: int
    inode_table_blocks: int
    bitmap_blocks: int
    inode_start_block: int
    bitmap_start_block: int
    data_start_block: int
    root_inode_number: int = 0
    checksum: Optional[int] = 0

def to_bytes(sb: SuperblockLayout) -> bytes:
    # pack first fields, rest reserved/pad to 512
    packed = struct.pack(
        "<I I Q I I I I I I I I I",
        sb.magic,
        sb.version,
        sb.total_size_bytes,
        sb.block_size_bytes,
        sb.total_blocks,
        sb.inode_count,
        sb.inode_table_blocks,
        sb.bitmap_blocks,
        sb.inode_start_block,
        sb.bitmap_start_block,
        sb.data_start_block,
        sb.root_inode_number
    )
    # append checksum as 4 bytes
    packed += struct.pack("<I", sb.checksum or 0)
    return packed.ljust(SUPERBLOCK_SIZE, b"\x00")

def from_bytes(buf: bytes) -> SuperblockLayout:
    if len(buf) != SUPERBLOCK_SIZE:
        raise ValueError("Invalid superblock size")
    parts = struct.unpack("<I I Q I I I I I I I I I", buf[:(4+4+8+4+4+4+4+4+4+4+4+4)])
    return SuperblockLayout(*parts, checksum=0)