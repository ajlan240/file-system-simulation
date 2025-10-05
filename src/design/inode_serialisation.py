# src/design/inode_serialization.py
# Pack/unpack inodes to/from fixed 128-byte layout (little-endian)
import struct
from datetime import datetime
from typing import List, Optional
from .architecture import Inode

INODE_SIZE = 128
# Layout:
# 4  inode_number (I)
# 1  type (B) 0=file 1=dir
# 3  pad (3s)
# 8  file_size (Q)
# 8  created_ms (Q)
# 8  modified_ms (Q)
# 4*10 direct blocks (10I)
# 4  indirect_block (I)
# 4  flags (I)
# remaining bytes -> reserved/padding to 128

_FORMAT = "<I B 3s Q Q Q " + "10I I I"  # final sizes checked below

def _now_ms() -> int:
    return int(datetime.utcnow().timestamp() * 1000)

def inode_to_bytes(inode: Inode) -> bytes:
    t = 1 if inode.file_type == "directory" else 0
    created_ms = int(inode.created_at.timestamp() * 1000)
    modified_ms = int(inode.modified_at.timestamp() * 1000)
    direct = [b if b is not None else 0 for b in inode.direct_blocks]
    indirect = inode.indirect_block if inode.indirect_block is not None else 0
    flags = 0
    packed = struct.pack(
        "<I B 3s Q Q Q 10I I I",
        inode.inode_number,
        t,
        b"\x00\x00\x00",
        inode.file_size,
        created_ms,
        modified_ms,
        *direct,
        indirect,
        flags
    )
    if len(packed) > INODE_SIZE:
        raise ValueError("INODE packed size exceeds INODE_SIZE")
    return packed.ljust(INODE_SIZE, b"\x00")

def bytes_to_inode(buf: bytes) -> Inode:
    if len(buf) != INODE_SIZE:
        raise ValueError("Invalid inode buffer size")
    parts = struct.unpack("<I B 3s Q Q Q 10I I I", buf[:(4+1+3+8+8+8+4*10+4+4)])
    inode_number = parts[0]
    file_type = "directory" if parts[1] == 1 else "file"
    file_size = parts[3]
    created_ms = parts[4]
    modified_ms = parts[5]
    direct = list(parts[6:6+10])
    indirect = parts[16]
    inode = Inode(
        inode_number=inode_number,
        file_type=file_type,
        file_size=file_size
    )
    inode.created_at = datetime.utcfromtimestamp(created_ms/1000.0)
    inode.modified_at = datetime.utcfromtimestamp(modified_ms/1000.0)
    inode.direct_blocks = [d if d != 0 else None for d in direct]
    inode.indirect_block = indirect if indirect != 0 else None
    return inode