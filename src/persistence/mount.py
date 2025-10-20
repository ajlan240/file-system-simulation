from dataclasses import dataclass
from src.design.superblock_serialisation import from_bytes as superblock_from_bytes

@dataclass
class FSContext:
    disk_path: str
    total_blocks: int
    block_size: int
    inode_count: int
    inode_start_block: int
    bitmap_start_block: int
    data_start_block: int
    root_inode_number: int

_fs: FSContext | None = None

def mount(disk_path: str):
    global _fs
    if _fs is not None:
        print("[INFO] Filesystem already mounted.")
        return

    # Read superblock (block 0) assuming 512 for bootstrap, then trust superblock values
    with open(disk_path, "rb") as f:
        raw = f.read(512)
    sb = superblock_from_bytes(raw)

    _fs = FSContext(
        disk_path=disk_path,
        total_blocks=sb.total_blocks,
        block_size=sb.block_size_bytes,
        inode_count=sb.inode_count,
        inode_start_block=sb.inode_start_block,
        bitmap_start_block=sb.bitmap_start_block,
        data_start_block=sb.data_start_block,
        root_inode_number=sb.root_inode_number,
    )
    print(f"[INFO] Mounted disk: {sb.total_blocks} blocks, {sb.block_size_bytes} B/block")

def get_fs() -> FSContext:
    if _fs is None:
        raise RuntimeError("Filesystem not mounted")
    return _fs