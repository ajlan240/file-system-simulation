def read_from_file(filename, offset, size):
    with open(filename, 'rb') as f:
        f.seek(offset)
        return f.read(size)
