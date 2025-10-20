import struct
from src.persistence.mount import get_fs

ENTRY_SIZE = 64
FMT = "<I60s"

def _root_block() -> int:
    fs = get_fs()
    return fs.data_start_block  # root’s first data block

def add_entry(inode_num: int, filename: str):
    fs = get_fs()
    block = _root_block()
    target = filename.lstrip("/")
    with open(fs.disk_path, "r+b") as f:
        f.seek(block * fs.block_size)
        data = f.read(fs.block_size)
        for i in range(0, fs.block_size, ENTRY_SIZE):
            entry = data[i:i+ENTRY_SIZE]
            if len(entry) < ENTRY_SIZE:
                break
            ino, name = struct.unpack(FMT, entry)
            if ino == 0:
                f.seek(block * fs.block_size + i)
                name_bytes = target.encode()[:60].ljust(60, b"\x00")
                f.write(struct.pack(FMT, inode_num, name_bytes))
                return
    raise RuntimeError("No free directory entries in root")

def list_entries():
    fs = get_fs()
    block = _root_block()
    entries = []
    with open(fs.disk_path, "rb") as f:
        f.seek(block * fs.block_size)
        data = f.read(fs.block_size)
        for i in range(0, fs.block_size, ENTRY_SIZE):
            entry = data[i:i+ENTRY_SIZE]
            if len(entry) < ENTRY_SIZE:
                break
            ino, name = struct.unpack(FMT, entry)
            if ino != 0:
                entries.append((ino, name.decode().strip("\x00")))
    return entries

def find_entry(filename: str) -> int | None:
    target = filename.lstrip("/")
    for ino, name in list_entries():
        if name == target:
            return ino
    return None

def remove_entry(filename: str) -> int:
    fs = get_fs()
    block = _root_block()
    target = filename.lstrip("/")
    with open(fs.disk_path, "r+b") as f:
        f.seek(block * fs.block_size)
        data = f.read(fs.block_size)
        for i in range(0, fs.block_size, ENTRY_SIZE):
            entry = data[i:i+ENTRY_SIZE]
            if len(entry) < ENTRY_SIZE:
                break
            ino, name = struct.unpack(FMT, entry)
            if ino != 0 and name.decode().strip("\x00") == target:
                f.seek(block * fs.block_size + i)
                f.write(b"\x00" * ENTRY_SIZE)
                return ino
    raise FileNotFoundError(f"{filename} not found in directory")