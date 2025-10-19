# disk_initializer.py
# ------------------------------------------
# Creates disk.img file if missing and writes superblock
# ------------------------------------------

import os
from persistence.disk_io import BLOCK_SIZE, DISK_FILE, write_block

def initialize_disk(num_blocks=100):
    """Create a disk image and initialize with superblock"""
    if os.path.exists(DISK_FILE):
        print("[INFO] Disk image already exists.")
        return

    with open(DISK_FILE, "wb") as f:
        f.write(b'\x00' * BLOCK_SIZE * num_blocks)
    print(f"[INIT] Created {DISK_FILE} with {num_blocks} blocks ({num_blocks * BLOCK_SIZE} bytes).")

    superblock = b"SUPERBLOCK: Disk initialized successfully"
    write_block(0, superblock)
    print("[INIT] Superblock written to block 0.")
