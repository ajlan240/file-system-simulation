from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

# Superblock definition (logical)
@dataclass
class Superblock:
    total_size_bytes: int
    block_size_bytes: int
    total_blocks: int
    inode_count: int
    inode_table_blocks: int
    bitmap_blocks: int
    inode_start_block: int
    bitmap_start_block: int
    data_start_block: int
    version: int = 1
    magic: int = 0xF1F51          # fixed
    checksum: Optional[int] = None

# Inode logical structure
@dataclass
class Inode:
    inode_number: int
    file_type: str                # 'file' or 'directory'
    file_size: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    direct_blocks: List[Optional[int]] = field(default_factory=lambda: [None]*10)
    indirect_block: Optional[int] = None

# Directory entry logical structure
@dataclass
class DirectoryEntry:
    filename: str
    inode_number: int
    flags: int = 1                # 1 = active

# ---- High-level interface contracts (implementers must follow) ----
# inode_directory
def allocate_inode() -> Inode:
    raise NotImplementedError()

def free_inode(inode_number: int) -> None:
    raise NotImplementedError()

def get_inode(inode_number: int) -> Inode:
    raise NotImplementedError()

def update_inode(inode: Inode) -> None:
    raise NotImplementedError()

def add_entry(filename: str, inode_number: int) -> None:
    raise NotImplementedError()

def remove_entry(filename: str) -> None:
    raise NotImplementedError()

def resolve(filename: str) -> Optional[int]:
    raise NotImplementedError()

# block_bitmap
def allocate_block() -> int:
    raise NotImplementedError()

def free_block(block_num: int) -> None:
    raise NotImplementedError()

def is_allocated(block_num: int) -> bool:
    raise NotImplementedError()

# persistence
def mount(disk_path: str = "disk.img") -> None:
    raise NotImplementedError()

def unmount() -> None:
    raise NotImplementedError()

def read_block(block_num: int) -> bytes:
    raise NotImplementedError()

def write_block(block_num: int, data: bytes, offset: int = 0) -> None:
    raise NotImplementedError()

# file_api
def create_file(filename: str) -> bool:
    raise NotImplementedError()

def delete_file(filename: str) -> bool:
    raise NotImplementedError()

def list_files() -> List[str]:
    raise NotImplementedError()

# fileio
def read_from_file(filename: str, offset: int, size: int) -> bytes:
    raise NotImplementedError()

def write_to_file(filename: str, offset: int, data: bytes) -> int:
    raise NotImplementedError()
