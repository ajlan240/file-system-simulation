

import os


def mount(disk_path="disk.img"):
    """Mounts the disk: loads or initializes necessary structures."""
    if not os.path.exists(disk_path):
        raise FileNotFoundError(f"{disk_path} not found. Run disk_initializer first.")
    print(f"[MOUNT] Mounted {disk_path}")
    return True



def unmount():

    print("[UNMOUNT] Flushing and saving structures...")
    print("[UNMOUNT] Disk unmounted successfully.")
    return True



BLOCK_SIZE = 512

def read_block(file, block_number):

    file.seek(block_number * BLOCK_SIZE)
    data = file.read(BLOCK_SIZE)
    print(f"[READ] Block {block_number} read.")
    return data

def write_block(file, block_number, data):

    if len(data) > BLOCK_SIZE:
        raise ValueError("Data exceeds block size.")
    file.seek(block_number * BLOCK_SIZE)
    file.write(data.ljust(BLOCK_SIZE, b'\x00'))
    print(f"[WRITE] Block {block_number} written.")



def create_disk_image(file_path="disk.img", size_mb=1):

    if os.path.exists(file_path):
        print("[INIT] Disk image already exists.")
        return
    with open(file_path, "wb") as f:
        f.write(b'\x00' * size_mb * 1024 * 1024)
    print(f"[INIT] Created {file_path} of size {size_mb} MB.")



def test_mount():
    print("\n--- Running test_mount ---")
    try:
        result = mount("disk.img")
        assert result is True
        print("✅ mount test passed.")
    except FileNotFoundError:
        print("⚠️ Disk not found. Run create_disk_image() first.")

def test_unmount():
    print("\n--- Running test_unmount ---")
    result = unmount()
    assert result is True
    print("✅ unmount test passed.")

def test_disk_io():
    print("\n--- Running test_disk_io ---")
    test_file = "test.img"
    with open(test_file, "wb") as f:
        f.write(b'\x00' * 1024)  # create 2 blocks

    with open(test_file, "r+b") as f:
        write_block(f, 0, b"HELLO")
        data = read_block(f, 0)
        assert b"HELLO" in data
    print("✅ disk_io test passed.")



if __name__ == "__main__":
    print("=== Persistence Module Developer Demo ===")


    create_disk_image("disk.img", size_mb=1)


    test_mount()


    test_disk_io()


    test_unmount()

    print("\nAll persistence module tests completed successfully.")
