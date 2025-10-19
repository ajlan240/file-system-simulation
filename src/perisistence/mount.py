# mount.py
# ------------------------------------------
# Mounts the disk and loads superblock, inode, bitmap info
# ------------------------------------------

from persistence.disk_io import read_block

def mount():
    """Mount the disk and load necessary structures"""
    print("[MOUNT] Mounting disk...")
    data = read_block(0)
    if data:
        print("[MOUNT] Disk mounted successfully.")
        print("Superblock contents:", data.decode(errors="ignore").strip())
        return {"mounted": True, "superblock": data.decode(errors="ignore")}
    else:
        print("[MOUNT] Mount failed.")
        return {"mounted": False}
