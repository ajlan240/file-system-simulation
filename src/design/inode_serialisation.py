import struct

# File type constants
FILE_TYPE_REGULAR = 1
FILE_TYPE_DIR = 2

# Fixed inode size (adjust if your design differs)
INODE_SIZE = 128

class Inode:
    def __init__(self, file_type, size, direct_blocks,
                 single_indirect, double_indirect, triple_indirect,
                 link_count, uid, gid, mode, ctime, mtime, atime):
        self.file_type = file_type
        self.size = size
        self.direct_blocks = direct_blocks
        self.single_indirect = single_indirect
        self.double_indirect = double_indirect
        self.triple_indirect = triple_indirect
        self.link_count = link_count
        self.uid = uid
        self.gid = gid
        self.mode = mode
        self.ctime = ctime
        self.mtime = mtime
        self.atime = atime

def inode_to_bytes(inode: Inode) -> bytes:
    # Pack exactly 14 fields
    data = struct.pack(
        "<I I 12i i i i I I I I I I I",
        inode.file_type,
        inode.size,
        *inode.direct_blocks,
        inode.single_indirect,
        inode.double_indirect,
        inode.triple_indirect,
        inode.link_count,
        inode.uid,
        inode.gid,
        inode.mode,
        inode.ctime,
        inode.mtime,
        inode.atime,
    )
    return data.ljust(INODE_SIZE, b"\x00")
