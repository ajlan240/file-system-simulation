import math
import os
from src.design.superblock_serialisation import SuperblockLayout, to_bytes
from src.design.inode_serialisation import INODE_SIZE, Inode, inode_to_bytes, FILE_TYPE_DIR

DEFAULT_DISK_PATH = "disk.img"
DEFAULT_TOTAL_BLOCKS = 2048
DEFAULT_BLOCK_SIZE = 512
DEFAULT_INODE_COUNT = 256

def _compute_layout(total_blocks, block_size_bytes, inode_count):
    inode_table_bytes = inode_count * INODE_SIZE
    inode_table_blocks = math.ceil(inode_table_bytes / block_size_bytes)

    bitmap_bytes = math.ceil(total_blocks / 8)
    bitmap_blocks = math.ceil(bitmap_bytes / block_size_bytes)

    inode_start_block = 1
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
        checksum=0,
    )

def initialize_disk(disk_path=DEFAULT_DISK_PATH, total_blocks=DEFAULT_TOTAL_BLOCKS,
                    block_size_bytes=DEFAULT_BLOCK_SIZE, inode_count=DEFAULT_INODE_COUNT):
    sb = _compute_layout(total_blocks, block_size_bytes, inode_count)

    if os.path.dirname(disk_path):
        os.makedirs(os.path.dirname(disk_path), exist_ok=True)

    with open(disk_path, "wb") as f:
        f.truncate(total_blocks * block_size_bytes)

    # Write superblock
    sb_bytes = to_bytes(sb)
    if len(sb_bytes) > sb.block_size_bytes:
        raise ValueError("Superblock bytes exceed block size")
    sb_block = sb_bytes.ljust(sb.block_size_bytes, b"\x00")
    with open(disk_path, "r+b") as f:
        f.seek(0)
        f.write(sb_block)

    # Zero inode table + bitmap
    zero_block = b"\x00" * sb.block_size_bytes
    with open(disk_path, "r+b") as f:
        for i in range(sb.inode_table_blocks):
            f.seek((sb.inode_start_block + i) * sb.block_size_bytes)
            f.write(zero_block)
        for i in range(sb.bitmap_blocks):
            f.seek((sb.bitmap_start_block + i) * sb.block_size_bytes)
            f.write(zero_block)

    # Initialize root inode (reserve first data block for root directory)
    root_first_block = sb.data_start_block
    root_inode = Inode(
        file_type=FILE_TYPE_DIR,
        size=0,
        direct_blocks=[root_first_block] + [-1] * 11,
        single_indirect=-1,
        double_indirect=-1,
        triple_indirect=-1,
        link_count=1,
        uid=0,
        gid=0,
        mode=0o755,
        ctime=0, mtime=0, atime=0
    )
    inode_offset = sb.inode_start_block * sb.block_size_bytes
    with open(disk_path, "r+b") as f:
        f.seek(inode_offset)
        f.write(inode_to_bytes(root_inode))

    print(f"[INIT] Disk created at {disk_path}")
    print(f"[INIT] Blocks: {sb.total_blocks}, Block size: {sb.block_size_bytes} bytes")
    print(f"[INIT] Data starts at block: {sb.data_start_block}")
    print(f"[INIT] Root inode initialized at #{sb.root_inode_number}")

    return sb

if __name__ == "__main__":
    initialize_disk()