# tests/fileio/test_file_io.py
import os
import pytest
from src.persistence.disk_initializer import initialize_disk
from src.persistence.mount import mount
from src.block_bitmap.bitmap import mark_reserved_regions
from src.file_api.create import create_file
from src.fileio import open_file, close_file, read_file, write_file, seek_file

def setup_disk(tmp_path):
    disk_path = tmp_path / "disk.img"
    initialize_disk(str(disk_path), total_blocks=128, block_size_bytes=256, inode_count=16)
    mount(str(disk_path))
    mark_reserved_regions()
    return disk_path

def test_open_read_write_seek_close(tmp_path):
    setup_disk(tmp_path)
    create_file("alpha")
    fd = open_file("alpha", "rw")
    assert isinstance(fd, int)

    # write
    written = write_file(fd, b"hello world")
    assert written == len(b"hello world")

    # seek and read
    seek_file(fd, 6, whence=0)  # start
    out = read_file(fd, 5)
    assert out == b"world"

    # append
    seek_file(fd, 0, whence=2)  # end
    write_file(fd, b"!!!")
    seek_file(fd, 0, whence=0)
    final = read_file(fd, 14)
    assert final == b"hello world!!!"

    close_file(fd)

def test_write_with_holes_cross_block(tmp_path):
    setup_disk(tmp_path)
    create_file("beta")
    fd = open_file("beta", "rw")

    # write at offset beyond current end; first seek to end then seek further to create a hole
    seek_file(fd, 0, whence=2)  # end (0)
    seek_file(fd, 300, whence=1)  # move forward 300 bytes
    data = b"XYZ"
    write_file(fd, data)

    # read back around the region
    seek_file(fd, 300, whence=0)
    out = read_file(fd, 3)
    assert out == b"XYZ"

    close_file(fd)

def test_permissions(tmp_path):
    setup_disk(tmp_path)
    create_file("gamma")
    fd_r = open_file("gamma", "r")
    with pytest.raises(PermissionError):
        write_file(fd_r, b"x")
    close_file(fd_r)

    fd_w = open_file("gamma", "w")
    with pytest.raises(PermissionError):
        read_file(fd_w, 1)
    close_file(fd_w)

def test_invalid_fd(tmp_path):
    setup_disk(tmp_path)
    with pytest.raises(ValueError):
        read_file(999, 10)
    with pytest.raises(ValueError):
        close_file(999)