import src.persistence.mount as mount_mod

def unmount():
    if mount_mod._fs is None:
        print("[INFO] Filesystem not mounted.")
        return
    mount_mod._fs = None
    print("[INFO] Filesystem unmounted.")