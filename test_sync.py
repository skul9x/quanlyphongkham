import sys
import time
from sync_manager import sync_manager
import database

def test_sync():
    print("[TEST] Initializing DB and Sync Manager...")
    database.initialize_database()
    
    print("[TEST] Starting Incremental Sync...")
    def print_progress(msg, pct):
        print(f"[PROGRESS {pct}%] {msg}")
        
    result = sync_manager._incremental_sync(progress_callback=print_progress)
    
    print(f"[TEST] Sync result: {result}")
    
    # Wait for the background queue to process
    print("[TEST] Waiting for sync queue to complete...")
    sync_manager.sync_queue.join()
    time.sleep(2)
    print("[TEST] Sync queue finished.")

if __name__ == "__main__":
    test_sync()
