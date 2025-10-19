# test_disk_io.py
from persistence import disk_io

def test_disk_io():
    data = b"HelloPersistence"
    disk_io.write_block(2, data)
    read_data = disk_io.read_block(2)
    assert data in read_data
    print("[TEST] Disk I/O test passed.")
