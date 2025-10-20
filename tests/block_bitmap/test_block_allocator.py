# tests/block_bitmap/test_block_allocator.py
# Basic tests for allocation/free flow. Requires a mounted, initialized disk.

import os
import tempfile
from src.persistence.disk_initializer import initialize_disk
from src.persistence.mount import mount, STATE
from src.block_bitmap.block_allocator import allocate_block, free_block, is_allocated

def test_allocate_and_free_block():
    with tempfile.TemporaryDirectory() as tmp:
        disk_path = os.path.join(tmp, "disk.img")
        sb = initialize_disk(disk_path=disk_path, total_blocks=256, block_size_bytes=512, inode_count=32)
        mount(disk_path)

        # Allocate a few blocks
        b1 = allocate_block()
        b2 = allocate_block()
        assert b1 != b2
        assert is_allocated(b1)
        assert is_allocated(b2)

        # Free one block
        free_block(b1)
        assert not is_allocated(b1)
        assert is_allocated(b2)