# Persistence Module Notes

### 📘 Overview
The Persistence Module simulates disk storage operations — creating, reading, writing, mounting, and unmounting a virtual disk file (`disk.img`).

---

### 🧱 Module Components

| File | Description |
|------|--------------|
| disk_io.py | Handles block-level read and write |
| disk_initializer.py | Creates disk.img and superblock |
| mount.py | Mounts disk and loads structures |
| unmount.py | Flushes metadata and unmounts |

---

### 🧩 Example Commands

```bash
# Step 1: Initialize Disk
python -m persistence.disk_initializer

# Step 2: Mount Disk
python -m persistence.mount

# Step 3: Write/Read a Block
python -m persistence.disk_io

# Step 4: Unmount Disk
python -m persistence.unmount
