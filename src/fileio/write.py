def write_to_file(filename, offset, data):
    with open(filename, 'r+b') as f:
        f.seek(offset)
        f.write(data)
