# src/common/config.py
# Central configuration constants for the simulated filesystem

DISK_SIZE_MB: int = 10                  # total disk image size (changeable)
BLOCK_SIZE_BYTES: int = 512             # block size in bytes
INODE_COUNT: int = 256                  # number of inodes
INODE_SERIALIZED_BYTES: int = 128       # bytes per inode on disk
ROOT_INODE_NUMBER: int = 0

# Derived values (computed at mount time)
def compute_derived():
    TOTAL_BYTES = DISK_SIZE_MB * 1024 * 1024
    TOTAL_BLOCKS = TOTAL_BYTES // BLOCK_SIZE_BYTES
    INODE_TABLE_BYTES = INODE_COUNT * INODE_SERIALIZED_BYTES
    INODE_TABLE_BLOCKS = (INODE_TABLE_BYTES + BLOCK_SIZE_BYTES - 1) // BLOCK_SIZE_BYTES
    # bitmap blocks computed iteratively by Member 5 (persistence), helper below
    return {
        "TOTAL_BYTES": TOTAL_BYTES,
        "TOTAL_BLOCKS": TOTAL_BLOCKS,
        "INODE_TABLE_BYTES": INODE_TABLE_BYTES,
        "INODE_TABLE_BLOCKS": INODE_TABLE_BLOCKS
    }