# src/persistence/unmount.py
# Unmount and optionally flush any in-memory structures (placeholder).

from typing import Dict, Any

def unmount() -> None:
    """
    Unmount the disk. Higher layers (inode table, bitmap) should have flushed
    their state prior to calling this if needed.
    """
    from .mount import STATE
    if not STATE.get("mounted"):
        print("[UNMOUNT] Disk is not mounted.")
        return
    STATE["mounted"] = False
    print("[UNMOUNT] Disk unmounted.")
