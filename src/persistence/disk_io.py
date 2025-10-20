# src/persistence/disk_io.py
# Safe block-level read/write with guard rails.

import os

class DiskIO:
    def __init__(self, disk_path: str, total_blocks: int, block_size: int):
        self.disk_path = disk_path
        self.total_blocks = total_blocks
        self.block_size = block_size
        self._fh = None

    def open(self):
        if not os.path.exists(self.disk_path):
            raise FileNotFoundError(f"Disk image not found: {self.disk_path}")
        self._fh = open(self.disk_path, "r+b")

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None

    def _seek_block(self, block_number: int):
        if block_number < 0 or block_number >= self.total_blocks:
            raise ValueError(f"Invalid block number {block_number}")
        offset = block_number * self.block_size
        self._fh.seek(offset)

    def read_block(self, block_number: int) -> bytes:
        self._seek_block(block_number)
        data = self._fh.read(self.block_size)
        if len(data) != self.block_size:
            raise IOError("Short read from disk image")
        return data

    def write_block(self, block_number: int, data: bytes):
        if len(data) != self.block_size:
            raise ValueError("Data length must equal block size")
        self._seek_block(block_number)
        self._fh.write(data)
        self._fh.flush()