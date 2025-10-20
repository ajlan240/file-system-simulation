
# src/fileio/offset_mapper.py
# Helpers to map logical byte offsets to block indices and in-block offsets.

def logical_to_block_index(offset: int, block_size: int) -> int:
    """
    Map a logical byte offset to the index of the block it falls into.
    """
    if offset < 0:
        raise ValueError("offset must be non-negative")
    return offset // block_size

def logical_to_block_inner_offset(offset: int, block_size: int) -> int:
    """
    Map a logical byte offset to its position within a block.
    """
    if offset < 0:
        raise ValueError("offset must be non-negative")
    return offset % block_size