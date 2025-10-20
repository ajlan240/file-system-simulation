# src/inode_directory/resolver.py
# High-level functions matching architecture contracts, delegating to inode table and directory store.

from typing import Optional, List
from src.design.architecture import Inode
from .inode_table import allocate_inode as _alloc_inode, free_inode as _free_inode
from .inode_table import get_inode as _get_inode, update_inode as _update_inode
from .directory import DirectoryStore

_dir = DirectoryStore()

def allocate_inode() -> Inode:
    inode = _alloc_inode()
    return inode

def free_inode(inode_number: int) -> None:
    _free_inode(inode_number)

def get_inode(inode_number: int) -> Inode:
    return _get_inode(inode_number)

def update_inode(inode: Inode) -> None:
    _update_inode(inode)

def add_entry(filename: str, inode_number: int) -> None:
    _dir.load()
    _dir.add_entry(filename, inode_number)

def remove_entry(filename: str) -> None:
    _dir.load()
    _dir.remove_entry(filename)

def resolve(filename: str) -> Optional[int]:
    _dir.load()
    return _dir.resolve(filename)

def list_files() -> List[str]:
    _dir.load()
    return [name for name, _ in _dir.list_entries()]