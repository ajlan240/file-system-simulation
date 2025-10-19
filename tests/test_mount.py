# test_mount.py
from persistence import mount

def test_mount():
    result = mount.mount()
    assert result["mounted"]
    print("[TEST] Mount test passed.")
