# Bitmap design notes

- The block allocation bitmap uses 1 bit per block.
- It is stored in the region defined by the superblock:
    - `bitmap_start_block` (start)
    - `bitmap_blocks` (length)
- Reserved regions are always marked allocated:
    - Block 0 (superblock)
    - Inode table region
    - Bitmap region (self)
- Allocation strategy:
    - First-fit from `data_start_block` forward.
    - This ensures data blocks are preferred and reserved regions are never allocated.
- API (as per Member 1 contracts):
    - `allocate_block() -> int`
    - `free_block(block_num: int) -> None`
    - `is_allocated(block_num: int) -> bool`