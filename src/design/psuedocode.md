# src/design/pseudocode.md
High-level pseudocode for implementers (Member 1 deliverable).

## Helpers
- BLOCK_SIZE = config.BLOCK_SIZE_BYTES
- read_block(block_num) -> bytes (block-sized)
- write_block(block_num, bytes, offset=0)

## locate_block(inode, logical_index)
1. if logical_index < len(inode.direct_blocks):
   return inode.direct_blocks[logical_index]
2. else:
   if inode.indirect_block is None: return None
   table = read_block_as_ints(inode.indirect_block)
   return table[logical_index - len(inode.direct_blocks)]

## ensure_block(inode, logical_index)
1. bnum = locate_block(inode, logical_index)
2. if bnum is not None: return bnum
3. new_b = allocate_block()
4. if logical_index < len(inode.direct_blocks):
   inode.direct_blocks[logical_index] = new_b
   else:
   if inode.indirect_block is None:
   inode.indirect_block = allocate_block()  # pointer table
   write_empty_int_table(inode.indirect_block)
   table = read_block_as_ints(inode.indirect_block)
   table[logical_index - len(inode.direct_blocks)] = new_b
   write_int_table(inode.indirect_block, table)
5. update_inode(inode)
6. return new_b

## create_file(filename)
- if resolve(filename) != None: return False
- inode = allocate_inode()
- inode.file_type = 'file'
- inode.file_size = 0
- update_inode(inode)
- add_entry(filename, inode.inode_number)
- return True

## delete_file(filename)
- inum = resolve(filename)
- if inum is None: return False
- inode = get_inode(inum)
- for b in inode.direct_blocks: if b: free_block(b)
- if inode.indirect_block:
  table = read_block_as_ints(inode.indirect_block)
  for b in table: if b: free_block(b)
  free_block(inode.indirect_block)
- remove_entry(filename)
- free_inode(inum)
- return True

## read_from_file(filename, offset, size)
- inum = resolve(filename); inode = get_inode(inum)
- if offset >= inode.file_size: return b''
- size = min(size, inode.file_size - offset)
- res = bytearray()
- cursor = offset
- remaining = size
- while remaining > 0:
  bi = cursor // BLOCK_SIZE
  bo = cursor % BLOCK_SIZE
  block = locate_block(inode, bi)
  if block is None: break
  data = read_block(block)
  take = min(remaining, BLOCK_SIZE - bo)
  res += data[bo:bo+take]
  remaining -= take; cursor += take
- return bytes(res)

## write_to_file(filename, offset, data)
- inum = resolve(filename); inode = get_inode(inum)
- written = 0; cursor = offset; remaining = len(data)
- while remaining > 0:
  bi = cursor // BLOCK_SIZE
  bo = cursor % BLOCK_SIZE
  bnum = ensure_block(inode, bi)
  take = min(remaining, BLOCK_SIZE - bo)
  if take < BLOCK_SIZE:
  buf = bytearray(read_block(bnum))
  buf[bo:bo+take] = data[written:written+take]
  write_block(bnum, bytes(buf), offset=0)
  else:
  write_block(bnum, data[written:written+take], offset=bo)
  written += take; remaining -= take; cursor += take
- inode.file_size = max(inode.file_size, offset + written)
- update_inode(inode)
- return written