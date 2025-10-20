# src/block_bitmap/__init__.py

from .block_allocator import allocate_block, free_block, is_allocated
from .bitmap import ensure_bitmap_loaded, mark_reserved_regions