import os
from src.persistence.disk_initializer import initialize_disk
from src.persistence.mount import mount
from src.persistence.unmount import unmount
from .command_parser import parse_command
from .command_executor import execute_command

DISK_PATH = "disk.img"

def run_cli():
    # Ensure disk exists
    if not os.path.exists(DISK_PATH):
        print("[INFO] No disk image found. Initializing a new one...")
        initialize_disk(DISK_PATH)

    # Mount the disk
    try:
        mount(DISK_PATH)
        print("[INFO] Filesystem mounted successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to mount filesystem: {e}")
        return

    print("Welcome to the Mini File System Simulator CLI. Type 'help' for commands.")

    while True:
        try:
            raw = input("fs> ").strip()
            if not raw:
                continue

            if raw in ("exit", "quit"):
                print("Unmounting filesystem and exiting...")
                try:
                    unmount()
                except Exception as e:
                    print(f"[WARNING] Failed to unmount cleanly: {e}")
                break

            cmd, args = parse_command(raw)
            if cmd is None:
                continue

            execute_command(cmd, args)

        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt detected. Exiting...")
            try:
                unmount()
            except Exception as e:
                print(f"[WARNING] Failed to unmount cleanly: {e}")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    run_cli()