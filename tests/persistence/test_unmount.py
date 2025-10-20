# test_unmount.py
from persistence import unmount

def test_unmount():
    metadata = {"mounted": True, "info": "Unmount test run"}
    unmount.unmount(metadata)
    print("[TEST] Unmount test passed.")
