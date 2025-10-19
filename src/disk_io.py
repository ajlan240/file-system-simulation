# disk_io.py
# ------------------------------------------
# Handles low-level read_block() and write_block() operations
# ------------------------------------------

BLOCK_SIZE = 512
DISK_FILE = "disk.img"

def read_block(block_number):
    """Read a block of data from disk.img file"""
    try:
        with open(DISK_FILE, "rb") as f:
            f.seek(block_number * BLOCK_SIZE)
            data = f.read(BLOCK_SIZE)
            print(f"[READ] Block {block_number} read.")
            return data
    except FileNotFoundError:
        print("[ERROR] Disk image not found. Initialize it first.")
        return None

def write_block(block_number, data):
    """Write a block of data to disk.img file"""
    if len(data) > BLOCK_SIZE:
        raise ValueError("Data exceeds block size of 512 bytes.")
    try:
        with open(DISK_FILE, "r+b") as f:
            f.seek(block_number * BLOCK_SIZE)
            f.write(data.ljust(BLOCK_SIZE, b'\x00'))
            print(f"[WRITE] Block {block_number} written.")
    except FileNotFoundError:
        print("[ERROR] Disk image not found. Initialize it first.")
