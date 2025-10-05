# docs/design_document.md
Member 1 - Comprehensive design summary

## Overview
This document defines the on-disk layout, metadata structures, and interface contracts for the File System Simulator.

## Disk layout
- Superblock (block 0)
- Inode table (blocks 1..N)
- Bitmap (next M blocks)
- Data blocks (remaining)

## Superblock fields
(total_size_bytes, block_size_bytes, total_blocks, inode_count, inode_table_blocks, bitmap_blocks, inode_start_block, bitmap_start_block, data_start_block, root_inode_number)

## Inode format
- Serialized to 128 bytes.
- Fields: inode_number, type, file_size, timestamps, 10 direct pointers, 1 indirect pointer.

## Directory format
- Fixed-size entries, each contains filename (UTF-8, fixed 64 bytes), inode_number (4 bytes), flags (1 byte), padding to ENTRY_SIZE.
- Directory content stored in data blocks of the directory inode.

## Bitmap
- Covers data blocks only. 1 bit per block. Stored in packed bytes in bitmap region.

## Interfaces
See src/design/architecture.py for dataclasses and function signatures.

## Invariants and semantics
- Root inode (0) exists and is directory.
- No shared data blocks between files; delete frees blocks.
- Reads beyond EOF return truncated result or empty bytes.
- Writes allocate blocks as needed.

## Testing
- Unit tests for each module.
- Integration tests: create -> write -> read -> delete flows.
- Edge cases: partial block writes, indirect allocation, full disk conditions.

## Implementation notes
- Persistence (Member 5) computes bitmap_blocks iteratively and initializes structures.
- Serialization helpers in src/design assist implementers.