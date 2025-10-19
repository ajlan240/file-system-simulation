# unmount.py
# ------------------------------------------
# Flush and save structures back to disk on unmount
# ------------------------------------------

import json
from persistence.disk_io import write_block

def unmount(metadata):
    """Flush in-memory metadata back to disk"""
    if not metadata.get("mounted"):
        print("[UNMOUNT] Disk is not mounted.")
        return

    print("[UNMOUNT] Flushing structures to disk...")
    meta_str = json.dumps(metadata).encode()
    write_block(1, meta_str)
    print("[UNMOUNT] Metadata saved to block 1.")
    print("[UNMOUNT] Disk unmounted successfully.")
