# src/persistence/file_api.py

import struct
from src.persistence.mount import get_fs
from src.design.inode_serialisation import Inode, inode_to_bytes, FILE_TYPE_REGULAR, INODE_SIZE
from src.persistence.directory_entry import add_entry, remove_entry, list_entries, find_entry

def _inode_offset(inode_num: int) -> int:
    fs = get_fs()
    return fs.inode_start_block * fs.block_size + inode_num * INODE_SIZE

def allocate_inode() -> int:
    fs = get_fs()
    inode_table_start = fs.inode_start_block * fs.block_size
    with open(fs.disk_path, "r+b") as f:
        for inode_num in range(fs.inode_count):
            offset = inode_table_start + inode_num * INODE_SIZE
            f.seek(offset)
            raw = f.read(INODE_SIZE)
            if raw == b"\x00" * INODE_SIZE:
                return inode_num
    raise RuntimeError("No free inodes available")

def write_inode(inode_num: int, inode: Inode):
    fs = get_fs()
    offset = _inode_offset(inode_num)
    with open(fs.disk_path, "r+b") as f:
        f.seek(offset)
        f.write(inode_to_bytes(inode))

def read_inode(inode_num: int) -> bytes:
    fs = get_fs()
    offset = _inode_offset(inode_num)
    with open(fs.disk_path, "rb") as f:
        f.seek(offset)
        return f.read(INODE_SIZE)

def _allocate_data_block() -> int:
    fs = get_fs()
    bitmap_start = fs.bitmap_start_block * fs.block_size
    with open(fs.disk_path, "r+b") as f:
        for block in range(fs.data_start_block, fs.total_blocks):
            byte_index = block // 8
            bit_index = block % 8
            f.seek(bitmap_start + byte_index)
            cur = f.read(1)
            byte_val = cur[0] if cur else 0
            if not (byte_val & (1 << bit_index)):
                byte_val |= (1 << bit_index)
                f.seek(bitmap_start + byte_index)
                f.write(bytes([byte_val]))
                return block
    raise RuntimeError("No free data blocks available")

def create_file(path: str):
    fs = get_fs()
    if not path or path[0] != "/":
        raise ValueError("Path must be absolute")
    name = path.lstrip("/")

    if find_entry(name) is not None:
        raise FileExistsError(f"{path} already exists")

    inode_num = allocate_inode()
    inode = Inode(
        file_type=FILE_TYPE_REGULAR,
        size=0,
        direct_blocks=[-1]*12,
        single_indirect=-1, double_indirect=-1, triple_indirect=-1,
        link_count=1, uid=0, gid=0, mode=0o644,
        ctime=0, mtime=0, atime=0,
    )
    write_inode(inode_num, inode)
    add_entry(inode_num, name)
    print(f"[CREATE] File '{path}' created with inode #{inode_num}")

def delete_file(filename: str):
    ino = remove_entry(filename)
    fs = get_fs()
    offset = _inode_offset(ino)
    with open(fs.disk_path, "r+b") as f:
        f.seek(offset)
        f.write(b"\x00" * INODE_SIZE)
    print(f"[DELETE] File '{filename}' removed")

def list_files():
    return [name for _, name in list_entries()]

def write_file(filename: str, content: bytes):
    fs = get_fs()
    ino = find_entry(filename.lstrip("/"))
    if ino is None:
        raise FileNotFoundError(f"{filename} not found")

    inode_bytes = read_inode(ino)
    file_type, cur_size, *direct_blocks = struct.unpack("<I I 12i", inode_bytes[:56])
    block = direct_blocks[0]

    if block < 0:
        block = _allocate_data_block()
        direct_blocks[0] = block

    data = content[:fs.block_size]
    data = data.ljust(fs.block_size, b"\x00")
    with open(fs.disk_path, "r+b") as f:
        f.seek(block * fs.block_size)
        f.write(data)

    new_size = min(len(content), fs.block_size)
    packed = struct.pack("<I I 12i", file_type, new_size, *direct_blocks)
    new_inode = packed + inode_bytes[len(packed):]
    with open(fs.disk_path, "r+b") as f:
        f.seek(_inode_offset(ino))
        f.write(new_inode)
    print(f"[WRITE] {len(content)} bytes written to '{filename}'")

def read_file(filename: str) -> bytes:
    fs = get_fs()
    ino = find_entry(filename.lstrip("/"))
    if ino is None:
        raise FileNotFoundError(f"{filename} not found")

    inode_bytes = read_inode(ino)
    file_type, size, *direct_blocks = struct.unpack("<I I 12i", inode_bytes[:56])
    block = direct_blocks[0]
    if block < 0:
        return b""

    with open(fs.disk_path, "rb") as f:
        f.seek(block * fs.block_size)
        data = f.read(fs.block_size)
    return data[:size]