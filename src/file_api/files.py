# src/file_api/files.py
# File metadata, listing, and content I/O on the simulated filesystem.

from typing import Dict, List, Optional, Tuple
from src.persistence.mount import STATE
from src.persistence.disk_io import read_block, write_block
from src.inode_directory.resolver import (
    resolve,
    get_inode,
    update_inode,
    list_files as _list_files,
    remove_entry,
)
from src.block_bitmap.block_allocator import allocate_block, free_block

def _require_mounted():
    if not STATE.get("mounted"):
        raise RuntimeError("Disk not mounted. Call mount() first.")

def _block_size() -> int:
    return STATE["superblock"].block_size_bytes

def _max_direct(inode) -> int:
    # Use existing length of direct_blocks as capacity; if empty, set a default (e.g., 12).
    if hasattr(inode, "direct_blocks") and inode.direct_blocks is not None and len(inode.direct_blocks) > 0:
        return len(inode.direct_blocks)
    # If no pre-sized list, assume a classic small number of direct pointers
    return 12

def list_files() -> List[str]:
    """
    List filenames from the simulated directory store.
    """
    _require_mounted()
    return _list_files()

def get_file_metadata(filename: str) -> Dict:
    """
    Return metadata from inode: size, type, block pointers.
    """
    _require_mounted()
    inum = resolve(filename)
    if inum is None:
        return {"error": "file not found"}

    inode = get_inode(inum)
    return {
        "inode_number": inode.inode_number,
        "file_type": getattr(inode, "file_type", "file"),
        "size_bytes": getattr(inode, "file_size", 0),
        "direct_blocks": list(getattr(inode, "direct_blocks", []) or []),
        "has_indirect": getattr(inode, "indirect_block", None) is not None,
    }

def _ensure_direct_capacity(inode, needed_blocks: int) -> None:
    """
    Ensure inode.direct_blocks has capacity for 'needed_blocks'.
    If not, extend with None placeholders.
    """
    if not hasattr(inode, "direct_blocks") or inode.direct_blocks is None:
        inode.direct_blocks = []
    while len(inode.direct_blocks) < needed_blocks:
        inode.direct_blocks.append(None)

def _allocate_blocks_for_size(inode, size_bytes: int) -> List[int]:
    """
    Allocate enough direct blocks to hold 'size_bytes', return block list.
    Does not handle indirect blocks for now (simplified).
    """
    bs = _block_size()
    blocks_needed = (size_bytes + bs - 1) // bs if size_bytes > 0 else 0
    if blocks_needed == 0:
        return []

    # Respect a simple direct-only policy
    capacity = max(_max_direct(inode), blocks_needed)
    _ensure_direct_capacity(inode, capacity)

    allocated: List[int] = []
    for i in range(blocks_needed):
        if inode.direct_blocks[i] is None:
            b = allocate_block()
            inode.direct_blocks[i] = b
        allocated.append(inode.direct_blocks[i])
    return allocated

def write_file(filename: str, data: bytes) -> None:
    """
    Write data bytes to a file in the simulated FS.
    Overwrites previous content (truncate + write).
    """
    _require_mounted()
    inum = resolve(filename)
    if inum is None:
        raise FileNotFoundError(f"'{filename}' not found")

    inode = get_inode(inum)
    if getattr(inode, "file_type", "file") != "file":
        raise IsADirectoryError(f"'{filename}' is a directory")

    # Free old blocks first (truncate)
    _truncate_inode_blocks(inode)

    # Allocate new blocks to fit data
    bs = _block_size()
    blocks = _allocate_blocks_for_size(inode, len(data))

    # Write data across blocks
    cursor = 0
    for i, bnum in enumerate(blocks):
        chunk = data[cursor:cursor + bs]
        # Write the chunk at offset 0 of the block
        write_block(bnum, chunk, offset=0)
        cursor += len(chunk)

    inode.file_size = len(data)
    update_inode(inode)

def read_file(filename: str) -> bytes:
    """
    Read and return the file content from the simulated FS.
    """
    _require_mounted()
    inum = resolve(filename)
    if inum is None:
        raise FileNotFoundError(f"'{filename}' not found")

    inode = get_inode(inum)
    if getattr(inode, "file_type", "file") != "file":
        raise IsADirectoryError(f"'{filename}' is a directory")

    bs = _block_size()
    size = getattr(inode, "file_size", 0)
    if size == 0:
        return b""

    chunks: List[bytes] = []
    remaining = size
    for bnum in getattr(inode, "direct_blocks", []) or []:
        if bnum is None or remaining <= 0:
            break
        raw = read_block(bnum)
        take = min(bs, remaining)
        chunks.append(raw[:take])
        remaining -= take

    return b"".join(chunks)

def truncate_file(filename: str) -> None:
    """
    Truncate file to zero length and free its data blocks.
    """
    _require_mounted()
    inum = resolve(filename)
    if inum is None:
        raise FileNotFoundError(f"'{filename}' not found")
    inode = get_inode(inum)
    if getattr(inode, "file_type", "file") != "file":
        raise IsADirectoryError(f"'{filename}' is a directory")

    _truncate_inode_blocks(inode)
    inode.file_size = 0
    update_inode(inode)

def _truncate_inode_blocks(inode) -> None:
    """
    Free all direct blocks of the inode.
    """
    if not hasattr(inode, "direct_blocks") or inode.direct_blocks is None:
        return
    for b in inode.direct_blocks:
        if b is not None:
            free_block(b)
    inode.direct_blocks = []

def delete_file(filename: str) -> None:
    """
    Delete a file (or empty directory) from the simulated FS:
    - For files: free data blocks, zero size, remove directory entry, free inode.
    - For directories: only allow if empty (enforced at higher layers).
    """
    _require_mounted()
    inum = resolve(filename)
    if inum is None:
        raise FileNotFoundError(f"'{filename}' not found")

    inode = get_inode(inum)
    if getattr(inode, "file_type", "file") == "file":
        _truncate_inode_blocks(inode)
        inode.file_size = 0
        update_inode(inode)
    # Remove from directory
    remove_entry(filename)
    # Free inode record
    from src.inode_directory.inode_table import free_inode
    free_inode(inum)