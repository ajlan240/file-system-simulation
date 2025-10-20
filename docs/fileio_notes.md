# File I/O Module Notes

## read.py
- `read_from_file(filename, offset, size)`
  - Reads `size` bytes from `filename` starting at `offset`.

## write.py
- `write_to_file(filename, offset, data)`
  - Writes `data` to `filename` at given `offset`.

## offset_mapper.py
- Maps logical offset to block index using block size.
