# src/inode_directory/directory.py
# Root directory: filename -> inode number mapping, persisted in a single data block.

import json
from typing import Dict, Optional
from src.persistence.mount import STATE
from src.persistence.disk_io import read_block, write_block
from src.block_bitmap.block_allocator import allocate_block
from src.design.architecture import DirectoryEntry

class DirectoryStore:
    """
    A simple directory store that persists a map of {filename: inode_number} in one block.
    For production FS, directory entries would be stored in multiple blocks; this keeps it simple.
    """

    def __init__(self):
        self._entries: Dict[str, int] = {}

    def _require_mounted(self):
        if not STATE.get("mounted") or STATE.get("superblock") is None:
            raise RuntimeError("Disk not mounted. Call mount() first.")

    def _dir_block_num(self) -> int:
        sb = STATE["superblock"]
        # Use root_inode_number's first direct block as the directory storage block.
        # If the root doesn't have a block yet, allocate one.
        if sb.root_inode_number == 0:
            # We require a root inode to be prepared by higher-level init; keeping 0 as root for simplicity.
            pass
        return self._ensure_root_dir_block()

    def _ensure_root_dir_block(self) -> int:
        """
        Ensure there is a dedicated block to store directory entries.
        We stash its block number into the superblock data region by writing the first data block number
        into block 'bitmap_start_block - 1' as a tiny metadata hack (kept simple).
        For better design, store it in the root inode's direct_blocks; here we assume higher layer will do it.
        """
        # Minimal approach: read block right before bitmap region to hold a 4-byte pointer (not ideal but simple).
        sb = STATE["superblock"]
        pointer_block = sb.bitmap_start_block - 1
        buf = read_block(pointer_block)
        # First 4 bytes as little-endian integer pointer to the directory block
        dir_block = int.from_bytes(buf[0:4], byteorder="little")
        if dir_block == 0:
            dir_block = allocate_block()
            newbuf = bytearray(buf)
            newbuf[0:4] = int(dir_block).to_bytes(4, byteorder="little")
            write_block(pointer_block, bytes(newbuf), offset=0)
        return dir_block

    def load(self) -> None:
        """
        Load directory entries from its block as JSON.
        """
        self._require_mounted()
        bnum = self._dir_block_num()
        raw = read_block(bnum)
        try:
            # Strip trailing zeros and decode
            data = raw.rstrip(b"\x00")
            if not data:
                self._entries = {}
                return
            obj = json.loads(data.decode("utf-8"))
            self._entries = {str(k): int(v) for (k, v) in obj.items()}
        except Exception:
            # If corrupt, start empty
            self._entries = {}

    def _flush(self) -> None:
        """
        Persist directory map as JSON to the directory block.
        """
        bnum = self._dir_block_num()
        sb = STATE["superblock"]
        payload = json.dumps(self._entries).encode("utf-8")
        if len(payload) > sb.block_size_bytes:
            raise ValueError("Directory entries exceed a single block")
        write_block(bnum, payload, offset=0)

    def add_entry(self, filename: str, inode_number: int) -> None:
        if filename in self._entries:
            raise FileExistsError("File already exists")
        self._entries[filename] = inode_number
        self._flush()

    def remove_entry(self, filename: str) -> None:
        if filename not in self._entries:
            raise FileNotFoundError("File not found")
        del self._entries[filename]
        self._flush()

    def resolve(self, filename: str) -> Optional[int]:
        return self._entries.get(filename)

    def list_entries(self):
        return list(self._entries.items())